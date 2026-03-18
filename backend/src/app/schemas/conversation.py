from datetime import datetime

from pydantic import BaseModel, model_validator


class ConversationCreate(BaseModel):
    listing_id: int
    user_one_id: int
    user_two_id: int

    @model_validator(mode="after")
    def user_ids_must_differ(self) -> "ConversationCreate":
        if self.user_one_id == self.user_two_id:
            raise ValueError("user_one_id and user_two_id must be different")
        return self


class Conversation(ConversationCreate):
    id: int
    created_at: datetime
