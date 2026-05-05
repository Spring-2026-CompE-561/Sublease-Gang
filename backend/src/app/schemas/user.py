from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.schemas.auth import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    account_disabled: bool | None = False
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicUserResponse(BaseModel):
    """User fields safe to expose to other authenticated users."""

    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    username: str | None = None


class UserPasswordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    confirm_new_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("passwords do not match")
        return self
