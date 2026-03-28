from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingUpdate
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError


def create_listing(db: Session, host_id: int, listing: ListingCreate) -> Listing:
    if db.get(User, host_id) is None:
        raise ResourceNotFoundError("User not found")
    db_listing = Listing(host_id=host_id, **listing.model_dump())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, listing_id: int) -> Listing | None:
    return db.query(Listing).filter(Listing.id == listing_id).first()


def get_listing_or_raise(db: Session, listing_id: int) -> Listing:
    db_listing = get_listing(db, listing_id)
    if db_listing is None:
        raise ResourceNotFoundError("Listing not found")
    return db_listing


def get_listings(
    db: Session,
    *,
    college_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    room_type: str | None = None,
    start_date=None,
    end_date=None,
    skip: int = 0,
    limit: int = 100,
) -> list[Listing]:
    query = db.query(Listing)
    if college_id is not None:
        query = query.filter(Listing.college_id == college_id)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if room_type is not None:
        query = query.filter(Listing.room_type == room_type)
    if start_date is not None:
        query = query.filter(Listing.start_date >= start_date)
    if end_date is not None:
        query = query.filter(Listing.end_date <= end_date)
    return query.order_by(Listing.created_at.desc()).offset(skip).limit(limit).all()


def update_listing(
    db: Session, listing_id: int, host_id: int, updates: ListingUpdate
) -> Listing:
    db_listing = get_listing(db, listing_id)
    if db_listing is None:
        raise ResourceNotFoundError("Listing not found")
    if db_listing.host_id != host_id:
        raise PermissionDeniedError("Not allowed to modify this listing")
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_listing, field, value)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int, host_id: int) -> None:
    db_listing = get_listing(db, listing_id)
    if db_listing is None:
        raise ResourceNotFoundError("Listing not found")
    if db_listing.host_id != host_id:
        raise PermissionDeniedError("Not allowed to delete this listing")
    db.delete(db_listing)
    db.commit()
