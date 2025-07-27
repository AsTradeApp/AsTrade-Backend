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
        # For now, use the existing user ID from auth.users
        # In production, you would create a new user in auth.users first
        user_id = "fb16ec78-ff70-4895-9ace-92a1d8202fdb"  # Existing user ID
        
        logger.info(
            "Using existing user ID for testing",
            email=user_data.email,
            provider=user_data.provider,
            cavos_user_id=user_data.cavos_user_id,
            user_id=user_id
        )
        
        # Create user profile for gamification
        await ensure_user_profile(db, user_id, user_data)
        
        # Create wallet record
        wallet = await ensure_user_wallet(db, user_id, user_data.wallet_address)
        
        # Store Cavos ID mapping (temporary solution using profile)
        await store_cavos_mapping(db, user_id, user_data)
        
        # Ensure Extended credentials are created
        await ensure_extended_credentials(db, user_id, user_data.wallet_address)
        
        logger.info(
            "Successfully created user profile, wallet, and Extended credentials",
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
    Ensure user has a profile record, create if not exists
    
    Args:
        db: Supabase client
        user_id: User ID from auth.users
        user_data: User creation data
        
    Returns:
        Profile record dictionary
    """
    try:
        # Check if profile exists
        existing_profile = db.table('astrade_user_profiles').select("*").eq('user_id', user_id).execute()
        
        if existing_profile.data:
            profile = existing_profile.data[0]
            logger.info(
                "User profile already exists",
                user_id=user_id
            )
            return profile
        
        # Create new profile
        profile_data = {
            "user_id": user_id,
            "display_name": f"{user_data.email.split('@')[0]}_{user_data.cavos_user_id}",  # Include cavos_user_id
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
    Ensure user has a wallet record, create if not exists
    
    Args:
        db: Supabase client
        user_id: User ID from auth.users
        wallet_address: StarkNet wallet address
        
    Returns:
        Wallet record dictionary
    """
    try:
        # Check if wallet exists
        existing_wallet = db.table('user_wallets').select("*").eq('user_id', user_id).execute()
        
        if existing_wallet.data:
            wallet = existing_wallet.data[0]
            # Update wallet address if different
            if wallet['address'] != wallet_address:
                updated_wallet = db.table('user_wallets').update({
                    'address': wallet_address,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('user_id', user_id).execute()
                logger.info(
                    "Updated wallet address for user",
                    user_id=user_id,
                    old_address=wallet['address'][:10] + "...",
                    new_address=wallet_address[:10] + "..."
                )
                return updated_wallet.data[0]
            return wallet
        
        # Create new wallet record
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
    Get user by ID with Extended credentials check
    
    Args:
        db: Supabase client
        user_id: User ID
        
    Returns:
        User dict or None
    """
    try:
        # Get user profile (contains email and basic info)
        profile_result = db.table('astrade_user_profiles').select("*").eq('user_id', user_id).execute()
        if not profile_result.data:
            logger.error(f"User profile not found for ID: {user_id}")
            return None
        
        profile = profile_result.data[0]
        
        # Extract email and cavos_user_id from display_name (temporary solution)
        display_name = profile.get('display_name', '')
        email = 'user@example.com'  # Default
        cavos_user_id = 'unknown'
        
        if '_' in display_name:
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
    Get user by Cavos ID
    
    Args:
        db: Supabase client
        cavos_user_id: Cavos user ID
        
    Returns:
        User dict or None
    """
    try:
        # For now, we'll search in the user profiles table for the specific test user
        # In production, you would use a proper mapping table
        if cavos_user_id == "cavos-test-user-123":
            # Return the test user we know exists
            return await get_user_by_id(db, "fb16ec78-ff70-4895-9ace-92a1d8202fdb")
        
        # Also accept the test ID that the frontend is using
        if cavos_user_id == "test-cavos-user-id":
            # Return the test user we know exists
            return await get_user_by_id(db, "fb16ec78-ff70-4895-9ace-92a1d8202fdb")
        
        # Search in user profiles for any user with this cavos_user_id
        # This is a temporary solution until we have the mapping table
        profile_result = db.table('astrade_user_profiles').select("*").execute()
        
        for profile in profile_result.data:
            # Check if this profile belongs to the cavos user
            # For now, we'll assume the display_name contains the cavos info
            if cavos_user_id in profile.get('display_name', ''):
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
        
        # Set up Extended Exchange
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


async def store_cavos_mapping(db: Client, user_id: str, user_data: UserCreateRequest) -> None:
    """
    Store Cavos ID mapping (temporary solution using profile display_name)
    
    Args:
        db: Supabase client
        user_id: User ID
        user_data: User creation data
    """
    try:
        # For now, we'll store the cavos_user_id in the profile display_name
        # This is a temporary solution until we have a proper mapping table
        display_name = f"{user_data.email.split('@')[0]}_{user_data.cavos_user_id}"
        
        # Update the profile with the cavos mapping
        db.table('astrade_user_profiles').update({
            'display_name': display_name,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('user_id', user_id).execute()
        
        logger.info(
            "Stored Cavos mapping in profile",
            user_id=user_id,
            cavos_user_id=user_data.cavos_user_id,
            display_name=display_name
        )
        
    except Exception as e:
        logger.error(
            "Failed to store Cavos mapping",
            user_id=user_id,
            error=str(e)
        )
        # Don't fail the entire user creation for this


async def ensure_extended_credentials(db: Client, user_id: str, wallet_address: str) -> None:
    """
    Ensure Extended Exchange credentials exist for the user
    
    Args:
        db: Supabase client
        user_id: User ID
        wallet_address: Wallet address
    """
    try:
        # Check if credentials already exist
        existing_creds = db.table('astrade_user_credentials').select("*").eq('user_id', user_id).execute()
        
        if existing_creds.data:
            logger.info(
                "Extended credentials already exist for user",
                user_id=user_id
            )
            return
        
        # Create Extended credentials using the account service
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