from sqlalchemy.orm import Session

from app.models.messages import Message as MessageModel
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate
from app.repository.conversation_service import require_conversation_participant
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError


def create_message(db: Session, message: MessageCreate) -> MessageModel:
    if db.get(User, message.sender_id) is None:
        raise ResourceNotFoundError("User not found")
    require_conversation_participant(db, message.conversation_id, message.sender_id)
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
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[MessageModel]:
    require_conversation_participant(db, conversation_id, user_id)
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
