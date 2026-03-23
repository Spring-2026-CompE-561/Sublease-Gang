from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.listing import Listing

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/listings")
async def get_map_listings(
    north: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    west: float = Query(...),
    college_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    room_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get map pins for listings within the given bounds."""
    if north <= south or east <= west:
        raise HTTPException(status_code=400, detail="invalid bounds")

    query = db.query(Listing).filter(
        Listing.latitude <= north,
        Listing.latitude >= south,
        Listing.longitude <= east,
        Listing.longitude >= west,
    )

    if college_id is not None:
        query = query.filter(Listing.college_id == college_id)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if room_type is not None:
        query = query.filter(Listing.room_type == room_type)
    if start_date is not None:
        query = query.filter(Listing.start_date >= start_date)
    if end_date is not None:
        query = query.filter(Listing.end_date <= end_date)

    listings = query.limit(limit).all()

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
    address: Optional[str] = Query(None),
):
    """Convert a text location into coordinates."""
    if not address:
        raise HTTPException(status_code=400, detail="query required")

    # TODO: hook up a geocoding service (Google Maps, Mapbox, etc.)
    return {"results": []}
