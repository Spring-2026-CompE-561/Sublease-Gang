from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.profiles import Profile
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.repository import profile as ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/me", response_model=ProfileResponse, status_code=201)
async def create_my_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a profile for the currently authenticated user."""
    try:
        return ProfileRepository.create_profile(db, current_user.id, payload)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the currently authenticated user's profile."""
    try:
        return ProfileRepository.get_profile_or_raise(db, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the currently authenticated user's profile."""
    try:
        return ProfileRepository.update_profile(db, current_user.id, payload)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.detail) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/me", status_code=204)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the currently authenticated user's profile."""
    try:
        ProfileRepository.delete_profile(db, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.get("/{username}", response_model=ProfileResponse)
async def get_profile_by_username(
    username: str,
    db: Session = Depends(get_db),
):
    """Get a public profile by username. No auth required."""
    profile = ProfileRepository.get_profile_by_username(db, username)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile