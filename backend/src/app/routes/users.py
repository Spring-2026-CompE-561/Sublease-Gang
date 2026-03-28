from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.repository.user import (
    create_user as repo_create_user,
    delete_user as repo_delete_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_password,
    update_user as repo_update_user,
)
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate

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
        existing = get_user_by_email(db, payload.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already registered")

    return repo_update_user(db, current_user, payload)


@router.delete("/me", status_code=204)
async def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the currently authenticated user's account."""
    repo_delete_user(db, current_user)
    return None


@router.put("/me/password", status_code=204)
async def change_password(payload: UserPasswordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change password for the currently authenticated user."""
    # TODO: use proper password hashing verification once auth is implemented
    if current_user.password_hash != payload.current_password:
        raise HTTPException(status_code=400, detail="Invalid current password")

    update_password(db, current_user, payload.new_password)  # TODO: hash password
    return None


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user's public profile."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already taken")

    return repo_create_user(db, payload)
