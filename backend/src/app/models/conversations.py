from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint

from sqlalchemy.orm import relationship

import datetime

from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    __table_args__ = (
        UniqueConstraint("listing_id", "user_one_id", "user_two_id", name="uq_conversation_listing_users"),
        CheckConstraint("user_one_id <> user_two_id", name="ck_conversation_distinct_users"),
    )

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    user_one_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_two_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    listing = relationship("Listing", back_populates="conversations")
    user_one = relationship("User", foreign_keys=[user_one_id])
    user_two = relationship("User", foreign_keys=[user_two_id])
    messages = relationship("Message", back_populates="conversation")