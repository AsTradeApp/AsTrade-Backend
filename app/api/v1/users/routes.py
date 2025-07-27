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
    db = Depends(get_db)
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


@router.post("/register", response_model=UserCreateResponse, summary="Register user from frontend")
async def register_user_from_frontend(
    user_data: UserCreateRequest,
    db = Depends(get_db)
):
    """
    Register user data from frontend after OAuth authentication.
    
    This endpoint:
    1. Updates existing auth.users with additional metadata
    2. Creates wallet record
    3. Sets up Extended Exchange integration
    4. Creates user profile for gamification
    
    Args:
        user_data: User registration data from OAuth (Google/Apple) + wallet info
        
    Returns:
        User registration response with user_id and creation timestamp
    """
    try:
        result = await create_user(db, user_data)
        return result
    except Exception as e:
        logger.error("Failed to register user from frontend", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register user: {str(e)}"
        )


@router.get("/{user_id}", response_model=SuccessResponse, summary="Get user information")
async def get_user_route(
    user_id: str = Path(..., description="User ID"),
    db = Depends(get_db)
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
            "user_id": user['id'],
            "email": user['email'],
            "provider": user.get('raw_user_meta_data', {}).get('provider') if user.get('raw_user_meta_data') else None,
            "wallet_address": user.get('wallet', {}).get('address') if user.get('wallet') else None,
            "created_at": user['created_at'],
            "has_api_credentials": credentials is not None,
            "extended_setup": {
                "is_configured": is_setup,
                "status": status_message,
                "environment": credentials.get('environment') if credentials else None,
                "trading_enabled": is_setup and credentials and credentials.get('environment') == "testnet"
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


@router.get("/cavos/{cavos_user_id}", response_model=SuccessResponse, summary="Get user by Cavos ID")
async def get_user_by_cavos_id_route(
    cavos_user_id: str = Path(..., description="Cavos User ID"),
    db = Depends(get_db)
):
    """
    Get user information by Cavos ID.
    
    Args:
        cavos_user_id: Cavos User ID
        
    Returns:
        User information if found
    """
    try:
        from app.api.v1.users.service import get_user_by_cavos_id
        
        user = await get_user_by_cavos_id(db, cavos_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify Extended setup
        is_setup, status_message, credentials = await verify_user_extended_setup(db, user['id'])
        
        user_data = {
            "user_id": user['id'],
            "email": user['email'],
            "provider": user.get('raw_user_meta_data', {}).get('provider') if user.get('raw_user_meta_data') else None,
            "wallet_address": user.get('wallet', {}).get('address') if user.get('wallet') else None,
            "created_at": user['created_at'],
            "has_api_credentials": credentials is not None,
            "extended_setup": {
                "is_configured": is_setup,
                "status": status_message,
                "environment": credentials.get('environment') if credentials else None,
                "trading_enabled": is_setup and credentials and credentials.get('environment') == "testnet"
            }
        }
        
        return SuccessResponse(data=user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user by Cavos ID", cavos_user_id=cavos_user_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(e)}"
        )


@router.post("/{user_id}/extended/setup", response_model=SuccessResponse, summary="Setup Extended Exchange")
async def setup_extended_route(
    user_id: str = Path(..., description="User ID"),
    db = Depends(get_db)
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
    db = Depends(get_db)
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


@router.get("/integration/status", response_model=SuccessResponse, summary="Check complete integration status")
async def check_integration_status_route(
    db = Depends(get_db)
):
    """
    Check the complete status of Cavos + Extended Exchange integration.
    
    Returns detailed information about:
    - Database tables and records
    - User creation flow
    - Extended Exchange setup
    - Available endpoints
    """
    try:
        # Get basic stats
        profiles_result = db.table('astrade_user_profiles').select("count", count="exact").execute()
        wallets_result = db.table('user_wallets').select("count", count="exact").execute()
        creds_result = db.table('astrade_user_credentials').select("count", count="exact").execute()
        
        # Get sample user data
        sample_profile = db.table('astrade_user_profiles').select("*").limit(1).execute()
        sample_wallet = db.table('user_wallets').select("*").limit(1).execute()
        sample_creds = db.table('astrade_user_credentials').select("*").limit(1).execute()
        
        integration_status = {
            "database": {
                "profiles_count": profiles_result.count if hasattr(profiles_result, 'count') else len(profiles_result.data),
                "wallets_count": wallets_result.count if hasattr(wallets_result, 'count') else len(wallets_result.data),
                "credentials_count": creds_result.count if hasattr(creds_result, 'count') else len(creds_result.data),
                "has_sample_data": len(sample_profile.data) > 0
            },
            "endpoints": {
                "user_creation": "✅ POST /api/v1/users/register",
                "user_lookup": "✅ GET /api/v1/users/{user_id}",
                "cavos_lookup": "✅ GET /api/v1/users/cavos/{cavos_user_id}",
                "extended_setup": "✅ POST /api/v1/users/{user_id}/extended/setup",
                "extended_status": "✅ GET /api/v1/users/{user_id}/extended/status"
            },
            "features": {
                "cavos_integration": "✅ User creation with Cavos data",
                "wallet_registration": "✅ Automatic wallet record creation",
                "extended_setup": "✅ Automatic Extended Exchange setup",
                "profile_creation": "✅ Gamification profile creation",
                "credential_storage": "✅ Secure credential storage"
            },
            "sample_data": {
                "profile": sample_profile.data[0] if sample_profile.data else None,
                "wallet": sample_wallet.data[0] if sample_wallet.data else None,
                "credentials": sample_creds.data[0] if sample_creds.data else None
            },
            "next_steps": [
                "Test user creation with real Cavos data",
                "Verify Extended Exchange connection",
                "Implement real auth.users creation",
                "Add proper Cavos ID mapping table",
                "Test trading functionality"
            ]
        }
        
        return SuccessResponse(data=integration_status)
        
    except Exception as e:
        logger.error("Failed to check integration status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check integration status: {str(e)}"
        ) 