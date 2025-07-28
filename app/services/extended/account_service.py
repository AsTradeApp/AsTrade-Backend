"""
Extended Exchange Account Management Service
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, Tuple
from supabase import Client
import structlog
import httpx

from app.services.extended.stark_crypto import generate_stark_credentials
from app.config.extended_config import extended_config
from app.services.extended.starknet_adapter import (
    StarknetExtendedAdapter,
    StarknetWalletData,
    ExtendedAccountResult,
    create_starknet_adapter
)


logger = structlog.get_logger()


class ExtendedAccountService:
    """Service for managing Extended Exchange accounts"""
    
    def __init__(self):
        self.base_url = extended_config.base_url
        self.onboarding_url = extended_config.onboarding_url
        self.signing_domain = extended_config.signing_domain
        
    async def create_extended_account_with_starknet_wallet(
        self,
        user: User,
        starknet_wallet: Dict[str, Any],
        environment: str = "testnet"
    ) -> Dict[str, Any]:
        """
        Create a new Extended Exchange account using Starknet wallet from Cavos
        
        Args:
            user: AsTrade user object
            starknet_wallet: Starknet wallet data from Cavos invisible wallet
                Expected format: {
                    "private_key": "0x...",
                    "public_key": "0x...", 
                    "address": "0x...",
                    "vault_id": 123456 (optional)
                }
            environment: "testnet" or "mainnet"
            
        Returns:
            Dictionary with account creation result
        """
        try:
            logger.info(
                "Creating Extended account with Starknet wallet",
                user_id=user.id,
                wallet_address=starknet_wallet.get("address"),
                environment=environment
            )
            
            # Validate wallet data
            required_fields = ["private_key", "public_key", "address"]
            for field in required_fields:
                if field not in starknet_wallet:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create wallet data object
            wallet_data = StarknetWalletData(
                private_key=starknet_wallet["private_key"],
                public_key=starknet_wallet["public_key"],
                address=starknet_wallet["address"],
                vault_id=starknet_wallet.get("vault_id")
            )
            
            # Create adapter for the specified environment
            adapter = create_starknet_adapter(environment)
            
            # Perform onboarding
            result = await adapter.onboard_with_starknet_keys(
                wallet_data=wallet_data,
                user_id=user.id,
                referral_code=None  # Could be added for referral system
            )
            
            if result.success:
                logger.info(
                    "Extended account creation successful",
                    user_id=user.id,
                    account_id=result.account_id,
                    environment=environment
                )
                
                return {
                    "success": True,
                    "extended_account_id": result.account_id,
                    "api_key": result.api_key,
                    "api_secret": result.api_secret,
                    "stark_private_key": result.stark_private_key,
                    "stark_public_key": result.stark_public_key,
                    "environment": environment,
                    "wallet_address": wallet_data.address
                }
            else:
                logger.error(
                    "Extended account creation failed",
                    user_id=user.id,
                    error=result.error,
                    environment=environment
                )
                return {
                    "success": False,
                    "error": result.error or "Unknown error during account creation"
                }
            
        except Exception as e:
            logger.error(
                "Failed to create Extended account with Starknet wallet",
                user_id=user.id,
                error=str(e),
                environment=environment
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_extended_account(
        self,
        user: Dict[str, Any],
        wallet_address: str,
        environment: str = "testnet"
    ) -> Dict[str, Any]:
        """
        Legacy method - Create a new Extended Exchange account (deprecated)
        Use create_extended_account_with_starknet_wallet instead
        
        Args:
            user: AsTrade user dictionary
            wallet_address: StarkNet wallet address from Cavos
            environment: "testnet" or "mainnet"
            
        Returns:
            Dictionary with account creation result
        """
        logger.warning(
            "Using deprecated create_extended_account method",
            user_id=user.id,
            environment=environment
        )
        
        # Generate Stark credentials for legacy support
        stark_credentials = generate_stark_credentials()
        
        # Create a mock wallet data structure
        starknet_wallet = {
            "private_key": stark_credentials['private_key'],
            "public_key": stark_credentials['public_key'],
            "address": wallet_address
        }
        
        return await self.create_extended_account_with_starknet_wallet(
            user, starknet_wallet, environment
        )
    
    async def store_extended_credentials(
        self,
        db: Client,
        user_id: str,
        account_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store Extended Exchange credentials in database
        
        Args:
            db: Supabase client
            user_id: AsTrade user ID
            account_data: Account creation result
            
        Returns:
            Credentials dictionary
        """
        try:
            # Check if credentials already exist
            existing_creds = db.table('astrade_user_credentials').select("*").eq('user_id', user_id).execute()
            
            credentials_data = {
                "user_id": user_id,
                "extended_api_key": account_data['api_key'],
                "extended_secret_key": account_data['api_secret'],
                "extended_stark_private_key": account_data['stark_private_key'],
                "environment": account_data['environment'],
                "is_mock_enabled": account_data['environment'] == 'testnet',
                "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if existing_creds.data:
                # Update existing credentials
                result = db.table('astrade_user_credentials').update(credentials_data).eq('user_id', user_id).execute()
                
                logger.info(
                    "Updated Extended credentials for user",
                    user_id=user_id,
                    environment=account_data['environment']
                )
            else:
                # Create new credentials
                credentials_data["created_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
                result = db.table('astrade_user_credentials').insert(credentials_data).execute()
                
                logger.info(
                    "Stored Extended credentials for user",
                    user_id=user_id,
                    environment=account_data['environment']
                )
            
            if not result.data:
                raise Exception("Failed to store credentials in database")
                
            return result.data[0]
                
        except Exception as e:
            logger.error(
                "Failed to store Extended credentials",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    async def setup_user_for_extended_with_starknet(
        self,
        db: Session,
        user: User,
        starknet_wallet: Dict[str, Any],
        environment: str = "testnet"
    ) -> Tuple[bool, str]:
        """
        Complete setup process for Extended Exchange integration using Starknet wallet
        
        Args:
<<<<<<< HEAD
            db: Supabase client
            user: AsTrade user dictionary
            wallet_address: StarkNet wallet address
=======
            db: Database session
            user: AsTrade user
            starknet_wallet: Starknet wallet data from Cavos
            environment: Environment to use ("testnet" or "mainnet")
>>>>>>> 5730961 (Add extended account service)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create Extended account with Starknet wallet
            account_result = await self.create_extended_account_with_starknet_wallet(
                user, starknet_wallet, environment
            )
            
            if not account_result['success']:
                return False, f"Failed to create Extended account: {account_result['error']}"
            
            # Store credentials in database
            credentials = await self.store_extended_credentials(
                db, user['id'], account_result
            )
            
            logger.info(
                "Successfully set up user for Extended Exchange with Starknet wallet",
                user_id=user.id,
                environment=environment,
                has_credentials=credentials is not None
            )
            
            return True, "Extended Exchange account created successfully with Starknet wallet"
            
        except Exception as e:
            logger.error(
                "Failed to setup user for Extended with Starknet wallet",
                user_id=user.id,
                error=str(e)
            )
            return False, f"Setup failed: {str(e)}"
    
    async def setup_user_for_extended(
        self,
        db: Session,
        user: User,
        wallet_address: str
    ) -> Tuple[bool, str]:
        """
        Legacy method - Complete setup process for Extended Exchange integration
        Use setup_user_for_extended_with_starknet instead
        
        Args:
            db: Database session
            user: AsTrade user
            wallet_address: StarkNet wallet address
            
        Returns:
            Tuple of (success, message)
        """
        logger.warning(
            "Using deprecated setup_user_for_extended method",
            user_id=user.id
        )
        
        # Determine environment based on user level or default to testnet
        environment = "testnet"  # Start with testnet for all users
        
        # Create Extended account using legacy method
        account_result = await self.create_extended_account(
            user, wallet_address, environment
        )
        
        if not account_result['success']:
            return False, f"Failed to create Extended account: {account_result['error']}"
        
        # Store credentials in database
        credentials = await self.store_extended_credentials(
            db, user.id, account_result
        )
        
        logger.info(
            "Successfully set up user for Extended Exchange (legacy)",
            user_id=user.id,
            environment=environment,
            has_credentials=credentials is not None
        )
        
        return True, "Extended Exchange account created successfully"
    
    async def get_user_credentials(
        self,
        db: Client,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get Extended Exchange credentials for user
        
        Args:
            db: Supabase client
            user_id: AsTrade user ID
            
        Returns:
            Credentials dictionary or None
        """
        result = db.table('astrade_user_credentials').select("*").eq('user_id', user_id).execute()
        return result.data[0] if result.data else None
    
    async def verify_extended_connection(
        self,
        credentials: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Verify connection to Extended Exchange with user credentials
        
        Args:
            credentials: User's Extended credentials dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create temporary client with user's credentials
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AsTrade/1.0",
                "X-Api-Key": credentials['extended_api_key']
            }
            
            timeout = httpx.Timeout(10.0)
            
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=timeout
            ) as client:
                # Try to get account balance (private endpoint)
                response = await client.get("/account/balance")
                
                if response.status_code == 200:
                    logger.info(
                        "Successfully verified Extended connection",
                        user_id=credentials['user_id'],
                        environment=credentials['environment']
                    )
                    return True, "Connection verified successfully"
                else:
                    logger.warning(
                        "Failed to verify Extended connection",
                        user_id=credentials['user_id'],
                        status_code=response.status_code,
                        response=response.text[:200]
                    )
                    return False, f"Connection failed: {response.status_code}"
                    
        except Exception as e:
            logger.error(
                "Error verifying Extended connection",
                user_id=credentials['user_id'],
                error=str(e)
            )
            return False, f"Verification error: {str(e)}"


# Global service instance
extended_account_service = ExtendedAccountService() 