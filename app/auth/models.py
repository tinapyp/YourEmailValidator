from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class UserStatus(str, enum.Enum):
    FREE = "FREE"
    DONATUR = "DONATUR"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    status = Column(String, default=UserStatus.FREE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    api_keys = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    api_usage = relationship(
        "APIUsage", back_populates="user", cascade="all, delete-orphan"
    )
