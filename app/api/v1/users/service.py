"""User service layer"""
from typing import Optional, Tuple
from supabase import Client
from fastapi import HTTPException
import structlog
import uuid
from datetime import datetime

from app.models.users import UserCreateRequest, UserCreateResponse
from app.services.extended.account_service import extended_account_service

logger = structlog.get_logger()


async def create_user(db: Client, user_data: UserCreateRequest) -> UserCreateResponse:
    """
    Create a new user with Extended Exchange integration
    
    Args:
        db: Supabase client
        user_data: User creation request data from Cavos
        
    Returns:
        UserCreateResponse with user details
    """
    try:
        # Step 1: Check if user already exists by cavos_user_id
        existing_user = await get_user_by_cavos_id(db, user_data.cavos_user_id)
        if existing_user:
            logger.info(
                "✅ User already exists with this Cavos ID - returning existing user without updates",
                cavos_user_id=user_data.cavos_user_id,
                user_id=existing_user['id']
            )
            return UserCreateResponse.create_success(
                user_id=existing_user['id'],
                created_at=datetime.utcnow()
            )
        
        # Step 1.5: Log that we're creating a completely new user
        logger.info(
            "🆕 No existing user found - creating brand new user",
            cavos_user_id=user_data.cavos_user_id,
            email=user_data.email
        )
        
        # Step 2: Create user in Supabase auth system
        logger.info(
            "Creating new user in Supabase auth system",
            email=user_data.email,
            provider=user_data.provider,
            cavos_user_id=user_data.cavos_user_id
        )
        
        try:
            # Use Supabase admin auth to create user
            logger.info("Attempting to create user via Supabase admin auth...")
            auth_response = db.auth.admin.create_user({
                "email": user_data.email,
                "password": str(uuid.uuid4()),  # Temporary password
                "email_confirm": True,  # Auto-confirm since OAuth verified
                "user_metadata": {
                    "provider": user_data.provider,
                    "cavos_user_id": user_data.cavos_user_id,
                    "wallet_address": user_data.wallet_address,
                    "created_via": "astrade_oauth"
                }
            })
            
            if not auth_response.user:
                raise Exception("Supabase auth user creation returned no user")
            
            user_id = auth_response.user.id
            
            logger.info(
                "✅ Successfully created user in Supabase auth system",
                user_id=user_id,
                email=user_data.email,
                cavos_user_id=user_data.cavos_user_id
            )
            
        except Exception as auth_error:
            # Fallback: generate a unique UUID for this user
            logger.warning(
                "Failed to create user in Supabase auth, generating unique UUID",
                error=str(auth_error),
                error_type=type(auth_error).__name__,
                cavos_user_id=user_data.cavos_user_id
            )
            
            # Generate a unique UUID for this user - each cavos_user_id gets its own UUID
            user_id = str(uuid.uuid4())
            logger.info(f"Generated unique UUID for user: {user_id}")
        
        logger.info(
            "Creating user profile and records",
            user_id=user_id,
            email=user_data.email,
            provider=user_data.provider,
            cavos_user_id=user_data.cavos_user_id
        )
        
        # Step 3: Create user profile for gamification (with cavos_user_id for lookup)
        await ensure_user_profile(db, user_id, user_data)
        
        # Step 4: Create wallet record  
        await ensure_user_wallet(db, user_id, user_data.wallet_address)
        
        # Step 5: Ensure Extended credentials are created
        await ensure_extended_credentials(db, user_id, user_data.wallet_address)
        
        logger.info(
            "Successfully created complete user profile",
            user_id=user_id,
            email=user_data.email,
            cavos_user_id=user_data.cavos_user_id
        )
        
        # Return user data
        return UserCreateResponse.create_success(
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(
            "Failed to create user",
            error=str(e),
            email=user_data.email
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


async def ensure_user_profile(db: Client, user_id: str, user_data: UserCreateRequest) -> dict:
    """
    Create a new user profile record - always create, never update existing
    
    Args:
        db: Supabase client
        user_id: Generated UUID for this user
        user_data: User creation data
        
    Returns:
        Profile record dictionary
    """
    try:
        # Create new profile for this user (we already checked no user exists with this cavos_user_id)
        # Store cavos_user_id in display_name for easy lookup
        email_part = user_data.email.split('@')[0] if user_data.email else "user"
        # Store cavos_user_id in display_name for lookup (format: email_cavosid)
        profile_data = {
            "user_id": user_id,
            "display_name": f"{email_part}_{user_data.cavos_user_id}",  # Store cavos_user_id for lookup
            "level": 1,
            "experience": 0,
            "total_trades": 0,
            "total_pnl": 0,
            "achievements": []
        }
        
        result = db.table('astrade_user_profiles').insert(profile_data).execute()
        
        if not result.data:
            raise Exception("Failed to create user profile")
            
        profile = result.data[0]
        
        logger.info(
            "Created user profile",
            user_id=user_id,
            display_name=profile['display_name']
        )
        
        return profile
        
    except Exception as e:
        logger.error(
            "Failed to ensure user profile",
            user_id=user_id,
            error=str(e)
        )
        raise


async def ensure_user_wallet(db: Client, user_id: str, wallet_address: str) -> dict:
    """
    Create a new wallet record - always create, never update existing
    
    Args:
        db: Supabase client
        user_id: Generated UUID for this user  
        wallet_address: StarkNet wallet address
        
    Returns:
        Wallet record dictionary
    """
    try:
        # Create new wallet record for this user (we already checked no user exists with this cavos_user_id)
        # Each new user gets their own unique wallet record
        wallet_data = {
            "user_id": user_id,
            "address": wallet_address,
            "network": "sepolia",  # Default network
            "transaction_hash": "pending",  # Will be updated when wallet is deployed
        }
        
        result = db.table('user_wallets').insert(wallet_data).execute()
        
        if not result.data:
            raise Exception("Failed to create wallet record")
            
        wallet = result.data[0]
        
        logger.info(
            "Created wallet record for user",
            user_id=user_id,
            wallet_address=wallet_address[:10] + "..."
        )
        
        # Set up Extended Exchange for the user
        try:
            # Get user from auth.users
            user_result = db.table('users').select("*").eq('id', user_id).execute()
            if user_result.data:
                user = user_result.data[0]
                success, message = await extended_account_service.setup_user_for_extended(
                    db, user, wallet_address
                )
                
                if success:
                    logger.info(
                        "Successfully created Extended account for user",
                        user_id=user_id,
                        message=message
                    )
                else:
                    logger.error(
                        "Failed to create Extended account for user",
                        user_id=user_id,
                        error=message
                    )
        except Exception as e:
            logger.error(
                "Exception during Extended account setup",
                user_id=user_id,
                error=str(e)
            )
        
        return wallet
        
    except Exception as e:
        logger.error(
            "Failed to ensure user wallet",
            user_id=user_id,
            error=str(e)
        )
        raise


async def get_user_by_id(db: Client, user_id: str) -> Optional[dict]:
    """
    Get user by ID from auth.users table with Extended credentials check
    
    Args:
        db: Supabase client
        user_id: User ID
        
    Returns:
        User dict or None
    """
    try:
        # Get user profile (which contains basic info)
        profile_result = db.table('astrade_user_profiles').select("*").eq('user_id', user_id).execute()
        if not profile_result.data:
            logger.error(f"User profile not found for ID: {user_id}")
            return None
        
        profile = profile_result.data[0]
        
        # For now, we'll construct user data from the profile
        # Extract email and cavos_user_id from display_name (format: email_part_cavos_id)
        display_name = profile.get('display_name', '')
        email = 'user@example.com'  # Default
        cavos_user_id = 'unknown'
        
        if display_name and isinstance(display_name, str) and '_' in display_name:
            parts = display_name.split('_')
            if len(parts) >= 2:
                email = f"{parts[0]}@example.com"
                cavos_user_id = parts[1]
        
        # Create user object from profile
        user = {
            'id': user_id,
            'email': email,
            'created_at': profile['created_at'],
            'raw_user_meta_data': {
                'provider': 'google',  # Default for now
                'cavos_user_id': cavos_user_id
            }
        }
        logger.info(f"Retrieved user from profile: {user_id}")
        
        # Load wallet information
        wallet_result = db.table('user_wallets').select("*").eq('user_id', user_id).execute()
        if wallet_result.data:
            user['wallet'] = wallet_result.data[0]
        
        # Load API credentials
        creds_result = db.table('astrade_user_credentials').select("*").eq('user_id', user_id).execute()
        if creds_result.data:
            user['api_credentials'] = creds_result.data[0]
        
        # Add profile data
        user['profile'] = profile
        
        return user
        
    except Exception as e:
        logger.error(
            "Error getting user by ID",
            user_id=user_id,
            error=str(e)
        )
        return None


async def get_user_by_cavos_id(db: Client, cavos_user_id: str) -> Optional[dict]:
    """
    Get user by Cavos ID by searching in user profiles display_name
    
    Args:
        db: Supabase client
        cavos_user_id: Cavos user ID
        
    Returns:
        User dict or None
    """
    try:
        logger.info(f"Searching for user with Cavos ID: {cavos_user_id}")
        
        # Search in user profiles for any user with this cavos_user_id in display_name
        profile_result = db.table('astrade_user_profiles').select("*").execute()
        
        if not profile_result.data:
            logger.warning("No user profiles found in database")
            return None
        
        for profile in profile_result.data:
            display_name = profile.get('display_name')
            if display_name and isinstance(display_name, str) and cavos_user_id in display_name:
                logger.info(f"Found user with matching Cavos ID: {profile['user_id']}")
                return await get_user_by_id(db, profile['user_id'])
        
        logger.warning(f"User not found for Cavos ID: {cavos_user_id}")
        return None
        
    except Exception as e:
        logger.error(
            "Error searching user by Cavos ID",
            cavos_user_id=cavos_user_id,
            error=str(e)
        )
        return None


async def verify_user_extended_setup(db: Client, user_id: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Verify if user has Extended Exchange setup correctly
    
    Args:
        db: Supabase client
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


async def setup_extended_for_existing_user(db: Client, user_id: str) -> Tuple[bool, str]:
    """
    Set up Extended Exchange for an existing user who doesn't have it
    
    Args:
        db: Supabase client
        user_id: User ID
        
    Returns:
        Tuple of (success, message)
    """
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            return False, "User not found"
        
        wallet_address = None
        if 'wallet' in user and user['wallet']:
            wallet_address = user['wallet']['address']
        
        if not wallet_address:
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
                    old_environment=existing_creds.get('environment')
                )
        
        # Set up Extended Exchange with user dict
        success, message = await extended_account_service.setup_user_for_extended(
            db, user, wallet_address
        )
        
        return success, message
        
    except Exception as e:
        logger.error(
            "Failed to setup Extended for existing user",
            user_id=user_id,
            error=str(e)
        )
        return False, f"Setup failed: {str(e)}"


async def ensure_extended_credentials(db: Client, user_id: str, wallet_address: str) -> None:
    """
    Create Extended Exchange credentials for the user - always create new
    
    Args:
        db: Supabase client
        user_id: Generated UUID for this user
        wallet_address: Wallet address
    """
    try:
        # Create new credentials for this user (we already checked no user exists with this cavos_user_id)  
        # Each new user gets their own unique credentials
        from app.services.extended.account_service import extended_account_service
        
        # Get user from auth.users (simulated for now)
        user = {
            'id': user_id,
            'email': 'user@example.com'  # We'll get this from profile later
        }
        
        success, message = await extended_account_service.setup_user_for_extended(
            db, user, wallet_address
        )
        
        if success:
            logger.info(
                "Successfully created Extended credentials",
                user_id=user_id,
                message=message
            )
        else:
            logger.error(
                "Failed to create Extended credentials",
                user_id=user_id,
                error=message
            )
            
    except Exception as e:
        logger.error(
            "Exception during Extended credentials creation",
            user_id=user_id,
            error=str(e)
        )
        # Don't fail the entire user creation for this 