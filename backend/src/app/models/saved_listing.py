from sqlalchemy import Column, DateTime, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class SavedListing(Base):
    __tablename__ = "saved_listings"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint("user_id", "listing_id"),)
