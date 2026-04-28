from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class ConversationStartRequest(BaseModel):
    listing_id: int
    other_user_id: int


class ConversationCreate(BaseModel):
    listing_id: int
    user_one_id: int
    user_two_id: int

    @model_validator(mode="after")
    def user_ids_must_differ(self) -> ConversationCreate:
        if self.user_one_id == self.user_two_id:
            raise ValueError("user_one_id and user_two_id must be different")
        return self


class Conversation(ConversationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
