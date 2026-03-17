from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship

import datetime

from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    room_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    sqft = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=True)
    thumbnail_url = Column(String, nullable=False, default=True)
    latitude = Column(Numeric(9,6), nullable=False)
    longitude = Column(Numeric(9,6), nullable=False)

    user = relationship("Profile", back_populates="listings")

