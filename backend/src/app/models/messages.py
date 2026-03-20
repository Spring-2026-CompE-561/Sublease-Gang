from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint

from sqlalchemy import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        CheckConstraint("length(content) > 0", name="ck_content_cannot_be_empty"),
    )

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
