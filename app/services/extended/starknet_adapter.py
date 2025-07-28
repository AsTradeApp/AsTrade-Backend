"""
Starknet Adapter for Extended Exchange Onboarding
Handles onboarding with Cavos invisible wallet Starknet keys
"""
import asyncio
import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import aiohttp
import structlog
from dataclasses import dataclass

from app.services.extended.sdk_config import ExtendedEndpointConfig


logger = structlog.get_logger()


@dataclass
class StarknetWalletData:
    """Starknet wallet data from Cavos invisible wallet"""
    private_key: str  # Hex string
    public_key: str   # Hex string
    address: str      # Starknet address
    vault_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate wallet data after initialization"""
        self._validate_keys()
        self._validate_address()
    
    def _validate_keys(self):
        """Validate private and public key formats"""
        # Remove '0x' prefix if present for validation
        private_clean = self.private_key.replace('0x', '')
        public_clean = self.public_key.replace('0x', '')
        
        # Check if they are valid hex strings
        if not re.match(r'^[0-9a-fA-F]+$', private_clean):
            raise ValueError("Invalid private key format: must be hexadecimal")
        
        if not re.match(r'^[0-9a-fA-F]+$', public_clean):
            raise ValueError("Invalid public key format: must be hexadecimal")
        
        # Check key lengths (Starknet keys are typically 64 hex characters)
        if len(private_clean) not in [64, 66]:  # Allow for potential variations
            logger.warning(
                "Unusual private key length",
                length=len(private_clean),
                expected="64 characters"
            )
        
        if len(public_clean) not in [64, 66]:
            logger.warning(
                "Unusual public key length", 
                length=len(public_clean),
                expected="64 characters"
            )
    
    def _validate_address(self):
        """Validate Starknet address format"""
        address_clean = self.address.replace('0x', '')
        
        if not re.match(r'^[0-9a-fA-F]+$', address_clean):
            raise ValueError("Invalid address format: must be hexadecimal")
        
        # Starknet addresses can vary in length but should be reasonable
        if len(address_clean) < 40 or len(address_clean) > 66:
            logger.warning(
                "Unusual address length",
                length=len(address_clean),
                address=self.address[:10] + "..."
            )


@dataclass
class ExtendedAccountResult:
    """Result of Extended account creation"""
    account_id: str
    api_key: str
    api_secret: str
    stark_private_key: str
    stark_public_key: str
    environment: str
    success: bool
    error: Optional[str] = None


class StarknetExtendedAdapter:
    """
    Adapter for Extended Exchange onboarding using Starknet keys directly
    """
    
    def __init__(self, config: ExtendedEndpointConfig):
        self.config = config
        self.timeout = aiohttp.Timeout(30.0)
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration parameters"""
        required_fields = ['base_url', 'onboarding_url', 'signing_domain']
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Configuration missing required field: {field}")
        
        # Validate URLs
        if not (self.config.base_url.startswith('http://') or 
                self.config.base_url.startswith('https://')):
            raise ValueError("Invalid base_url: must start with http:// or https://")
        
        if not (self.config.onboarding_url.startswith('http://') or 
                self.config.onboarding_url.startswith('https://')):
            raise ValueError("Invalid onboarding_url: must start with http:// or https://")
        
    async def onboard_with_starknet_keys(
        self,
        wallet_data: StarknetWalletData,
        user_id: str,
        referral_code: Optional[str] = None
    ) -> ExtendedAccountResult:
        """
        Onboard user with Starknet keys from Cavos wallet
        
        Args:
            wallet_data: Starknet wallet information from Cavos
            user_id: AsTrade user ID
            referral_code: Optional referral code
            
        Returns:
            ExtendedAccountResult with onboarding status and credentials
        """
        try:
            # Validate inputs
            if not user_id or len(user_id.strip()) == 0:
                raise ValueError("User ID cannot be empty")
            
            if len(user_id) < 8:
                raise ValueError("User ID must be at least 8 characters long")
            
            logger.info(
                "Starting Extended onboarding with Starknet keys",
                user_id=user_id,
                wallet_address=wallet_data.address,
                environment=self.config.signing_domain,
                has_vault_id=wallet_data.vault_id is not None
            )
            
            # For now, we'll simulate the onboarding process since the real API
            # requires complex L1/L2 signature coordination
            # In production, you would need to implement the actual API calls
            
            if "testnet" in self.config.signing_domain:
                # Testnet simulation
                result = await self._simulate_testnet_onboarding(wallet_data, user_id)
            else:
                # Mainnet would require real implementation
                result = await self._simulate_mainnet_onboarding(wallet_data, user_id)
                
            logger.info(
                "Extended onboarding completed",
                user_id=user_id,
                success=result.success,
                account_id=result.account_id if result.success else None,
                environment=result.environment
            )
            
            return result
            
        except ValueError as e:
            logger.error(
                "Validation error during Extended onboarding",
                user_id=user_id,
                error=str(e)
            )
            return ExtendedAccountResult(
                account_id="",
                api_key="",
                api_secret="",
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment=self.config.signing_domain,
                success=False,
                error=f"Validation error: {str(e)}"
            )
        except Exception as e:
            logger.error(
                "Failed Extended onboarding with Starknet keys",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return ExtendedAccountResult(
                account_id="",
                api_key="",
                api_secret="",
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment=self.config.signing_domain,
                success=False,
                error=f"Onboarding error: {str(e)}"
            )
    
    async def _simulate_testnet_onboarding(
        self,
        wallet_data: StarknetWalletData,
        user_id: str
    ) -> ExtendedAccountResult:
        """Simulate testnet onboarding for development"""
        
        try:
            # Simulate API delay
            await asyncio.sleep(1)
            
            # Generate mock credentials based on wallet data
            timestamp = int(time.time())
            account_id = f"extended_testnet_{user_id[:8]}_{timestamp}"
            
            # Create deterministic but unique API keys based on wallet data
            key_base = f"{wallet_data.public_key[-8:]}_{timestamp}"
            api_key = f"testnet_key_{key_base}"
            api_secret = f"testnet_secret_{hash(wallet_data.private_key) % 100000}_{timestamp}"
            
            logger.info(
                "Simulated testnet onboarding successful",
                user_id=user_id,
                account_id=account_id
            )
            
            return ExtendedAccountResult(
                account_id=account_id,
                api_key=api_key,
                api_secret=api_secret,
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment="testnet",
                success=True
            )
            
        except Exception as e:
            logger.error(
                "Error in testnet simulation",
                user_id=user_id,
                error=str(e)
            )
            return ExtendedAccountResult(
                account_id="",
                api_key="",
                api_secret="",
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment="testnet",
                success=False,
                error=f"Testnet simulation failed: {str(e)}"
            )
    
    async def _simulate_mainnet_onboarding(
        self,
        wallet_data: StarknetWalletData,
        user_id: str
    ) -> ExtendedAccountResult:
        """Simulate mainnet onboarding (would be real implementation)"""
        
        try:
            # For mainnet, you would implement the actual Extended API calls
            # This is a placeholder for the real implementation
            
            await asyncio.sleep(2)  # Simulate longer mainnet processing
            
            timestamp = int(time.time())
            account_id = f"extended_mainnet_{user_id[:8]}_{timestamp}"
            
            # Create deterministic but unique API keys
            key_base = f"{wallet_data.public_key[-8:]}_{timestamp}"
            api_key = f"mainnet_key_{key_base}"
            api_secret = f"mainnet_secret_{hash(wallet_data.private_key) % 100000}_{timestamp}"
            
            logger.info(
                "Simulated mainnet onboarding successful",
                user_id=user_id,
                account_id=account_id
            )
            
            return ExtendedAccountResult(
                account_id=account_id,
                api_key=api_key,
                api_secret=api_secret,
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment="mainnet",
                success=True
            )
            
        except Exception as e:
            logger.error(
                "Error in mainnet simulation",
                user_id=user_id,
                error=str(e)
            )
            return ExtendedAccountResult(
                account_id="",
                api_key="",
                api_secret="",
                stark_private_key=wallet_data.private_key,
                stark_public_key=wallet_data.public_key,
                environment="mainnet",
                success=False,
                error=f"Mainnet simulation failed: {str(e)}"
            )
    
    async def verify_account(
        self,
        account_id: str,
        api_key: str
    ) -> Tuple[bool, str]:
        """
        Verify Extended account is properly set up
        
        Args:
            account_id: Extended account ID
            api_key: API key for the account
            
        Returns:
            Tuple of (success, message)
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Api-Key": api_key,
                "User-Agent": "AsTrade/1.0"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Try to get account info (mock endpoint for now)
                url = f"{self.config.base_url}/account/info"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return True, "Account verification successful"
                    else:
                        return False, f"Verification failed: {response.status}"
                        
        except Exception as e:
            logger.error(
                "Error verifying Extended account",
                account_id=account_id,
                error=str(e)
            )
            return False, f"Verification error: {str(e)}"


# Factory function for creating adapters
def create_starknet_adapter(environment: str = "testnet") -> StarknetExtendedAdapter:
    """
    Create a StarknetExtendedAdapter for the specified environment
    
    Args:
        environment: "testnet" or "mainnet"
        
    Returns:
        StarknetExtendedAdapter instance
    """
    config = ExtendedEndpointConfig.from_environment(environment)
    return StarknetExtendedAdapter(config) 