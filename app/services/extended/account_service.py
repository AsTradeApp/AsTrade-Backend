"""
Extended Exchange Account Management Service
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import structlog
import httpx

from app.models.database import User, UserApiCredentials
from app.services.extended.stark_crypto import generate_stark_credentials
from app.config.extended_config import extended_config


logger = structlog.get_logger()


class ExtendedAccountService:
    """Service for managing Extended Exchange accounts"""
    
    def __init__(self):
        self.base_url = extended_config.base_url
        self.onboarding_url = extended_config.onboarding_url
        self.signing_domain = extended_config.signing_domain
        
    async def create_extended_account(
        self,
        user: User,
        wallet_address: str,
        environment: str = "testnet"
    ) -> Dict[str, Any]:
        """
        Create a new Extended Exchange account for AsTrade user
        
        Args:
            user: AsTrade user object
            wallet_address: StarkNet wallet address from Cavos
            environment: "testnet" or "mainnet"
            
        Returns:
            Dictionary with account creation result
        """
        try:
            # Generate Stark credentials
            stark_credentials = generate_stark_credentials()
            private_key = stark_credentials['private_key']
            public_key = stark_credentials['public_key']
            
            logger.info(
                "Generated Stark credentials for user",
                user_id=user.id,
                public_key=public_key[:16] + "...",  # Log only part for security
                environment=environment
            )
            
            # Prepare account creation request
            account_data = {
                "wallet_address": wallet_address,
                "stark_public_key": public_key,
                "environment": environment,
                "referral_code": None  # Could be added for referral system
            }
            
            # For now, we'll simulate account creation since Extended requires
            # specific onboarding flow through their UI or SDK
            # In production, this would call Extended's onboarding API
            
            if environment == "testnet":
                # Simulate successful account creation
                extended_account_id = f"extended_testnet_{user.id[:8]}"
                api_key = f"api_key_testnet_{int(time.time())}"
                api_secret = f"api_secret_testnet_{int(time.time())}"
                
                logger.info(
                    "Simulated Extended account creation for testnet",
                    user_id=user.id,
                    extended_account_id=extended_account_id,
                    environment=environment
                )
            else:
                # For mainnet, we would need real API integration
                extended_account_id = f"extended_mainnet_{user.id[:8]}"
                api_key = f"api_key_mainnet_{int(time.time())}"
                api_secret = f"api_secret_mainnet_{int(time.time())}"
            
            return {
                "success": True,
                "extended_account_id": extended_account_id,
                "api_key": api_key,
                "api_secret": api_secret,
                "stark_private_key": private_key,
                "stark_public_key": public_key,
                "environment": environment,
                "wallet_address": wallet_address
            }
            
        except Exception as e:
            logger.error(
                "Failed to create Extended account",
                user_id=user.id,
                error=str(e),
                environment=environment
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def store_extended_credentials(
        self,
        db: Session,
        user_id: str,
        account_data: Dict[str, Any]
    ) -> UserApiCredentials:
        """
        Store Extended Exchange credentials in database
        
        Args:
            db: Database session
            user_id: AsTrade user ID
            account_data: Account creation result
            
        Returns:
            UserApiCredentials object
        """
        try:
            # Check if credentials already exist
            existing_creds = db.query(UserApiCredentials).filter(
                UserApiCredentials.user_id == user_id
            ).first()
            
            if existing_creds:
                # Update existing credentials
                existing_creds.extended_api_key = account_data['api_key']
                existing_creds.extended_secret_key = account_data['api_secret']
                existing_creds.extended_stark_private_key = account_data['stark_private_key']
                existing_creds.environment = account_data['environment']
                existing_creds.is_mock_enabled = account_data['environment'] == 'testnet'
                
                db.commit()
                db.refresh(existing_creds)
                
                logger.info(
                    "Updated Extended credentials for user",
                    user_id=user_id,
                    environment=account_data['environment']
                )
                
                return existing_creds
            else:
                # Create new credentials
                credentials = UserApiCredentials(
                    user_id=user_id,
                    extended_api_key=account_data['api_key'],
                    extended_secret_key=account_data['api_secret'],
                    extended_stark_private_key=account_data['stark_private_key'],
                    environment=account_data['environment'],
                    is_mock_enabled=account_data['environment'] == 'testnet'
                )
                
                db.add(credentials)
                db.commit()
                db.refresh(credentials)
                
                logger.info(
                    "Stored Extended credentials for user",
                    user_id=user_id,
                    environment=account_data['environment']
                )
                
                return credentials
                
        except Exception as e:
            db.rollback()
            logger.error(
                "Failed to store Extended credentials",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    async def setup_user_for_extended(
        self,
        db: Session,
        user: User,
        wallet_address: str
    ) -> Tuple[bool, str]:
        """
        Complete setup process for Extended Exchange integration
        
        Args:
            db: Database session
            user: AsTrade user
            wallet_address: StarkNet wallet address
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Determine environment based on user level or default to testnet
            environment = "testnet"  # Start with testnet for all users
            
            # Create Extended account
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
                "Successfully set up user for Extended Exchange",
                user_id=user.id,
                environment=environment,
                has_credentials=credentials is not None
            )
            
            return True, "Extended Exchange account created successfully"
            
        except Exception as e:
            logger.error(
                "Failed to setup user for Extended",
                user_id=user.id,
                error=str(e)
            )
            return False, f"Setup failed: {str(e)}"
    
    async def get_user_credentials(
        self,
        db: Session,
        user_id: str
    ) -> Optional[UserApiCredentials]:
        """
        Get Extended Exchange credentials for user
        
        Args:
            db: Database session
            user_id: AsTrade user ID
            
        Returns:
            UserApiCredentials or None
        """
        return db.query(UserApiCredentials).filter(
            UserApiCredentials.user_id == user_id
        ).first()
    
    async def verify_extended_connection(
        self,
        credentials: UserApiCredentials
    ) -> Tuple[bool, str]:
        """
        Verify connection to Extended Exchange with user credentials
        
        Args:
            credentials: User's Extended credentials
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create temporary client with user's credentials
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AsTrade/1.0",
                "X-Api-Key": credentials.extended_api_key
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
                        user_id=credentials.user_id,
                        environment=credentials.environment
                    )
                    return True, "Connection verified successfully"
                else:
                    logger.warning(
                        "Failed to verify Extended connection",
                        user_id=credentials.user_id,
                        status_code=response.status_code,
                        response=response.text[:200]
                    )
                    return False, f"Connection failed: {response.status_code}"
                    
        except Exception as e:
            logger.error(
                "Error verifying Extended connection",
                user_id=credentials.user_id,
                error=str(e)
            )
            return False, f"Verification error: {str(e)}"


# Global service instance
extended_account_service = ExtendedAccountService() 