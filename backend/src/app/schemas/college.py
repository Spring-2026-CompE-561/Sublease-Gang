from pydantic import BaseModel, ConfigDict
from typing import Optional

class CollegeBase(BaseModel):
    name: str
    city: Optional[str] = None

class CollegeCreate(CollegeBase):
    pass

class CollegeRead(CollegeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)