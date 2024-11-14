from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    # Relationship
    user = relationship("User", back_populates="api_keys")
    usage = relationship(
        "APIUsage", back_populates="api_key", cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_key():
        return f"evk_{uuid.uuid4().hex}"


class APIUsage(Base):
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="CASCADE"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    endpoint = Column(String)
    is_success = Column(Boolean)
    response_time = Column(Float)

    # Relationships
    user = relationship("User", back_populates="api_usage")
    api_key = relationship("APIKey", back_populates="usage")
