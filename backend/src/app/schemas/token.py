from datetime import datetime

from pydantic import BaseModel, ConfigDict


# what is stored in db
class TokenBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    expiration_time: datetime
    scope: str | None = None
    token_type: str


# creating a token
class TokenCreate(BaseModel):
    user_id: int
    scope: str | None = None


# for db reading
class Token(TokenBase):
    id: int
    created_at: datetime


# schema that returns tokens on login/refresh
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    expiration_time: datetime
