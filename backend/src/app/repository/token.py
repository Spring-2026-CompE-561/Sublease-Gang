from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import Token
from app.models.user import User
from app.repository.exceptions import ResourceNotFoundError
from app.schemas.token import TokenCreate


def create_token(
    db: Session,
    token_data: TokenCreate,
    *,
    access_token: str,
    refresh_token: str | None = None,
    token_type: str = "bearer",
    expiration_time: datetime,
) -> Token:
    if db.get(User, token_data.user_id) is None:
        raise ResourceNotFoundError("User not found")
    db_token = Token(
        user_id=token_data.user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token_type,
        expiration_time=expiration_time,
        scope=token_data.scope,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_token_by_id(db: Session, token_id: int) -> Token | None:
    return db.query(Token).filter(Token.id == token_id).first()


def get_token_by_access(db: Session, access_token: str) -> Token | None:
    return db.query(Token).filter(Token.access_token == access_token).first()


def get_token_by_refresh(db: Session, refresh_token: str) -> Token | None:
    return db.query(Token).filter(Token.refresh_token == refresh_token).first()


def get_tokens_by_user(db: Session, user_id: int) -> list[Token]:
    return db.query(Token).filter(Token.user_id == user_id).all()


def delete_token(db: Session, token_id: int) -> None:
    db_token = get_token_by_id(db, token_id)
    if db_token is None:
        raise ResourceNotFoundError("Token not found")
    db.delete(db_token)
    db.commit()


def delete_tokens_by_user(db: Session, user_id: int) -> None:
    """Revoke all tokens for a user (e.g. on logout-all or account disable)."""
    db.query(Token).filter(Token.user_id == user_id).delete()
    db.commit()
