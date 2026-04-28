from datetime import datetime

from pydantic import BaseModel, model_validator


class ListingCreate(BaseModel):
    """Schema for creating a new listing."""

    title: str
    description: str
    price: float
    location: str
    room_type: str | None = None
    sqft: int | None = None
    start_date: datetime
    end_date: datetime
    college_id: int | None = None
    thumbnail_url: str | None = None
    latitude: float
    longitude: float

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
    latitude: float | None = None
    longitude: float | None = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")
        return self


class ListingResponse(ListingCreate):
    """Schema for listing response."""

    host_id: int
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
