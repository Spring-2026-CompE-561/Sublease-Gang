from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class MessageSend(BaseModel):
    """Body for POST /conversations/{id}/messages (sender comes from auth)."""

    content: str

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v


class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: str

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v


class MessageUpdate(BaseModel):
    content: Optional[str] = None

    @field_validator("content")
    @classmethod
    def content_cannot_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not v.strip():
            raise ValueError("content cannot be empty")
        return v


class Message(MessageCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
