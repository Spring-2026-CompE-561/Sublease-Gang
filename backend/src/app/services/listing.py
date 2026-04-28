from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.repository.listing import (
    create_listing,
    delete_listing,
    get_listing,
    get_listing_filter_options,
    get_listing_or_raise,
    get_listings_in_bounds,
    search_listings,
    update_listing,
)
from app.schemas.listing import ListingCreate, ListingUpdate


class ListingService:
    """Business logic for listing operations."""

    @staticmethod
    def create(db: Session, host_id: int, payload: ListingCreate) -> Listing:
        return create_listing(db, host_id, payload)

    @staticmethod
    def get_by_id(db: Session, listing_id: int) -> Listing | None:
        return get_listing(db, listing_id)

    @staticmethod
    def get_or_raise(db: Session, listing_id: int) -> Listing:
        return get_listing_or_raise(db, listing_id)

    @staticmethod
    def search(db: Session, **filters) -> tuple[int, list[Listing]]:
        return search_listings(db, **filters)

    @staticmethod
    def get_filter_options(db: Session) -> dict:
        return get_listing_filter_options(db)

    @staticmethod
    def get_in_bounds(db: Session, **kwargs) -> list[Listing]:
        return get_listings_in_bounds(db, **kwargs)

    @staticmethod
    def update(
        db: Session, listing_id: int, host_id: int, updates: ListingUpdate
    ) -> Listing:
        return update_listing(db, listing_id, host_id, updates)

    @staticmethod
    def delete(db: Session, listing_id: int, host_id: int) -> None:
        delete_listing(db, listing_id, host_id)
