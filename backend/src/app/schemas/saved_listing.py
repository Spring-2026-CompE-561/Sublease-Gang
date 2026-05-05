from datetime import datetime

from pydantic import BaseModel


class SavedListingResponse(BaseModel):
    """Schema for saved listing response."""

    user_id: int
    listing_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
