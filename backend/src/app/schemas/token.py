from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    id: int
    user_id: int 
    created_at: datetime
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expiration_time: Optional[datetime] = None
    scope: Optional[str] = None
    token_type: str




