"""Authentication service"""
from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
import structlog

from app.models.database import User
from app.services.database import get_db

logger = structlog.get_logger()

async def get_current_user(
    x_user_id: str = Header(..., description="User ID from auth token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from X-User-ID header.
    
    Args:
        x_user_id: User ID from request header
        db: Database session
        
    Returns:
        User model if authenticated
        
    Raises:
        HTTPException: If user not found or invalid
    """
    try:
        # Query user from database
        user = db.query(User).filter(User.id == x_user_id).first()
        
        if not user:
            logger.error("User not found", user_id=x_user_id)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
            
        return user
        
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

async def get_current_user_id(
    x_user_id: str = Header(..., description="User ID from auth token")
) -> str:
    """
    Get current authenticated user ID from X-User-ID header.
    
    Args:
        x_user_id: User ID from request header
        
    Returns:
        User ID string if authenticated
        
    Raises:
        HTTPException: If user ID not provided
    """
    try:
        if not x_user_id:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        return x_user_id
        
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

async def get_optional_user_id(
    x_user_id: Optional[str] = Header(None, description="Optional User ID from auth token")
) -> Optional[str]:
    """
    Get optional user ID from X-User-ID header.
    
    Args:
        x_user_id: Optional user ID from request header
        
    Returns:
        User ID string if provided, None otherwise
    """
    return x_user_id if x_user_id else None 