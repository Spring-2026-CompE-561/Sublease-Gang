from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional

from app.core.database import get_db
from app.models.listing import Listing
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

router = APIRouter(prefix="/listings", tags=["listings"])

# TODO: replace with real auth dependency once auth is implemented
def get_current_user(db: Session = Depends(get_db)):
    """Placeholder for auth dependency."""
    raise HTTPException(status_code=401, detail="Authentication not implemented yet")


@router.post("/", response_model=ListingResponse, status_code=201)
async def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
):
    """Create a new room listing."""
    # TODO: get host_id from auth token via get_current_user
    raise HTTPException(status_code=501, detail="Auth required to create listing")

@router.get("/", response_model=dict)
async def search_listings(
    college_id: Optional[int] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    room_type: Optional[str] = None,
    min_sqft: Optional[int] = None,
    max_sqft: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    available_only: Optional[bool] = None,
    sort: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search listings with filters and sorting."""
    query = db.query(Listing)

    if college_id is not None:
        query = query.filter(Listing.college_id == college_id)
    if location is not None:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if room_type is not None:
        query = query.filter(Listing.room_type == room_type)
    if min_sqft is not None:
        query = query.filter(Listing.sqft >= min_sqft)
    if max_sqft is not None:
        query = query.filter(Listing.sqft <= max_sqft)
    if start_date is not None:
        query = query.filter(Listing.start_date >= start_date)
    if end_date is not None:
        query = query.filter(Listing.end_date <= end_date)

    count = query.count()
    listings = query.offset(offset).limit(limit).all()

    results = []
    for l in listings:
        results.append({
            "id": l.id,
            "title": l.title,
            "price": l.price,
            "college": l.college_id,
            "location_text": l.location,
            "room_type": l.room_type,
            "sqft": l.sqft,
            "start_date": str(l.start_date) if l.start_date else None,
            "end_date": str(l.end_date) if l.end_date else None,
            "thumbnail_url": l.thumbnail_url,
            "created_at": str(l.created_at) if l.created_at else None,
        })

    return {"count": count, "limit": limit, "offset": offset, "results": results}

@router.get("/filters")
async def get_filters(db: Session = Depends(get_db)):
    """Get available filter options."""
    room_types = [r[0] for r in db.query(Listing.room_type).distinct().filter(Listing.room_type.isnot(None)).all()]
    colleges = [{"id": c[0], "name": c[0]} for c in db.query(Listing.college_id).distinct().filter(Listing.college_id.isnot(None)).all()]

    price_min = db.query(sql_func.min(Listing.price)).scalar()
    price_max = db.query(sql_func.max(Listing.price)).scalar()
    sqft_min = db.query(sql_func.min(Listing.sqft)).scalar()
    sqft_max = db.query(sql_func.max(Listing.sqft)).scalar()

    return {
        "room_types": room_types,
        "colleges": colleges,
        "price_min": price_min, "price_max": price_max,
        "sqft_min": sqft_min, "sqft_max": sqft_max,
    }

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """View an existing listing."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
):
    """Edit an existing listing."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # TODO: verify current user is the listing owner via auth
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)
    return listing

@router.delete("/{listing_id}", status_code=204, response_model=None)
async def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    """Delete an existing listing."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # TODO: verify current user is the listing owner via auth
    db.delete(listing)
    db.commit()