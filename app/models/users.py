from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    email: Optional[str] = None


class UserApiCredentials(BaseModel):
    """API credentials model"""
    user_id: str
    extended_api_key: Optional[str] = None
    extended_secret_key: Optional[str] = None
    extended_stark_private_key: str
    environment: str = "testnet"
    is_mock_enabled: bool = True
    created_at: datetime
    updated_at: datetime


class User(BaseModel):
    """User model"""
    id: str
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    api_credentials: Optional[UserApiCredentials] = None

    class Config:
        from_attributes = True


class UserCreateResponse(BaseModel):
    """Response model for user creation"""
    user_id: str
    message: str = "User created successfully"


class UserResponse(BaseModel):
    """Standard user response model"""
    user_id: str
    email: Optional[str] = None
    created_at: datetime 