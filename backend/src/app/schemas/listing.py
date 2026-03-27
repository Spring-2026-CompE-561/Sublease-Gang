from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

class ListingCreate(BaseModel):
    """Schema for creating a new listing."""

    title: str
    description: str
    price: float
    location: str
    room_type: Optional[str] = None
    sqft: Optional[int] = None
    start_date: datetime
    end_date: datetime
    college_id: Optional[int] = None
    thumbnail_url: Optional[str] = None
    latitude: float
    longitude: float


    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ListingUpdate(BaseModel):
    """Schema for updating a listing."""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    room_type: Optional[str] = None
    sqft: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    college_id: Optional[int] = None
    thumbnail_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
