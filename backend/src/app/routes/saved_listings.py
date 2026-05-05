from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import ResourceNotFoundError
from app.schemas.listing import ListingResponse
from app.services.saved_listing import SavedListingService

router = APIRouter(prefix="/saved-listings", tags=["saved-listings"])


@router.get("/", response_model=list[ListingResponse])
async def list_saved_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all listings saved by the current user (newest first)."""
    return SavedListingService.list(db, current_user.id)


@router.post("/{listing_id}", response_model=ListingResponse, status_code=201)
async def save_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a listing for the current user. Idempotent."""
    try:
        return SavedListingService.save(db, current_user.id, listing_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.delete("/{listing_id}", status_code=204, response_model=None)
async def unsave_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a saved listing for the current user. Idempotent."""
    SavedListingService.unsave(db, current_user.id, listing_id)
