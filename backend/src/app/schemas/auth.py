import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Argon2 happily handles long inputs; the cap is just to bound payload size.
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128

_strict = ConfigDict(extra="forbid")


class LoginRequest(BaseModel):
    model_config = _strict

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    model_config = _strict

    refresh_token: str


class LogoutRequest(BaseModel):
    model_config = _strict

    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    model_config = _strict

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    model_config = _strict

    token: str
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class SignupRequest(BaseModel):
    """Combined User + Profile signup payload.

    Validators mirror those on ProfileCreate so client-side and server-side
    rules stay aligned. Contact fields are optional at signup.
    """

    model_config = _strict

    # User fields
    email: EmailStr
    username: str
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    # Profile fields
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    icon: str | None = None
    description: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None

    @field_validator("firstname", "lastname")
    @classmethod
    def validate_names(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Cannot be blank")
        if not re.match(r"^[A-Za-z\s\-']+$", v):
            raise ValueError("Must contain only letters, spaces, or hyphens")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Cannot be blank")
        if not re.match(r"^\w{3,30}$", v):
            raise ValueError(
                "Must be 3-30 characters, letters/numbers/underscores only"
            )
        return v

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = re.sub(r"[\s\-\(\)\+]", "", v)
        if not digits.isdigit() or not (7 <= len(digits) <= 15):
            raise ValueError("Must be a valid phone number (7-15 digits)")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if len(v) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if len(v) > 255:
            raise ValueError("Icon URL cannot exceed 255 characters")
        return v
