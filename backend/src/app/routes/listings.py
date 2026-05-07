from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.schemas.listing import ListingCreate, ListingResponse, ListingUpdate
from app.services.listing import ListingService

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
    college_id: int | None = None,
    # Cap text filters: defends against oversized payloads and DoS via huge
    # LIKE patterns. These flow into ilike() in the repo; wildcard escaping
    # happens there.
    location: str | None = Query(None, max_length=200),
    min_price: float | None = None,
    max_price: float | None = None,
    room_type: str | None = Query(None, max_length=50),
    min_sqft: int | None = None,
    max_sqft: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    available_only: bool | None = None,
    host_id: int | None = None,
    sort: str | None = Query(None, max_length=20),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Search listings with filters and sorting.

    Filtering by ``host_id`` requires authentication so host listings are not
    anonymously scraped; other searches remain public.
    """
    if host_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
        host_id=host_id,
        skip=offset,
        limit=limit,
    )

    results = []
    for l in listings:
        results.append(
            {
                "id": l.id,
                "title": l.title,
                "description": l.description,
                "price": l.price,
                "college": l.college_id,
                "location_text": l.location,
                "location": l.location,
                "room_type": l.room_type,
                "sqft": l.sqft,
                "start_date": str(l.start_date) if l.start_date else None,
                "end_date": str(l.end_date) if l.end_date else None,
                "thumbnail_url": l.thumbnail_url,
                "image_urls": l.image_urls
                if l.image_urls is not None
                else ([l.thumbnail_url] if l.thumbnail_url else []),
                "latitude": float(l.latitude) if l.latitude is not None else None,
                "longitude": float(l.longitude) if l.longitude is not None else None,
                "created_at": str(l.created_at) if l.created_at else None,
            },
        )

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
        return ListingService.update(
            db, listing_id, host_id=current_user.id, updates=payload,
        )
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
