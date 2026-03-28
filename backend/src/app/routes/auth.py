from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.services.user import UserService
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    try:
        user = UserService.register(db, payload)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login and return an access token."""
    try:
        token_data = UserService.authenticate(db, payload.email, payload.password)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return token_data


@router.post("/logout", status_code=204)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard the token)."""
    return None


@router.post("/refresh")
async def refresh():
    """Exchange refresh token for a new access token."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/forgot_password")
async def forgot_password():
    """Send password reset email."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/reset_password")
async def reset_password():
    """Reset password using token from email."""
    raise HTTPException(status_code=501, detail="Not implemented")
