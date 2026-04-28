import re

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class ProfileCreate(BaseModel):
    # user_id — comes from JWT, not request body
    firstname: str
    lastname: str
    username: str
    icon: str | None = None
    description: str | None = None
    # Using EmailStr ensures the email is in a valid format
    contact_email: EmailStr | None = None
    contact_phone: str | None = None

    @field_validator("firstname", "lastname")
    @classmethod
    def validate_names(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Cannot be blank")
        # Names should only contain letters, spaces, hyphens
        if not re.match(r"^[A-Za-z\s\-']+$", v):
            raise ValueError("Must contain only letters, spaces, or hyphens")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Cannot be blank")
        # Alphanumeric + underscores only, 3-30 chars (standard username rules)
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
        # Strip formatting characters before storing
        digits = re.sub(r"[\s\-\(\)\+]", "", v)
        if not digits.isdigit() or not (7 <= len(digits) <= 15):
            raise ValueError("Must be a valid phone number (7-15 digits)")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v.strip()) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v.strip()

    @model_validator(mode="after")
    def validate_profile(self) -> ProfileCreate:
        # Spec says contact info is optional, but if a student is listing
        # a sublease, having NO contact method makes the profile useless
        if self.contact_email is None and self.contact_phone is None:
            raise ValueError("At least one contact method (email or phone) is required")
        return self


class ProfileUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    username: str | None = None
    icon: str | None = None
    description: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None

    @field_validator("firstname", "lastname")
    @classmethod
    def validate_names(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Cannot be blank")
        if not re.match(r"^[A-Za-z\s\-']+$", v):
            raise ValueError("Must contain only letters, spaces, or hyphens")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
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
        if len(v.strip()) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v.strip()

    @model_validator(mode="after")
    def validate_contact_method(self) -> ProfileUpdate:
        # If both contact fields are explicitly set to None, reject it
        # Only enforce when at least one contact field was provided in the update
        both_provided = (
            "contact_email" in self.model_fields_set
            or "contact_phone" in self.model_fields_set
        )
        if both_provided and self.contact_email is None and self.contact_phone is None:
            raise ValueError("At least one contact method (email or phone) is required")
        return self


class ProfileResponse(BaseModel):
    user_id: int
    firstname: str
    lastname: str
    username: str
    icon: str | None = None
    description: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None

    model_config = {"from_attributes": True}
