from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from app.core.database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expiration_time = Column(DateTime, nullable=True)
    scope = Column(String, nullable=True)
    tokenType = Column(String, nullable=False)


    user = relationship("User", back_populates="tokens")