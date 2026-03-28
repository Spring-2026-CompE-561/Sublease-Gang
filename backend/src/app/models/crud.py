from datetime import datetime

from sqlalchemy.orm import Session

from app.core.auth import hash_password
from app.models.conversations import Conversation
from app.models.messages import Message as MessageModel
from app.models.token import Token
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate
from app.schemas.token import TokenCreate
from app.schemas.user import UserCreate, UserUpdate


class ResourceNotFoundError(Exception):
    """Raised when a referenced or requested resource does not exist."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class PermissionDeniedError(Exception):
    """Raised when the caller is not allowed to perform the requested action."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


# USER CRUD operations
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        email = user.email,
        username = user.username,
        password_hash = hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def update_user(db: Session, user: User, updates: UserUpdate) -> User:
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def update_password(db: Session, user: User, new_password_hash: str) -> User:
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    return user

def disable_user(db: Session, user: User) -> User:
    user.account_disabled = True
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


# TOKEN CRUD operations
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


# MESSAGE CRUD operations
def create_message(db: Session, message: MessageCreate) -> MessageModel:
    if db.get(User, message.sender_id) is None:
        raise ResourceNotFoundError("User not found")
    conversation = db.get(Conversation, message.conversation_id)
    if conversation is None:
        raise ResourceNotFoundError("Conversation not found")
    if message.sender_id not in (conversation.user_one_id, conversation.user_two_id):
        raise PermissionDeniedError("Sender is not a participant in this conversation")
    db_message = MessageModel(
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_message(db: Session, message_id: int) -> MessageModel | None:
    return db.query(MessageModel).filter(MessageModel.id == message_id).first()


def get_message_or_raise(db: Session, message_id: int) -> MessageModel:
    db_message = get_message(db, message_id)
    if db_message is None:
        raise ResourceNotFoundError("Message not found")
    return db_message


def get_messages_by_conversation(
    db: Session,
    conversation_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[MessageModel]:
    if db.get(Conversation, conversation_id) is None:
        raise ResourceNotFoundError("Conversation not found")
    return (
        db.query(MessageModel)
        .filter(MessageModel.conversation_id == conversation_id)
        .order_by(MessageModel.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_message(
    db: Session, message_id: int, user_id: int, payload: MessageUpdate
) -> MessageModel:
    db_message = get_message(db, message_id)
    if db_message is None:
        raise ResourceNotFoundError("Message not found")
    if db_message.sender_id != user_id:
        raise PermissionDeniedError("Not allowed to modify this message")
    if payload.content is not None:
        db_message.content = payload.content
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int, user_id: int) -> None:
    db_message = get_message(db, message_id)
    if db_message is None:
        raise ResourceNotFoundError("Message not found")
    if db_message.sender_id != user_id:
        raise PermissionDeniedError("Not allowed to delete this message")
    db.delete(db_message)
    db.commit()
