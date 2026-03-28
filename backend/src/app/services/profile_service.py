from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.profiles import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.services.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


def create_profile(db: Session, user_id: int, profile_in: ProfileCreate) -> Profile:
    if db.get(User, user_id) is None:
        raise ResourceNotFoundError("User not found")
    if db.get(Profile, user_id) is not None:
        raise ResourceConflictError("Profile already exists for this user")
    db_profile = Profile(user_id=user_id, **profile_in.model_dump())
    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
    except IntegrityError:
        db.rollback()
        raise ResourceConflictError("Username already taken")
    return db_profile


def get_profile(db: Session, user_id: int) -> Profile | None:
    return db.get(Profile, user_id)


def get_profile_or_raise(db: Session, user_id: int) -> Profile:
    db_profile = get_profile(db, user_id)
    if db_profile is None:
        raise ResourceNotFoundError("Profile not found")
    return db_profile


def get_profile_by_username(db: Session, username: str) -> Profile | None:
    return db.query(Profile).filter(Profile.username == username).first()


def update_profile(db: Session, user_id: int, updates: ProfileUpdate) -> Profile:
    db_profile = get_profile(db, user_id)
    if db_profile is None:
        raise ResourceNotFoundError("Profile not found")
    update_data = updates.model_dump(exclude_unset=True)
    new_email = db_profile.contact_email
    new_phone = db_profile.contact_phone
    if "contact_email" in update_data:
        new_email = update_data["contact_email"]
    if "contact_phone" in update_data:
        new_phone = update_data["contact_phone"]
    if new_email is None and new_phone is None:
        raise ValueError("At least one contact method (email or phone) is required")
    try:
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db.commit()
        db.refresh(db_profile)
    except IntegrityError:
        db.rollback()
        raise ResourceConflictError("Username already taken")
    return db_profile


def delete_profile(db: Session, user_id: int) -> None:
    db_profile = get_profile(db, user_id)
    if db_profile is None:
        raise ResourceNotFoundError("Profile not found")
    db.delete(db_profile)
    db.commit()
