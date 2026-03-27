from sqlalchemy.orm import Session
from app.models.user import User
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