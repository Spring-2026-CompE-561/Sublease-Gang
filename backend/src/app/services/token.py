from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import Token
from app.repository.token import (
    create_token,
    get_token_by_id,
    get_token_by_access,
    get_token_by_refresh,
    get_tokens_by_user,
    delete_token,
    delete_tokens_by_user,
)
from app.schemas.token import TokenCreate


class TokenService:
    """Business logic for token operations."""

    @staticmethod
    def create(
        db: Session,
        token_data: TokenCreate,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_type: str = "bearer",
        expiration_time: datetime,
    ) -> Token:
        return create_token(
            db, token_data,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expiration_time=expiration_time,
        )

    @staticmethod
    def get_by_id(db: Session, token_id: int) -> Token | None:
        return get_token_by_id(db, token_id)

    @staticmethod
    def get_by_access(db: Session, access_token: str) -> Token | None:
        return get_token_by_access(db, access_token)

    @staticmethod
    def get_by_refresh(db: Session, refresh_token: str) -> Token | None:
        return get_token_by_refresh(db, refresh_token)

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> list[Token]:
        return get_tokens_by_user(db, user_id)

    @staticmethod
    def delete(db: Session, token_id: int) -> None:
        delete_token(db, token_id)

    @staticmethod
    def revoke_all_for_user(db: Session, user_id: int) -> None:
        delete_tokens_by_user(db, user_id)
