from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.models.saved_listing import SavedListing
from app.repository.exceptions import ResourceNotFoundError


def list_saved_listings(db: Session, user_id: int) -> list[Listing]:
    """Return Listings the user has saved, newest-saved first."""
    return (
        db.query(Listing)
        .join(SavedListing, SavedListing.listing_id == Listing.id)
        .filter(SavedListing.user_id == user_id)
        .order_by(SavedListing.created_at.desc())
        .all()
    )


def is_saved(db: Session, user_id: int, listing_id: int) -> bool:
    return (
        db.query(SavedListing)
        .filter(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        .first()
        is not None
    )


def save_listing(db: Session, user_id: int, listing_id: int) -> SavedListing:
    """Save a listing for the user. Idempotent: returns existing row if already saved."""
    if db.get(Listing, listing_id) is None:
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
        return existing
    saved = SavedListing(user_id=user_id, listing_id=listing_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def unsave_listing(db: Session, user_id: int, listing_id: int) -> None:
    """Remove a saved listing. No-op if not saved."""
    row = (
        db.query(SavedListing)
        .filter(
            SavedListing.user_id == user_id,
            SavedListing.listing_id == listing_id,
        )
        .first()
    )
    if row is None:
        return
    db.delete(row)
    db.commit()
