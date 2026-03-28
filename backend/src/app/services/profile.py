from sqlalchemy.orm import Session

from app.models.profiles import Profile
from app.repository.profile import (
    create_profile,
    get_profile,
    get_profile_or_raise,
    get_profile_by_username,
    update_profile,
    delete_profile,
)
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    """Business logic for profile operations."""

    @staticmethod
    def create(db: Session, user_id: int, profile_in: ProfileCreate) -> Profile:
        return create_profile(db, user_id, profile_in)

    @staticmethod
    def get(db: Session, user_id: int) -> Profile | None:
        return get_profile(db, user_id)

    @staticmethod
    def get_or_raise(db: Session, user_id: int) -> Profile:
        return get_profile_or_raise(db, user_id)

    @staticmethod
    def get_by_username(db: Session, username: str) -> Profile | None:
        return get_profile_by_username(db, username)

    @staticmethod
    def update(db: Session, user_id: int, updates: ProfileUpdate) -> Profile:
        return update_profile(db, user_id, updates)

    @staticmethod
    def delete(db: Session, user_id: int) -> None:
        delete_profile(db, user_id)
