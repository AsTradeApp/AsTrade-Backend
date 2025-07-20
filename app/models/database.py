from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to user_api_credentials
    api_credentials = relationship("UserApiCredentials", back_populates="user", uselist=False)


class UserApiCredentials(Base):
    """SQLAlchemy model for user_api_credentials table"""
    __tablename__ = "user_api_credentials"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    extended_api_key = Column(String(255), nullable=True)
    extended_secret_key = Column(String(255), nullable=True)
    extended_stark_private_key = Column(Text, nullable=False)
    environment = Column(String(10), default="testnet")
    is_mock_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="api_credentials") 