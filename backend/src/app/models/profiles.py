from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    # Share Primary Key with User (One to One)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    icon = Column(String(255), nullable=True, default=None)
    description = Column(String(500), nullable=True, default=None)
    contact_email = Column(String(254), nullable=True, default=None)
    contact_phone = Column(String(20), nullable=True, default=None)

    # Back Reference to User
    user = relationship("User", back_populates="profile")