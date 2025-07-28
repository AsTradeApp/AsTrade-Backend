"""User authentication dependencies"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.services.database import get_supabase
from app.models.database import User


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db=Depends(get_supabase)
) -> User:
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
        # Query user from Supabase
        response = db.table("users").select("*").eq("id", x_user_id).single().execute()
        user_data = response.data
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Convert to User model
        user = User()
        for key, value in user_data.items():
            setattr(user, key, value)
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate user: {str(e)}"
        ) 