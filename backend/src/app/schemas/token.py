from datetime import datetime
from typing import Optional, Field

from pydantic import BaseModel

class TokenBase(BaseModel):
    user_id: int 
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expiration_time: Optional[datetime] = None
    scope: Optional[str] = None
    token_type: str = Field(..., alias="tokenType")

class TokenCreate(TokenBase):
    pass

class Token(TokenBase):
    id: int
    time_created: datetime

    class Config:
        from_attributes = True




