from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CONTENT_MAX = 5000


class MessageSend(BaseModel):
    """Body for POST /conversations/{id}/messages (sender comes from auth)."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(..., max_length=_CONTENT_MAX)

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v


class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: str = Field(..., max_length=_CONTENT_MAX)

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v


class MessageUpdate(BaseModel):
    content: str | None = Field(default=None, max_length=_CONTENT_MAX)

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.strip():
            raise ValueError("content cannot be empty")
        return v


class Message(MessageCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
