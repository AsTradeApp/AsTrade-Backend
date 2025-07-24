"""User API routes with Extended Exchange integration"""
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
import structlog

from app.models.responses import SuccessResponse, ErrorResponse
from app.models.users import UserCreateRequest, UserCreateResponse
from app.services.database import get_db
from app.api.v1.users.service import (
    create_user,
    get_user_by_id,
    verify_user_extended_setup,
    setup_extended_for_existing_user
)

logger = structlog.get_logger()
router = APIRouter(prefix="/users")


@router.post("/", response_model=UserCreateResponse, summary="Create new user")
async def create_user_route(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new AsTrade user with automatic Extended Exchange setup.
    
    This endpoint:
    1. Creates a new AsTrade user account
    2. Automatically sets up Extended Exchange integration
    3. Generates Stark keys for trading
    4. Stores credentials securely
    
    Args:
        user_data: User creation data from OAuth (Google/Apple)
        
    Returns:
        User creation response with user_id and creation timestamp
    """
    try:
        result = await create_user(db, user_data)
        return result
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=SuccessResponse, summary="Get user information")
async def get_user_route(
    user_id: str = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get user information including Extended Exchange setup status.
    
    Returns:
        - Basic user information
        - Extended Exchange setup status
        - Available features based on setup
    """
    try:
        # Get user
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify Extended setup
        is_setup, status_message, credentials = await verify_user_extended_setup(db, user_id)
        
        user_data = {
            "user_id": user.id,
            "email": user.email,
            "provider": user.provider,
            "wallet_address": user.wallet_address,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "has_api_credentials": credentials is not None,
            "extended_setup": {
                "is_configured": is_setup,
                "status": status_message,
                "environment": credentials.environment if credentials else None,
                "trading_enabled": is_setup and credentials and credentials.environment == "testnet"
            }
        }
        
        return SuccessResponse(data=user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(e)}"
        )


@router.post("/{user_id}/extended/setup", response_model=SuccessResponse, summary="Setup Extended Exchange")
async def setup_extended_route(
    user_id: str = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Set up or re-configure Extended Exchange for an existing user.
    
    This endpoint can be used to:
    1. Set up Extended Exchange for users who don't have it
    2. Re-configure Extended setup if there are issues
    3. Upgrade from testnet to mainnet (future feature)
    
    Returns:
        Setup result with status message
    """
    try:
        success, message = await setup_extended_for_existing_user(db, user_id)
        
        if success:
            return SuccessResponse(
                data={
                    "setup_completed": True,
                    "message": message,
                    "next_steps": [
                        "You can now access Extended Exchange features",
                        "Start with testnet trading to practice",
                        "Check your balance and positions"
                    ]
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Extended setup failed: {message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed Extended setup", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Extended setup failed: {str(e)}"
        )


@router.get("/{user_id}/extended/status", response_model=SuccessResponse, summary="Check Extended status")
async def check_extended_status_route(
    user_id: str = Path(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Check the status of Extended Exchange integration for a user.
    
    Returns detailed information about:
    - Whether Extended Exchange is set up
    - Connection status to Extended API
    - Available features and limitations
    - Environment (testnet/mainnet)
    """
    try:
        is_setup, status_message, credentials = await verify_user_extended_setup(db, user_id)
        
        status_data = {
            "user_id": user_id,
            "extended_configured": is_setup,
            "status_message": status_message,
            "connection_verified": is_setup,
            "environment": credentials.environment if credentials else None,
            "features": {
                "trading": is_setup,
                "balance_check": is_setup,
                "position_management": is_setup,
                "order_history": is_setup,
                "websocket_streams": is_setup
            },
            "limitations": [] if is_setup else [
                "Trading not available",
                "Extended Exchange features disabled",
                "Only basic AsTrade features available"
            ]
        }
        
        if credentials and not is_setup:
            status_data["suggestions"] = [
                "Try re-configuring Extended Exchange",
                "Check your wallet connection",
                "Contact support if issue persists"
            ]
        
        return SuccessResponse(data=status_data)
        
    except Exception as e:
        logger.error("Failed to check Extended status", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check status: {str(e)}"
        ) 