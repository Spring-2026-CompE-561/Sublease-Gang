from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: str
    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user fields."""

    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    username: str
    account_disabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}
