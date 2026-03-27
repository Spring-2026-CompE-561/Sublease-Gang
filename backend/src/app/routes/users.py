from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PasswordChange

router = APIRouter(prefix="/users", tags=["users"])


# TODO: replace with real auth dependency once auth is implemented
def get_current_user(db: Session = Depends(get_db)):
    """Placeholder for auth dependency. Returns user from token."""
    raise HTTPException(status_code=401, detail="Authentication not implemented yet")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update the currently authenticated user's profile."""
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != current_user.id).first():
            raise HTTPException(status_code=409, detail="Email already registered")
        current_user.email = payload.email

    if payload.name is not None:
        current_user.username = payload.name

    if payload.bio is not None:
        current_user.bio = payload.bio

    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
async def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the currently authenticated user's account."""
    db.delete(current_user)
    db.commit()
    return None


@router.put("/me/password", status_code=204)
async def change_password(payload: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change password for the currently authenticated user."""
    # TODO: use proper password hashing verification once auth is implemented
    if current_user.password_hash != payload.current_password:
        raise HTTPException(status_code=400, detail="Invalid current password")

    current_user.password_hash = payload.new_password  # TODO: hash password
    db.commit()
    return None


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user's public profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=payload.password,  # TODO: hash password when auth is implemented
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
