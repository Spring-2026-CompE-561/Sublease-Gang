from sqlalchemy.orm import Session

from app.models.conversations import Conversation
from app.repository.conversation import (
    create_conversation,
    delete_conversation,
    get_conversation_by_id,
    get_conversation_by_listing_and_users,
    list_conversations_for_user,
    require_conversation_participant,
)
from app.schemas.conversation import ConversationCreate


class ConversationService:
    """Business logic for conversation operations."""

    @staticmethod
    def create(db: Session, data: ConversationCreate) -> Conversation:
        return create_conversation(db, data)

    @staticmethod
    def get_by_id(db: Session, conversation_id: int) -> Conversation | None:
        return get_conversation_by_id(db, conversation_id)

    @staticmethod
    def get_by_listing_and_users(
        db: Session,
        listing_id: int,
        user_a_id: int,
        user_b_id: int,
    ) -> Conversation | None:
        return get_conversation_by_listing_and_users(
            db, listing_id, user_a_id, user_b_id
        )

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> list[Conversation]:
        return list_conversations_for_user(db, user_id)

    @staticmethod
    def get_or_create(
        db: Session,
        listing_id: int,
        user_a_id: int,
        user_b_id: int,
    ) -> Conversation:
        existing = get_conversation_by_listing_and_users(
            db,
            listing_id,
            user_a_id,
            user_b_id,
        )
        if existing:
            return existing
        data = ConversationCreate(
            listing_id=listing_id,
            user_one_id=user_a_id,
            user_two_id=user_b_id,
        )
        return create_conversation(db, data)

    @staticmethod
    def delete(db: Session, conversation: Conversation) -> None:
        delete_conversation(db, conversation)

    @staticmethod
    def require_participant(
        db: Session, conversation_id: int, user_id: int
    ) -> Conversation:
        return require_conversation_participant(db, conversation_id, user_id)
