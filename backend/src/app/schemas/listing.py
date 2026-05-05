from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.college import CollegeRead

class ListingCreate(BaseModel):
    """Schema for creating a new listing."""

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    location: str = Field(..., min_length=1)
    room_type: str = Field(..., min_length=1)
    sqft: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    college_id: int | None = None
    image_urls: list[str] = Field(..., min_length=1, max_length=12)
    latitude: float
    longitude: float

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, v: list[str]) -> list[str]:
        for u in v:
            if not u or not str(u).strip():
                raise ValueError("image_urls entries must be non-empty strings")
            if len(u) > 2_800_000:
                raise ValueError("each image_urls entry is too large")
        return v

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ListingUpdate(BaseModel):
    """Schema for updating a listing."""

    title: str | None = None
    description: str | None = None
    price: float | None = None
    location: str | None = None
    room_type: str | None = None
    sqft: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    college_id: int | None = None
    thumbnail_url: str | None = None
    image_urls: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None

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
