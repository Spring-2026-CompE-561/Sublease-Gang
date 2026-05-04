from datetime import UTC, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import hash_password
from app.models.conversations import Conversation
from app.models.listing import Listing
from app.models.messages import Message
from app.models.profiles import Profile
from app.models.token import Token
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
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
    user.password_changed_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def disable_user(db: Session, user: User) -> User:
    user.account_disabled = True
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    """Hard-delete a user and every row that references them.

    No FK cascades are configured at the schema level, so we explicitly walk
    the dependency graph in FK-safe order. Everything happens in a single
    transaction — if any step fails, the whole delete rolls back.
    """
    listing_ids = [
        listing_id
        for (listing_id,) in db.query(Listing.id)
        .filter(Listing.host_id == user.id)
        .all()
    ]

    # Conversations the user touches: as a participant on either side, OR on a
    # listing they host (covers the case where two other users were chatting
    # about this user's listing).
    convo_clauses = [
        Conversation.user_one_id == user.id,
        Conversation.user_two_id == user.id,
    ]
    if listing_ids:
        convo_clauses.append(Conversation.listing_id.in_(listing_ids))
    conversation_ids = [
        cid
        for (cid,) in db.query(Conversation.id).filter(or_(*convo_clauses)).all()
    ]

    if conversation_ids:
        db.query(Message).filter(
            Message.conversation_id.in_(conversation_ids)
        ).delete(synchronize_session=False)
    # Catch any messages this user sent in conversations we didn't pick up
    # above (defensive — shouldn't exist, but keeps the FK happy).
    db.query(Message).filter(Message.sender_id == user.id).delete(
        synchronize_session=False
    )
    if conversation_ids:
        db.query(Conversation).filter(Conversation.id.in_(conversation_ids)).delete(
            synchronize_session=False
        )
    if listing_ids:
        db.query(Listing).filter(Listing.id.in_(listing_ids)).delete(
            synchronize_session=False
        )
    db.query(Profile).filter(Profile.user_id == user.id).delete(
        synchronize_session=False
    )
    db.query(Token).filter(Token.user_id == user.id).delete(
        synchronize_session=False
    )
    db.delete(user)
    db.commit()
