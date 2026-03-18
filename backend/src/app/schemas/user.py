from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    password_hash: str
    account_disabled: Optional[bool] = False
    created_at: datetime
