import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
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
        return ProfileService.create(db, current_user.id, payload)
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
        return ProfileService.get_or_raise(db, current_user.id)
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
        return ProfileService.update(db, current_user.id, payload)
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
        ProfileService.delete(db, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e


@router.get("/{username}", response_model=ProfileResponse)
async def get_profile_by_username(
    username: str,
    db: Session = Depends(get_db),
):
    """Get a public profile by username. No auth required."""
    profile = ProfileService.get_by_username(db, username)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
# Local-disk storage. TODO: swap to object storage (S3/R2) before deploy —
# files written here won't survive container restarts and aren't CDN-fronted.
ICON_DIR = Path("media") / "icons"

ALLOWED_ICON_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_ICON_BYTES = 5 * 1024 * 1024


def _sniff_image_mime(data: bytes) -> str | None:
    """Return the MIME type implied by the first few bytes, or None."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


@router.post("/me/icon", response_model=ProfileResponse)
async def upload_my_icon(
    file: Annotated[UploadFile, File()],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a profile picture for the current user."""
    extension = ALLOWED_ICON_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image type. Use jpg, png, webp, or gif.",
        )
    contents = await file.read()
    if len(contents) > MAX_ICON_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Icon exceeds {MAX_ICON_BYTES // (1024 * 1024)}MB limit.",
        )
    sniffed = _sniff_image_mime(contents)
    if sniffed is None or sniffed != file.content_type:
        raise HTTPException(
            status_code=415,
            detail="File contents do not match the declared image type.",
        )
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{current_user.id}_{uuid.uuid4().hex}{extension}"
    path = ICON_DIR / filename
    path.write_bytes(contents)
    icon_url = f"/media/icons/{filename}"
    try:
        return ProfileService.set_icon(db, current_user.id, icon_url)
    except ResourceNotFoundError as e:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail=e.detail) from e
