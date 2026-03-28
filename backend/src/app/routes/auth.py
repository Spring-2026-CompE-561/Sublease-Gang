import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.settings import settings
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

logger = logging.getLogger(__name__)

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
    """Login and return an access + refresh token pair."""
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a refresh token for a new access + refresh token pair."""
    token_payload = verify_token(payload.refresh_token)
    if token_payload is None or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = token_payload.get("sub")
    user = UserService.get_by_id(db, int(user_id))
    if user is None or user.account_disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account disabled",
        )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/forgot_password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    """Generate a password reset token.

    Always returns 200 regardless of whether the email exists to prevent
    email enumeration. In development mode the reset token is included
    in the response for testing convenience.
    """
    from app.core.auth import create_reset_token

    response: dict = {
        "message": "If that email is registered, a reset link has been sent."
    }
    user = UserService.get_by_email(db, payload.email)
    if user is None:
        return response
    reset_token = create_reset_token(data={"sub": str(user.id)})
    logger.info("Password reset token for user %s: %s", user.id, reset_token)
    if settings.environment == "development":
        response["reset_token"] = reset_token
    return response


@router.put("/reset_password")
async def reset_password(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """Reset password using a token from forgot_password."""
    token_payload = verify_token(payload.token)
    if token_payload is None or token_payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user_id = token_payload.get("sub")
    user = UserService.get_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    UserService.reset_password(db, user, payload.new_password)
    return {"message": "Password has been reset successfully."}
