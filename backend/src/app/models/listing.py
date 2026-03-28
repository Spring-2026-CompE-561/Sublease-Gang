from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

import datetime

from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(String(1000), nullable=False)
    price = Column(Float, nullable=False)
    location = Column(String(255), nullable=False)
    room_type = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    sqft = Column(Integer, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    college_id = Column(Integer, nullable=True)
    thumbnail_url = Column(String, nullable=True, default=None)
    latitude = Column(Numeric(9,6), nullable=False)
    longitude = Column(Numeric(9,6), nullable=False)

    user = relationship("User", back_populates="listings")
    conversations = relationship("Conversation", back_populates="listing")

