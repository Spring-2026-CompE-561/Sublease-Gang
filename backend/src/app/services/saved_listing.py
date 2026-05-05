from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.models.saved_listing import SavedListing
from app.repository.saved_listing import (
    add,
    exists,
    list_for_user,
    remove,
)


class SavedListingService:
    """Business logic for saved listing operations."""

    @staticmethod
    def save(db: Session, user_id: int, listing_id: int) -> SavedListing:
        return add(db, user_id, listing_id)

    @staticmethod
    def unsave(db: Session, user_id: int, listing_id: int) -> None:
        return remove(db, user_id, listing_id)

    @staticmethod
    def list_for_user(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Listing]:
        return list_for_user(db, user_id, skip, limit)

    @staticmethod
    def is_saved(db: Session, user_id: int, listing_id: int) -> bool:
        return exists(db, user_id, listing_id)
