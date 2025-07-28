"""Authentication service"""
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