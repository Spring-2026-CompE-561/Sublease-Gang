from datetime import datetime

from pydantic import BaseModel, model_validator

class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: str

    @model_validator(mode="after")
    def content_cannot_be_empty(self) -> "MessageCreate":
        if not self.content or not self.content.strip():
            raise ValueError("content cannot be empty")
        return self

class Message(MessageCreate):
    id: int
    created_at: datetime