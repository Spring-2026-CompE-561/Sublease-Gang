from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    account_disabled: Optional[bool] = False
    created_at: datetime

    model_config = { "from_attributes": True }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    confirm_new_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("passwords do not match")
        return self
