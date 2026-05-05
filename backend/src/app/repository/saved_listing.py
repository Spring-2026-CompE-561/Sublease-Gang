from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.models.saved_listing import SavedListing
from app.models.user import User
from app.repository.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


def add(db: Session, user_id: int, listing_id: int) -> SavedListing:
    """Save a listing for a user. Raises ResourceConflictError if already saved."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError("User not found")

    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if listing is None:
        raise ResourceNotFoundError("Listing not found")

    existing = (
        db.query(SavedListing)
        .filter(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        .first()
    )
    if existing is not None:
        raise ResourceConflictError("Listing already saved")

    saved = SavedListing(user_id=user_id, listing_id=listing_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def remove(db: Session, user_id: int, listing_id: int) -> None:
    """Remove a saved listing for a user. Raises ResourceNotFoundError if not saved."""
    saved = (
        db.query(SavedListing)
        .filter(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        .first()
    )
    if saved is None:
        raise ResourceNotFoundError("Listing not saved")

    db.delete(saved)
    db.commit()


def list_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Listing]:
    """Get all listings saved by a user."""
    return (
        db.query(Listing)
        .join(SavedListing, Listing.id == SavedListing.listing_id)
        .filter(SavedListing.user_id == user_id)
        .order_by(SavedListing.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def exists(db: Session, user_id: int, listing_id: int) -> bool:
    """Check if a listing is saved by a user."""
    return (
        db.query(SavedListing)
        .filter(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        .first()
        is not None
    )
