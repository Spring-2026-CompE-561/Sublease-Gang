from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expiration_time = Column(DateTime(timezone=True), nullable=True)
    scope = Column(String, nullable=True)
    token_type = Column(String, nullable=False)
    # JTI of the refresh token this row tracks. Unique when present.
    jti = Column(String, unique=True, index=True, nullable=True)
    # Set when the refresh token is rotated, replayed, or explicitly revoked.
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tokens")
