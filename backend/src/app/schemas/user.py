from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
    username: str
    password_hash: str
    account_disabled: Optional[bool] = False
    created_at: datetime
    