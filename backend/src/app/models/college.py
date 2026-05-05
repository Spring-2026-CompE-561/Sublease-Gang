from sqlalchemy import (
    Column,
    String,
    Integer,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    city = Column(String(255), nullable=True)

    listings = relationship("Listing", back_populates="college")
