"""User service layer"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException
import structlog
import uuid
from datetime import datetime

from app.models.database import User, UserApiCredentials
from app.models.users import UserCreateRequest, UserCreateResponse
from app.services.extended.account_service import extended_account_service

logger = structlog.get_logger()


async def create_user(db: Session, user_data: UserCreateRequest) -> UserCreateResponse:
    """
    Create a new user with Extended Exchange integration
    
    Args:
        db: Database session
        user_data: User creation request data
        
    Returns:
        UserCreateResponse with user details
    """
    try:
        # Check if user already exists by email or cavos_user_id
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | 
            (User.cavos_user_id == user_data.cavos_user_id)
        ).first()
        
        if existing_user:
            logger.warning(
                "User already exists",
                email=user_data.email,
                cavos_user_id=user_data.cavos_user_id,
                existing_user_id=existing_user.id
            )
            # Return existing user data
            return UserCreateResponse.create_success(
                user_id=existing_user.id,
                created_at=existing_user.created_at
            )
        
        # Create new AsTrade user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            provider=user_data.provider,
            cavos_user_id=user_data.cavos_user_id,
            wallet_address=user_data.wallet_address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(
            "Created new AsTrade user",
            user_id=user.id,
            email=user.email,
            provider=user.provider,
            wallet_address=user.wallet_address
        )
        
        # Create Extended Exchange account for the user
        try:
            success, message = await extended_account_service.setup_user_for_extended(
                db, user, user_data.wallet_address
            )
            
            if success:
                logger.info(
                    "Successfully created Extended account for user",
                    user_id=user.id,
                    message=message
                )
            else:
                logger.error(
                    "Failed to create Extended account for user",
                    user_id=user.id,
                    error=message
                )
                # Don't fail user creation if Extended setup fails
                # User can still use AsTrade with limited functionality
                
        except Exception as e:
            logger.error(
                "Exception during Extended account setup",
                user_id=user.id,
                error=str(e)
            )
            # Continue with user creation even if Extended setup fails
        
        return UserCreateResponse.create_success(
            user_id=user.id,
            created_at=user.created_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to create user",
            error=str(e),
            email=user_data.email
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


async def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get user by ID with Extended credentials check
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object or None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Load API credentials relationship
        if not user.api_credentials:
            # Try to load credentials separately
            credentials = db.query(UserApiCredentials).filter(
                UserApiCredentials.user_id == user_id
            ).first()
            if credentials:
                user.api_credentials = credentials
    
    return user


async def verify_user_extended_setup(db: Session, user_id: str) -> Tuple[bool, str, Optional[UserApiCredentials]]:
    """
    Verify if user has Extended Exchange setup correctly
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Tuple of (is_setup, status_message, credentials)
    """
    try:
        # Get user credentials
        credentials = await extended_account_service.get_user_credentials(db, user_id)
        
        if not credentials:
            return False, "No Extended credentials found", None
        
        # Verify connection to Extended
        is_connected, message = await extended_account_service.verify_extended_connection(credentials)
        
        if is_connected:
            return True, "Extended Exchange setup verified", credentials
        else:
            return False, f"Extended connection failed: {message}", credentials
            
    except Exception as e:
        logger.error(
            "Error verifying Extended setup",
            user_id=user_id,
            error=str(e)
        )
        return False, f"Verification error: {str(e)}", None


async def setup_extended_for_existing_user(db: Session, user_id: str) -> Tuple[bool, str]:
    """
    Set up Extended Exchange for an existing user who doesn't have it
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Tuple of (success, message)
    """
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            return False, "User not found"
        
        if not user.wallet_address:
            return False, "User has no wallet address"
        
        # Check if already has Extended credentials
        existing_creds = await extended_account_service.get_user_credentials(db, user_id)
        if existing_creds:
            # Verify if existing credentials work
            is_connected, message = await extended_account_service.verify_extended_connection(existing_creds)
            if is_connected:
                return True, "Extended already set up and working"
            else:
                logger.info(
                    "Re-setting up Extended for user with invalid credentials",
                    user_id=user_id,
                    old_environment=existing_creds.environment
                )
        
        # Set up Extended Exchange
        success, message = await extended_account_service.setup_user_for_extended(
            db, user, user.wallet_address
        )
        
        return success, message
        
    except Exception as e:
        logger.error(
            "Failed to setup Extended for existing user",
            user_id=user_id,
            error=str(e)
        )
        return False, f"Setup failed: {str(e)}" 