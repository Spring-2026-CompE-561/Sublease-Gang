from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.token import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201)
async def signup(db: Session = Depends(get_db)):
    """Create a new user account."""
    # TODO: implement signup logic
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/login")
async def login(db: Session = Depends(get_db)):
    """Login and return access + refresh tokens."""
    # TODO: implement login logic
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/refresh")
async def refresh(db: Session = Depends(get_db)):
    """Exchange refresh token for a new access token."""
    # TODO: implement token refresh logic
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/logout")
async def logout(db: Session = Depends(get_db)):
    """Logout and invalidate refresh token."""
    # TODO: implement logout logic
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/forgot_password")
async def forgot_password(db: Session = Depends(get_db)):
    """Send password reset email."""
    # TODO: implement forgot password logic
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/reset_password")
async def reset_password(db: Session = Depends(get_db)):
    """Reset password using token from email."""
    # TODO: implement reset password logic
    raise HTTPException(status_code=501, detail="Not implemented")
