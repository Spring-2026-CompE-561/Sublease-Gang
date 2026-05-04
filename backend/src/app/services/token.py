from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.auth import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    RESET_TOKEN_EXPIRE_MINUTES,
    create_refresh_token,
    create_reset_token,
)
from app.models.token import Token
from app.repository.token import (
    create_token,
    delete_token,
    delete_tokens_by_user,
    get_token_by_access,
    get_token_by_id,
    get_token_by_jti,
    get_token_by_refresh,
    get_tokens_by_user,
    record_token_jti,
    revoke_all_active_for_user_and_type,
    revoke_token,
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
            db,
            token_data,
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

    # ── Refresh-token rotation API ──────────────────────────────────────

    @staticmethod
    def issue_refresh_token(db: Session, user_id: int) -> str:
        """Mint a new refresh JWT and persist its jti for later validation."""
        jti = uuid4().hex
        expiration = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        token = create_refresh_token({"sub": str(user_id)}, jti=jti)
        record_token_jti(db, user_id, jti, "refresh", expiration)
        return token

    @staticmethod
    def get_refresh_record(db: Session, jti: str) -> Token | None:
        row = get_token_by_jti(db, jti)
        if row is not None and row.token_type == "refresh":
            return row
        return None

    @staticmethod
    def revoke_refresh(db: Session, token: Token) -> None:
        revoke_token(db, token)

    @staticmethod
    def revoke_all_refresh_for_user(db: Session, user_id: int) -> None:
        revoke_all_active_for_user_and_type(db, user_id, "refresh")

    # ── Reset-token jti API ─────────────────────────────────────────────

    @staticmethod
    def issue_reset_token(db: Session, user_id: int) -> str:
        """Mint a single-use reset JWT and persist its jti."""
        jti = uuid4().hex
        expiration = datetime.now(UTC) + timedelta(
            minutes=RESET_TOKEN_EXPIRE_MINUTES
        )
        token = create_reset_token({"sub": str(user_id)}, jti=jti)
        record_token_jti(db, user_id, jti, "reset", expiration)
        return token

    @staticmethod
    def get_reset_record(db: Session, jti: str) -> Token | None:
        row = get_token_by_jti(db, jti)
        if row is not None and row.token_type == "reset":
            return row
        return None

    @staticmethod
    def revoke_all_reset_for_user(db: Session, user_id: int) -> None:
        revoke_all_active_for_user_and_type(db, user_id, "reset")
