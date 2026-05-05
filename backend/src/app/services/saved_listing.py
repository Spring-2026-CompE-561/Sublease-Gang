from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.repository.saved_listing import (
    is_saved,
    list_saved_listings,
    save_listing,
    unsave_listing,
)


class SavedListingService:
    """Business logic for user-saved listings."""

    @staticmethod
    def list(db: Session, user_id: int) -> list[Listing]:
        return list_saved_listings(db, user_id)

    @staticmethod
    def is_saved(db: Session, user_id: int, listing_id: int) -> bool:
        return is_saved(db, user_id, listing_id)

    @staticmethod
    def save(db: Session, user_id: int, listing_id: int) -> Listing:
        save_listing(db, user_id, listing_id)
        return db.get(Listing, listing_id)

    @staticmethod
    def unsave(db: Session, user_id: int, listing_id: int) -> None:
        unsave_listing(db, user_id, listing_id)
