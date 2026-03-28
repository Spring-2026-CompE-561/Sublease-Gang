from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import ResourceConflictError
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update the currently authenticated user's profile."""
    try:
        return UserService.update(db, current_user, payload)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e


@router.delete("/me", status_code=204)
async def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the currently authenticated user's account."""
    UserService.delete(db, current_user)
    return None


@router.put("/me/password", status_code=204)
async def change_password(payload: UserPasswordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change password for the currently authenticated user."""
    try:
        UserService.change_password(db, current_user, payload.current_password, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return None


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user's public profile."""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    try:
        return UserService.register(db, payload)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e
