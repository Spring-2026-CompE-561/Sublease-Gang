from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.repository.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_password,
    update_user,
    delete_user,
    disable_user,
)
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Business logic for user operations."""

    @staticmethod
    def register(db: Session, payload: UserCreate) -> User:
        if get_user_by_email(db, payload.email):
            raise ResourceConflictError("Email already registered")
        if get_user_by_username(db, payload.username):
            raise ResourceConflictError("Username already taken")
        return create_user(db, payload)

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> dict:
        """Validate credentials and return token data."""
        user = get_user_by_email(db, email)
        if user is None or not verify_password(password, user.password_hash):
            raise ResourceNotFoundError("Invalid email or password")
        if user.account_disabled:
            raise ResourceNotFoundError("Account is disabled")
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return get_user_by_id(db, user_id)

    @staticmethod
    def update(db: Session, user: User, updates: UserUpdate) -> User:
        if updates.email is not None:
            existing = get_user_by_email(db, updates.email)
            if existing and existing.id != user.id:
                raise ResourceConflictError("Email already registered")
        return update_user(db, user, updates)

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Invalid current password")
        update_password(db, user, hash_password(new_password))

    @staticmethod
    def delete(db: Session, user: User) -> None:
        delete_user(db, user)

    @staticmethod
    def disable(db: Session, user: User) -> User:
        return disable_user(db, user)
