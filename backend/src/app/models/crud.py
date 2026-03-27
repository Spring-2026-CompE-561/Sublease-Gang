from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.conversations import Conversation
from app.models.user import User
from app.schemas.conversation import ConversationCreate
from app.schemas.user import UserCreate, UserUpdate
from app.core.auth import hash_password

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


# CONVERSATION CRUD operations
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
