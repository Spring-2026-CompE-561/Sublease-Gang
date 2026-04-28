from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.listing import ListingService

router = APIRouter(prefix="/map", tags=["map"])


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
    limit: int = 100,
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
    """Convert a text location into coordinates."""
    if not address:
        raise HTTPException(status_code=400, detail="query required")

    # TODO: hook up a geocoding service (Google Maps, Mapbox, etc.)
    return {"results": []}
