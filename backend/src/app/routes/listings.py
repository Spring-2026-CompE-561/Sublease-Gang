from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.services.listing import ListingService
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=ListingResponse, status_code=201)
async def create_listing(
    payload: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new room listing."""
    try:
        return ListingService.create(db, current_user.id, payload)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e

@router.get("/", response_model=dict)
async def list_listings(
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
    count, listings = ListingService.search(
        db,
        college_id=college_id,
        location=location,
        min_price=min_price,
        max_price=max_price,
        room_type=room_type,
        min_sqft=min_sqft,
        max_sqft=max_sqft,
        start_date=start_date,
        end_date=end_date,
        skip=offset,
        limit=limit,
    )

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
    return ListingService.get_filter_options(db)

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """View an existing listing."""
    try:
        return ListingService.get_or_raise(db, listing_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit an existing listing."""
    try:
        return ListingService.update(db, listing_id, host_id=current_user.id, updates=payload)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=e.detail) from e

@router.delete("/{listing_id}", status_code=204, response_model=None)
async def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an existing listing."""
    try:
        ListingService.delete(db, listing_id, host_id=current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=e.detail) from e
