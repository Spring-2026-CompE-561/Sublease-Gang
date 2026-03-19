from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ListingCreate(BaseModel):
    """Schema for creating a new listing."""

    host_id: int
    title: str
    description: str
    price: float
    location: str
    room_type: Optional[str] = None
    sqft: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    college_id: Optional[int] = None
    thumbnail_url: str
    latitude: float
    longitude: float


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


class ListingResponse(ListingCreate):
    """Schema for listing response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
