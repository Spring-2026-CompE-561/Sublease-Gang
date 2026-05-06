from sqlalchemy.orm import Session

from app.models.messages import Message as MessageModel
from app.repository.message import (
    create_message,
    delete_message,
    get_message,
    get_message_or_raise,
    get_messages_by_conversation,
    get_unread_message_count,
    mark_messages_as_read_in_conversation,
    update_message,
)
from app.schemas.message import MessageCreate, MessageUpdate


class MessageService:
    """Business logic for message operations."""

    @staticmethod
    def create(db: Session, message: MessageCreate) -> MessageModel:
        return create_message(db, message)

    @staticmethod
    def get_by_id(db: Session, message_id: int) -> MessageModel | None:
        return get_message(db, message_id)

    @staticmethod
    def get_or_raise(db: Session, message_id: int) -> MessageModel:
        return get_message_or_raise(db, message_id)

    @staticmethod
    def list_by_conversation(
        db: Session,
        conversation_id: int,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MessageModel]:
        return get_messages_by_conversation(
            db, conversation_id, user_id=user_id, skip=skip, limit=limit
        )

    @staticmethod
    def update(
        db: Session, message_id: int, user_id: int, payload: MessageUpdate
    ) -> MessageModel:
        return update_message(db, message_id, user_id, payload)

    @staticmethod
    def delete(db: Session, message_id: int, user_id: int) -> None:
        delete_message(db, message_id, user_id)

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get the count of unread messages for the user."""
        return get_unread_message_count(db, user_id)

    @staticmethod
    def mark_conversation_as_read(
        db: Session, conversation_id: int, user_id: int
    ) -> int:
        """Mark all unread messages in a conversation as read. Returns count updated."""
        return mark_messages_as_read_in_conversation(db, conversation_id, user_id)
