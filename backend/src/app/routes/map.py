import logging
from datetime import datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.listing import ListingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/map", tags=["map"])

# Nominatim's TOS requires a unique, identifying User-Agent and 1 req/s max.
# https://operations.osmfoundation.org/policies/nominatim/
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_USER_AGENT = (
    "Sublease-Gang/1.0 (https://github.com/Spring-2026-CompE-561)"
)
_NOMINATIM_TIMEOUT_SECS = 5
_GEOCODE_MAX_QUERY_LEN = 200
# Tiny in-process LRU. Reduces upstream calls on repeat addresses; cheap to
# blow away on restart. Cap is small because this is a per-worker dict.
_GEOCODE_CACHE_MAX = 256
_geocode_cache: dict[str, list[dict]] = {}


@router.get("/listings")
async def get_map_listings(
    north: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    west: float = Query(...),
    college_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    room_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get map pins for listings within the given bounds."""
    if north <= south:
        raise HTTPException(status_code=400, detail="invalid bounds")
    if not (-90 <= south <= 90 and -90 <= north <= 90):
        raise HTTPException(status_code=400, detail="latitude out of range")
    if not (-180 <= west <= 180 and -180 <= east <= 180):
        raise HTTPException(status_code=400, detail="longitude out of range")

    listings = ListingService.get_in_bounds(
        db,
        north=north,
        south=south,
        east=east,
        west=west,
        college_id=college_id,
        min_price=min_price,
        max_price=max_price,
        room_type=room_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    results = [
        {
            "id": l.id,
            "lat": float(l.latitude),
            "lng": float(l.longitude),
            "price": l.price,
            "title": l.title,
            "start_date": str(l.start_date) if l.start_date else None,
            "end_date": str(l.end_date) if l.end_date else None,
        }
        for l in listings
    ]

    return {"results": results}


@router.get("/geocode")
async def geocode(
    address: str | None = Query(None),
):
    """Convert a text location into coordinates via Nominatim.

    Server-side proxy keeps the user's IP off the upstream request and lets
    us send a TOS-compliant User-Agent that the browser never could.
    """
    if not address:
        raise HTTPException(status_code=400, detail="query required")
    address = address.strip()
    if not address:
        raise HTTPException(status_code=400, detail="query required")
    if len(address) > _GEOCODE_MAX_QUERY_LEN:
        raise HTTPException(status_code=400, detail="query too long")

    cache_key = address.lower()
    cached = _geocode_cache.get(cache_key)
    if cached is not None:
        return {"results": cached}

    try:
        response = requests.get(
            _NOMINATIM_URL,
            params={"format": "jsonv2", "limit": 1, "q": address},
            headers={"User-Agent": _NOMINATIM_USER_AGENT, "Accept": "application/json"},
            timeout=_NOMINATIM_TIMEOUT_SECS,
        )
    except requests.RequestException as e:
        logger.warning("Geocoder upstream error: %s", e)
        raise HTTPException(status_code=502, detail="geocoder upstream error") from e

    if not response.ok:
        logger.warning("Geocoder returned %s", response.status_code)
        raise HTTPException(status_code=502, detail="geocoder upstream error")

    raw = response.json() if response.content else []
    cleaned: list[dict] = []
    for entry in raw if isinstance(raw, list) else []:
        if not isinstance(entry, dict):
            continue
        try:
            lat = float(entry.get("lat"))
            lon = float(entry.get("lon"))
        except (TypeError, ValueError):
            continue
        cleaned.append(
            {
                "lat": lat,
                "lon": lon,
                "display_name": entry.get("display_name") or "",
            }
        )

    if len(_geocode_cache) >= _GEOCODE_CACHE_MAX:
        _geocode_cache.clear()
    _geocode_cache[cache_key] = cleaned
    return {"results": cleaned}
