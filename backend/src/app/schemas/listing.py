import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Accepts: https URLs, /media/ relative paths, or base64-encoded data URIs
# whose MIME is PNG or JPEG. Rejects everything else — javascript:, file:,
# data:image/svg+xml, data:image/gif, data:image/webp, unscoped data: URIs.
_IMAGE_URL_RE = re.compile(
    r"^(?:https?://|/media/|data:image/(?:jpeg|jpg|png);base64,)",
    re.IGNORECASE,
)


def _validate_image_urls(values: list[str]) -> list[str]:
    for u in values:
        s = str(u).strip()
        if not s:
            raise ValueError("image_urls entries must be non-empty strings")
        if len(s) > 2_800_000:
            raise ValueError("each image_urls entry is too large")
        if not _IMAGE_URL_RE.match(s):
            raise ValueError(
                "image_urls must be https URLs, /media/ paths, or "
                "data:image/(jpeg|png);base64 URIs",
            )
    return values

from app.schemas.college import CollegeRead

# Caps on user-provided text. Bounding these defends against oversized
# payload storage, accidental DB bloat, and stored-XSS payload size.
_TITLE_MAX = 200
_DESC_MAX = 5000
_LOCATION_MAX = 200
_ROOM_TYPE_MAX = 50


def _strip_required(v: str) -> str:
    s = v.strip()
    if not s:
        raise ValueError("cannot be blank")
    return s


def _strip_optional(v: str | None) -> str | None:
    if v is None:
        return v
    s = v.strip()
    if not s:
        raise ValueError("cannot be blank")
    return s


class ListingCreate(BaseModel):
    """Schema for creating a new listing."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=_TITLE_MAX)
    description: str = Field(..., min_length=1, max_length=_DESC_MAX)
    price: float = Field(..., gt=0)
    location: str = Field(..., min_length=1, max_length=_LOCATION_MAX)
    room_type: str = Field(..., min_length=1, max_length=_ROOM_TYPE_MAX)
    sqft: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    college_id: int | None = None
    image_urls: list[str] = Field(..., min_length=1, max_length=12)
    latitude: float
    longitude: float

    @field_validator("title", "description", "location", "room_type")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return _strip_required(v)

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, v: list[str]) -> list[str]:
        return _validate_image_urls(v)

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ListingUpdate(BaseModel):
    """Schema for updating a listing."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=_TITLE_MAX)
    description: str | None = Field(default=None, min_length=1, max_length=_DESC_MAX)
    price: float | None = None
    location: str | None = Field(default=None, min_length=1, max_length=_LOCATION_MAX)
    room_type: str | None = Field(default=None, min_length=1, max_length=_ROOM_TYPE_MAX)
    sqft: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    college_id: int | None = None
    thumbnail_url: str | None = None
    image_urls: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("title", "description", "location", "room_type")
    @classmethod
    def strip_text(cls, v: str | None) -> str | None:
        return _strip_optional(v)

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        return _validate_image_urls(v)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")
        return self


class ListingResponse(BaseModel):
    """Schema for listing response (DB rows may predate stricter create rules)."""

    id: int
    host_id: int
    title: str
    description: str
    price: float
    location: str
    room_type: str | None = None
    sqft: int | None = None
    start_date: datetime
    end_date: datetime
    college_id: int | None = None
    college: CollegeRead | None = None
    thumbnail_url: str | None = None
    image_urls: list[str] | None = None
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
