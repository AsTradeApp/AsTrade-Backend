from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


class PaginationInfo(BaseModel):
    """Pagination information for paginated responses"""
    cursor: Optional[int] = None
    count: int
    has_next: bool = False
    has_previous: bool = False


class ErrorDetail(BaseModel):
    """Error detail information"""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None


class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    status: str = Field(description="Response status: 'ok' or 'error'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    

class SuccessResponse(BaseResponse):
    """Success response model"""
    status: str = "ok"
    data: Any
    pagination: Optional[PaginationInfo] = None


class ErrorResponse(BaseResponse):
    """Error response model"""
    status: str = "error"
    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    uptime: float
    services: Dict[str, str]


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str
    channel: str
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow) 