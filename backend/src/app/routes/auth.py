import logging
from datetime import UTC, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DUMMY_PASSWORD_HASH,
    create_access_token,
    verify_password,
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
    LogoutRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.services.token import TokenService
from app.services.user import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account, its profile, and return auth tokens."""
    try:
        user = UserService.register_with_profile(db, payload)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = TokenService.issue_refresh_token(db, user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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
async def logout(
    payload: LogoutRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke the caller's refresh token.

    If a refresh_token is supplied and validates as belonging to the
    caller, that single jti is revoked. If the body is missing or the
    token doesn't match, every active refresh token for the user is
    revoked (defensive default).
    """
    revoked_specific = False
    if payload is not None and payload.refresh_token:
        token_payload = verify_token(payload.refresh_token)
        if (
            token_payload is not None
            and token_payload.get("type") == "refresh"
            and str(token_payload.get("sub")) == str(current_user.id)
        ):
            jti = token_payload.get("jti")
            if jti is not None:
                record = TokenService.get_refresh_record(db, jti)
                if record is not None and record.revoked_at is None:
                    TokenService.revoke_refresh(db, record)
                    revoked_specific = True
    if not revoked_specific:
        TokenService.revoke_all_refresh_for_user(db, current_user.id)
    return


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
    iat = token_payload.get("iat")
    pca = user.password_changed_at
    if pca.tzinfo is None:
        pca = pca.replace(tzinfo=UTC)
    if iat is None or iat < int(pca.timestamp()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Rotation + reuse detection. Every refresh token has a server-tracked jti.
    # If the row is missing, the token is a forgery / from before tracking
    # started. If the row is already revoked, the same token has been
    # presented twice — assume compromise and burn every active refresh
    # token for this user.
    jti = token_payload.get("jti")
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    record = TokenService.get_refresh_record(db, jti)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if record.revoked_at is not None:
        TokenService.revoke_all_refresh_for_user(db, user.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    TokenService.revoke_refresh(db, record)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh = TokenService.issue_refresh_token(db, user.id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/forgot_password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Generate a password reset token.

    Always returns 200 regardless of whether the email exists to prevent
    email enumeration. In development mode the reset token is included
    in the response for testing convenience.
    """
    response: dict = {
        "message": "If that email is registered, a reset link has been sent.",
    }
    user = UserService.get_by_email(db, payload.email)
    if user is None:
        # Pay the Argon2 verification cost so timing doesn't reveal whether
        # the email is registered. The dummy hash never matches anything.
        verify_password(payload.email, DUMMY_PASSWORD_HASH)
        return response
    reset_token = TokenService.issue_reset_token(db, user.id)
    if settings.environment == "development":
        logger.info("Password reset token for user %s: %s", user.id, reset_token)
        response["reset_token"] = reset_token
    else:
        logger.info("Password reset requested for user %s", user.id)
    return response


@router.put("/reset_password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password using a token from forgot_password.

    Reset tokens are single-use. The jti is looked up server-side; if it
    has already been consumed (or was never issued by us) the request is
    rejected. After a successful reset every active reset and refresh
    token for the user is revoked.
    """
    token_payload = verify_token(payload.token)
    if token_payload is None or token_payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    jti = token_payload.get("jti")
    if jti is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    record = TokenService.get_reset_record(db, jti)
    if record is None or record.revoked_at is not None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user_id = token_payload.get("sub")
    user = UserService.get_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    UserService.reset_password(db, user, payload.new_password)
    # Burn the consumed jti and any peers; also revoke the user's refresh
    # tokens so a stolen pair can't outlive a reset.
    TokenService.revoke_all_reset_for_user(db, user.id)
    TokenService.revoke_all_refresh_for_user(db, user.id)
    return {"message": "Password has been reset successfully."}
