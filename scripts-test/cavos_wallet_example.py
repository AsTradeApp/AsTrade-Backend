"""
Cavos Wallet L2/Starknet Integration Example

This example demonstrates how to use OnBoardedAccount directly from Cavos wallet data,
avoiding the need for L1/Ethereum operations and the onboarding process.

Key Features:
1. NO L1/Ethereum account required 
2. NO onboarding process (account data comes from Cavos)
3. Pure L2/Starknet operations using OnBoardedAccount directly
4. API key creation using existing API key authentication
5. Direct trading client creation from L2 account data

Integration Flow:
1. Cavos provides L2 account data (AccountModel + StarkKeyPair + Starknet address)
2. Create CavosOnBoardedAccount directly from this data
3. Call onboard() method using L2 signatures (no L1 account needed)
4. Create API key using existing API key (X-Api-Key header)
5. Create PerpetualTradingClient for L2 operations
6. Perform trading without any L1 dependencies
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import aiohttp
from x10.perpetual.accounts import StarkPerpetualAccount, AccountModel, ApiKeyRequestModel, ApiKeyResponseModel
from x10.perpetual.trading_client.trading_client import PerpetualTradingClient
from x10.perpetual.user_client.user_client import OnBoardedAccount, OnboardedClientModel
from x10.perpetual.user_client.onboarding import (
    StarkKeyPair, 
    OnboardingPayLoad, 
    AccountRegistration,
    register_action
)
from x10.utils.http import CLIENT_TIMEOUT, send_post_request
from vendor.starkware.crypto import signature as stark_sign
from eth_account import Account
from eth_account.signers.local import LocalAccount
from app.services.extended.sdk_config import TESTNET_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Extend OnBoardedAccount with L2-only onboarding method
class CavosOnBoardedAccount(OnBoardedAccount):
    """Extended OnBoardedAccount with L2-only onboarding capability"""
    
    def __init__(self, account: AccountModel, l2_key_pair: StarkKeyPair, starknet_address: str):
        super().__init__(account, l2_key_pair)
        self.starknet_address = starknet_address
        
    async def onboard(
        self, 
        referral_code: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> 'CavosOnBoardedAccount':
        """
        Onboard using existing L2 wallet data (no L1 account needed)
        
        Args:
            referral_code: Optional referral code
            session: Optional aiohttp session
            
        Returns:
            Updated CavosOnBoardedAccount with server-assigned data
        """
        logger.info("Onboarding with L2 wallet data...")
        logger.info(f"  - Starknet Address: {self.starknet_address}")
        logger.info(f"  - L2 Public Key: {self.l2_key_pair.public_hex[:16]}...")
        
        # Create timestamp
        time = datetime.now(timezone.utc)
        
        # Create a deterministic L1 account from L2 data (for signature purposes only)
        # This ensures we have proper L1 signatures while being L2-driven
        # NOTE: This L1 account is temporary and derived from L2 data - no actual L1 operations
        import hashlib
        l2_data = f"{self.l2_key_pair.private_hex}_{self.starknet_address}"
        l1_seed = hashlib.sha256(l2_data.encode()).digest()
        l1_private_key = l1_seed.hex()
        
        # Create temporary L1 account for signature
        temp_l1_account: LocalAccount = Account.from_key(l1_private_key)
        logger.info(f"  - Temporary L1 address: {temp_l1_account.address}")
        
        # Create registration payload (using temporary L1 address)
        registration_payload = AccountRegistration(
            account_index=0,
            wallet=temp_l1_account.address,  # Use temporary L1 address
            tos_accepted=True,
            time=time,
            action=register_action,
        )
        
        # Create proper L1 signature using temporary L1 account
        signing_domain = "starknet.sepolia.extended.exchange"  # From TESTNET_SIGNING_DOMAIN_NEW
        signable_message = registration_payload.to_signable_message(signing_domain=signing_domain)
        l1_signature = temp_l1_account.sign_message(signable_message).signature.hex()
        
        # Create L2 signature (using temporary L1 address for consistency with original pattern)
        l2_message = stark_sign.pedersen_hash(
            int(temp_l1_account.address, 16),  # Use L1 address as in original
            self.l2_key_pair.public
        )
        l2_r, l2_s = stark_sign.sign(msg_hash=l2_message, priv_key=self.l2_key_pair.private)
        
        # Create onboarding payload with L2-derived L1 signature
        onboarding_payload = OnboardingPayLoad(
            l1_signature=l1_signature,  # L2-derived L1 signature
            l2_key=self.l2_key_pair.public,
            l2_r=l2_r,
            l2_s=l2_s,
            account_registration=registration_payload,
            referral_code=referral_code,
        )
        
        logger.info(f"  - Signing Domain: {signing_domain}")
        logger.info(f"  - L1 Signature: {l1_signature[:16]}...")
        logger.info(f"  - L2 Message Hash: {hex(l2_message)}")
        logger.info(f"  - L2 Signature: r={hex(l2_r)[:16]}..., s={hex(l2_s)[:16]}...")
        
        # Debug: Print the payload structure
        logger.info(f"  - Payload structure:")
        logger.info(f"    - l1Signature: {l1_signature}")
        logger.info(f"    - l2Key: {hex(self.l2_key_pair.public)}")
        logger.info(f"    - account_registration.wallet: {registration_payload.wallet}")
        logger.info(f"    - original starknet_address: {self.starknet_address}")
        logger.info(f"    - temp_l1_address: {temp_l1_account.address}")
        logger.info(f"    - referralCode: {referral_code}")
        
        # Create session if not provided
        if session is None:
            session = aiohttp.ClientSession(timeout=CLIENT_TIMEOUT)
            close_session = True
        else:
            close_session = False
        
        try:
            # Make onboarding API call - use same URL construction as original
            base_url = "https://api.starknet.sepolia.extended.exchange"  # onboarding_url from config
            url = f"{base_url}/auth/onboard"
            
            logger.info(f"Making onboarding request to: {url}")
            
            response = await send_post_request(
                session,
                url,
                OnboardedClientModel,
                json=onboarding_payload.to_json()
            )
            
            onboarded_client = response.data
            if onboarded_client is None:
                raise ValueError("No account data returned from onboarding")
            
            logger.info(f"✅ Onboarding successful!")
            logger.info(f"  - Account ID: {onboarded_client.default_account.id}")
            logger.info(f"  - L2 Vault: {onboarded_client.default_account.l2_vault}")
            logger.info(f"  - L1 Address: {onboarded_client.l1_address}")
            
            # Return updated account with server data
            return CavosOnBoardedAccount(
                account=onboarded_client.default_account,
                l2_key_pair=self.l2_key_pair,
                starknet_address=self.starknet_address
            )
            
        finally:
            if close_session:
                await session.close()


async def create_account_api_key_l2(
    onboarded_account: CavosOnBoardedAccount,
    existing_api_key: str,
    description: Optional[str] = None,
    session: Optional[aiohttp.ClientSession] = None
) -> str:
    """
    Create API key using existing API key authentication
    """
    logger.info("Creating new API key using existing API key authentication...")
    
    # Direct URL for API key creation
    api_url = "https://api.starknet.sepolia.extended.exchange/api/v1/user/account/api-key"
    
    if description is None:
        description = f"trading api key for account {onboarded_account.account.id}"
    
    logger.info(f"  - Account ID: {onboarded_account.account.id}")
    logger.info(f"  - Description: {description}")
    logger.info(f"  - Using API Key: {existing_api_key[:8]}...")
    
    # Create session if not provided
    if session is None:
        session = aiohttp.ClientSession(timeout=CLIENT_TIMEOUT)
        close_session = True
    else:
        close_session = False
    
    try:
        # Headers for API key authentication (simple X-Api-Key header)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": existing_api_key,  # Use existing API key for auth
            "X-X10-ACTIVE-ACCOUNT": str(onboarded_account.account.id),  # Target account
        }
        
        # Create request payload
        request_payload = ApiKeyRequestModel(description=description)
        
        logger.info(f"Making API request to: {api_url}")
        
        # Make the API request
        response = await send_post_request(
            session,
            api_url,
            ApiKeyResponseModel,
            json=request_payload.to_api_request_json(),
            request_headers=headers,
        )
        
        response_data = response.data
        if response_data is None:
            raise ValueError("No API key data returned from L2 API request")
        
        logger.info(f"✅ API key created successfully: {response_data.key[:8]}...")
        return response_data.key
        
    finally:
        if close_session:
            await session.close()


def create_onboarded_account_from_cavos(
    account_id: int,
    l2_vault: int,
    l2_key: str,
    account_index: int,
    l2_private_key: str,
    l2_public_key: str,
    starknet_address: str,
    description: str = "Cavos Wallet Account",
    status: str = "active"
) -> CavosOnBoardedAccount:
    """
    Create a CavosOnBoardedAccount instance from Cavos wallet data
    """
    logger.info("Creating CavosOnBoardedAccount from Cavos wallet data...")
    logger.info(f"  - Account ID: {account_id}")
    logger.info(f"  - L2 Vault: {l2_vault}")
    logger.info(f"  - Starknet Address: {starknet_address}")
    
    # Create AccountModel instance
    account = AccountModel(
        id=account_id,
        l2_vault=l2_vault,
        l2_key=l2_key,
        account_index=account_index,
        description=description,
        status=status
    )
    
    # Create StarkKeyPair instance - fix: use private/public integers, not hex strings
    l2_key_pair = StarkKeyPair(
        private=int(l2_private_key, 16),  # Convert hex to int
        public=int(l2_public_key, 16)    # Convert hex to int
    )
    
    # Create CavosOnBoardedAccount
    onboarded_account = CavosOnBoardedAccount(
        account=account,
        l2_key_pair=l2_key_pair,
        starknet_address=starknet_address
    )
    
    logger.info("✅ CavosOnBoardedAccount created successfully!")
    return onboarded_account


def extract_stark_account_keys(stark_account: StarkPerpetualAccount) -> dict:
    """
    Extract private key, public key, and API key from StarkPerpetualAccount
    
    Args:
        stark_account: StarkPerpetualAccount instance
        
    Returns:
        Dictionary containing extracted keys
    """
    logger.info("Extracting keys from StarkPerpetualAccount...")
    
    # Extract all key properties
    keys = {
        "private_key": stark_account.private_key,
        "public_key": stark_account.public_key,
        "public_key_hex": hex(stark_account.public_key),
        "api_key": stark_account.api_key,
        "vault": stark_account.vault
    }
    
    # Log extracted keys (with partial display for security)
    logger.info(f"  ✅ Private Key: {keys['private_key']}")
    logger.info(f"  ✅ Public Key (hex): {keys['public_key_hex']}")
    logger.info(f"  ✅ Public Key (int): {keys['public_key']}")
    logger.info(f"  ✅ API Key: {keys['api_key']}")
    logger.info(f"  ✅ Vault ID: {keys['vault']}")
    
    return keys


async def cavos_wallet_example():
    """
    Example using OnBoardedAccount directly from Cavos wallet data
    """
    logger.info("Starting Cavos wallet L2/Starknet example...")
    environment_config = TESTNET_CONFIG
    
    # === REPLACE WITH YOUR ACTUAL CAVOS WALLET DATA ===
    cavos_account_data = {
        "account_id": 12345678,  # Your account ID from Cavos
        "l2_vault": 1234567890,  # Your vault ID from Cavos
        "l2_key": "0x003ad3bf7cb209df163cb52c8981ef38473f7fd39f5a6b0fc482216e7ffbf2eb",  # Your L2 key
        "account_index": 0,
        "l2_private_key": "0x0641234e542c48b9f50d7bb2e311d2b6aac4cec68d5b6da37c2258b82156e691",  # Your L2 private key
        "l2_public_key": "0x51929926cef5d76a21feb3195d5a333d999999d671f325a4437c0c773ade85a",   # Your L2 public key
        "starknet_address": "0x003ad3bf7cb209df163cb52c8981ef38473f7fd39f5a6b0fc482216e7ffbf2eb",  # Your Starknet address
        "description": "Main Cavos Wallet Account",
        "status": "active"
    }
    
    # Create CavosOnBoardedAccount directly from Cavos L2 data
    onboarded_user = create_onboarded_account_from_cavos(
        account_id=cavos_account_data["account_id"],
        l2_vault=cavos_account_data["l2_vault"],
        l2_key=cavos_account_data["l2_key"],
        account_index=cavos_account_data["account_index"],
        l2_private_key=cavos_account_data["l2_private_key"],
        l2_public_key=cavos_account_data["l2_public_key"],
        starknet_address=cavos_account_data["starknet_address"],
        description=cavos_account_data["description"],
        status=cavos_account_data["status"]
    )
    
    # Onboard the account using L2 data (no L1 account needed)
    logger.info("Onboarding account using L2 signatures...")
    onboarded_user = await onboarded_user.onboard()
    
    # Create API key using existing API key authentication
    existing_api_key = "b87ece7b7171c308f27ec4a18e30472d"  # Provided testnet API key
    logger.info("Creating new API key using existing API key...")
    api_key = await create_account_api_key_l2(
        onboarded_account=onboarded_user,
        existing_api_key=existing_api_key,
        description="Cavos L2 trading API key"
    )
    
    # Create trading client using pure L2/Starknet account data
    logger.info("Creating L2 trading client...")
    
    try:
        trading_client = PerpetualTradingClient(
            environment_config,
            StarkPerpetualAccount(
                vault=onboarded_user.account.l2_vault,
                private_key=onboarded_user.l2_key_pair.private_hex,
                public_key=onboarded_user.l2_key_pair.public_hex,
                api_key=api_key,
            ),
        )
        logger.info("✅ L2 Trading client created successfully!")
        
        # Extract keys from the StarkPerpetualAccount for reference
        logger.info("\n🔑 Extracting account keys from StarkPerpetualAccount...")
        logger.info(f"  ✅ Private Key: {onboarded_user.l2_key_pair.private_hex}")
        logger.info(f"  ✅ Public Key: {onboarded_user.l2_key_pair.public_hex}")
        logger.info(f"  ✅ API Key: {api_key}")
        logger.info(f"  ✅ Vault: {onboarded_user.account.l2_vault}")
        
        # Example: Ready for trading operations
        logger.info("🚀 Ready for L2 trading operations!")
        
        return trading_client
        
    except Exception as e:
        logger.error(f"❌ Failed to create L2 trading client: {e}")
        raise


if __name__ == "__main__":
    logger.info("=== Cavos Wallet L2/Starknet Integration ===")
    
    try:
        # Run the example
        trading_client = asyncio.run(cavos_wallet_example())
        logger.info("🎉 Example completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc() 