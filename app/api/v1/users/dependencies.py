"""User authentication dependencies"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.services.database import get_supabase
from app.models.users import User
from pydantic import BaseModel
from datetime import datetime


class SimpleUser(BaseModel):
    id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db=Depends(get_supabase)
) -> SimpleUser:
    """
    Get the current authenticated user from the X-User-ID header.
    This is a simplified auth mechanism - in production you'd want to use proper JWT tokens.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="X-User-ID header is required"
        )
    
    try:
        # Validar que el user_id tiene formato UUID válido
        import uuid
        try:
            uuid.UUID(x_user_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID format"
            )
        
        # Convert to SimpleUser model (asumimos que el usuario existe)
        user = SimpleUser(id=x_user_id)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate user: {str(e)}"
        ) 