from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.services.saved_listing import SavedListingService

router = APIRouter(prefix="/saved-listings", tags=["saved-listings"])


@router.post("/{listing_id}", status_code=201, response_model=dict)
async def save_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a listing for the current user."""
    try:
        SavedListingService.save(db, current_user.id, listing_id)
        return {"listing_id": listing_id, "saved": True}
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e


@router.delete("/{listing_id}", status_code=204, response_model=None)
async def unsave_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a saved listing for the current user."""
    try:
        SavedListingService.unsave(db, current_user.id, listing_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.get("/", response_model=dict)
async def get_saved_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all saved listings for the current user."""
    listings = SavedListingService.list_for_user(db, current_user.id)

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
            }
        )

    return {"count": len(results), "results": results}
