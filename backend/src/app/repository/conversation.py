from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.conversations import Conversation
from app.schemas.conversation import ConversationCreate
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError


def _canonical_user_pair(user_a_id: int, user_b_id: int) -> tuple[int, int]:
    return tuple(sorted((user_a_id, user_b_id)))


def create_conversation(db: Session, data: ConversationCreate) -> Conversation:
    user_one_id, user_two_id = _canonical_user_pair(data.user_one_id, data.user_two_id)
    db_conversation = Conversation(
        listing_id=data.listing_id,
        user_one_id=user_one_id,
        user_two_id=user_two_id,
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_conversation_by_id(db: Session, conversation_id: int) -> Conversation | None:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversation_by_listing_and_users(
    db: Session, listing_id: int, user_a_id: int, user_b_id: int
) -> Conversation | None:
    user_one_id, user_two_id = _canonical_user_pair(user_a_id, user_b_id)
    return (
        db.query(Conversation)
        .filter(
            Conversation.listing_id == listing_id,
            Conversation.user_one_id == user_one_id,
            Conversation.user_two_id == user_two_id,
        )
        .first()
    )


def list_conversations_for_user(db: Session, user_id: int) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.user_one_id == user_id,
                Conversation.user_two_id == user_id,
            )
        )
        .all()
    )


def delete_conversation(db: Session, conversation: Conversation) -> None:
    db.delete(conversation)
    db.commit()


def require_conversation_participant(
    db: Session, conversation_id: int, user_id: int
) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ResourceNotFoundError("Conversation not found")
    if user_id not in (conversation.user_one_id, conversation.user_two_id):
        raise PermissionDeniedError("Not a participant in this conversation")
    return conversation
