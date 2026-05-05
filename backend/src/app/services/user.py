from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.services.token import TokenService
from app.models.profiles import Profile
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.repository.profile import get_profile_by_username
from app.repository.user import (
    create_user,
    delete_user,
    disable_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_password,
    update_user,
)
from app.schemas.auth import SignupRequest
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
    def register_with_profile(db: Session, payload: SignupRequest) -> User:
        """Create a User and its associated Profile in a single transaction."""
        if get_user_by_email(db, payload.email):
            raise ResourceConflictError("Email already registered")
        if get_user_by_username(db, payload.username):
            raise ResourceConflictError("Username already taken")
        if get_profile_by_username(db, payload.username):
            raise ResourceConflictError("Username already taken")

        db_user = User(
            email=payload.email,
            username=payload.username,
            password_hash=hash_password(payload.password),
        )
        db.add(db_user)
        try:
            db.flush()
            db_profile = Profile(
                user_id=db_user.id,
                firstname=payload.firstname,
                lastname=payload.lastname,
                username=payload.username,
                icon=payload.icon,
                description=payload.description,
                contact_email=payload.contact_email,
                contact_phone=payload.contact_phone,
            )
            db.add(db_profile)
            db.commit()
            db.refresh(db_user)
        except IntegrityError as e:
            db.rollback()
            raise ResourceConflictError("Email or username already in use") from e
        return db_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> dict:
        """Validate credentials and return token data."""
        user = get_user_by_email(db, email)
        if user is None:
            # Constant-time defense: pay Argon2's verification cost even
            # when the email is unknown so login latency doesn't telegraph
            # whether the email is registered.
            verify_password(password, DUMMY_PASSWORD_HASH)
            raise ResourceNotFoundError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise ResourceNotFoundError("Invalid email or password")
        if user.account_disabled:
            raise ResourceNotFoundError("Account is disabled")
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = TokenService.issue_refresh_token(db, user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
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
    def change_password(
        db: Session, user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Invalid current password")
        update_password(db, user, hash_password(new_password))

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return get_user_by_email(db, email)

    @staticmethod
    def reset_password(db: Session, user: User, new_password: str) -> None:
        update_password(db, user, hash_password(new_password))

    @staticmethod
    def delete(db: Session, user: User) -> None:
        delete_user(db, user)

    @staticmethod
    def disable(db: Session, user: User) -> User:
        return disable_user(db, user)
