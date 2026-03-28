from sqlalchemy import func as sql_func
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


def search_listings(
    db: Session,
    *,
    college_id: int | None = None,
    location: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    room_type: str | None = None,
    min_sqft: int | None = None,
    max_sqft: int | None = None,
    start_date=None,
    end_date=None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, list[Listing]]:
    """Search listings with filters. Returns (total_count, results)."""
    query = db.query(Listing)
    if college_id is not None:
        query = query.filter(Listing.college_id == college_id)
    if location is not None:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if room_type is not None:
        query = query.filter(Listing.room_type == room_type)
    if min_sqft is not None:
        query = query.filter(Listing.sqft >= min_sqft)
    if max_sqft is not None:
        query = query.filter(Listing.sqft <= max_sqft)
    if start_date is not None:
        query = query.filter(Listing.start_date >= start_date)
    if end_date is not None:
        query = query.filter(Listing.end_date <= end_date)
    count = query.count()
    results = query.offset(skip).limit(limit).all()
    return count, results


def get_listing_filter_options(db: Session) -> dict:
    """Return available filter options for listings."""
    room_types = [
        r[0] for r in db.query(Listing.room_type).distinct().filter(Listing.room_type.isnot(None)).all()
    ]
    colleges = [
        {"id": c[0], "name": c[0]}
        for c in db.query(Listing.college_id).distinct().filter(Listing.college_id.isnot(None)).all()
    ]
    return {
        "room_types": room_types,
        "colleges": colleges,
        "price_min": db.query(sql_func.min(Listing.price)).scalar(),
        "price_max": db.query(sql_func.max(Listing.price)).scalar(),
        "sqft_min": db.query(sql_func.min(Listing.sqft)).scalar(),
        "sqft_max": db.query(sql_func.max(Listing.sqft)).scalar(),
    }


def get_listings_in_bounds(
    db: Session,
    *,
    north: float,
    south: float,
    east: float,
    west: float,
    college_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    room_type: str | None = None,
    start_date=None,
    end_date=None,
    limit: int = 100,
) -> list[Listing]:
    """Return listings within geographic bounds."""
    query = db.query(Listing).filter(
        Listing.latitude <= north,
        Listing.latitude >= south,
        Listing.longitude <= east,
        Listing.longitude >= west,
    )
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
    return query.limit(limit).all()


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
