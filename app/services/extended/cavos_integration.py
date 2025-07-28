"""
Cavos Integration Service for Extended Exchange Onboarding
Handles transaction signing and execution through Cavos API
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple
import aiohttp
import structlog
from dataclasses import dataclass

from app.config.settings import settings


logger = structlog.get_logger()


@dataclass
class CavosWalletData:
    """Cavos wallet data structure"""
    address: str
    network: str  # "sepolia" or "mainnet"
    public_key: str
    private_key: str  # encrypted by Cavos
    user_id: str
    org_id: str


@dataclass
class ExtendedOnboardingCall:
    """Starknet contract call for Extended onboarding"""
    contract_address: str
    entrypoint: str
    calldata: List[str]


class CavosTransactionService:
    """
    Service for executing Extended onboarding transactions through Cavos API
    """
    
    def __init__(self):
        self.base_url = "https://services.cavos.xyz/api/v1/external"
        self.timeout = aiohttp.ClientTimeout(total=60.0)  # Extended timeout for transactions
        
    async def execute_extended_onboarding_transaction(
        self,
        user_access_token: str,
        wallet_data: CavosWalletData,
        extended_contract_calls: List[ExtendedOnboardingCall]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Execute Extended Exchange onboarding transaction through Cavos
        
        Args:
            user_access_token: User's Cavos access token
            wallet_data: Cavos wallet information
            extended_contract_calls: Contract calls for Extended onboarding
            
        Returns:
            Tuple of (success, message, transaction_hash)
        """
        try:
            logger.info(
                "Executing Extended onboarding transaction via Cavos",
                wallet_address=wallet_data.address,
                network=wallet_data.network,
                calls_count=len(extended_contract_calls)
            )
            
            # Prepare transaction payload
            calls = []
            for call in extended_contract_calls:
                calls.append({
                    "contractAddress": call.contract_address,
                    "entrypoint": call.entrypoint,
                    "calldata": call.calldata
                })
            
            payload = {
                "address": wallet_data.address,
                "org_id": wallet_data.org_id,
                "calls": calls,
                "network": wallet_data.network
            }
            
            headers = {
                "Authorization": f"Bearer {user_access_token}",
                "Content-Type": "application/json",
                "User-Agent": "AsTrade/1.0"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/execute/session"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        tx_hash = response_data.get("transaction_hash")
                        status = response_data.get("status", "SUBMITTED")
                        
                        logger.info(
                            "Extended onboarding transaction submitted successfully",
                            wallet_address=wallet_data.address,
                            transaction_hash=tx_hash,
                            status=status
                        )
                        
                        return True, f"Transaction submitted with status: {status}", tx_hash
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(
                            "Failed to execute Extended onboarding transaction",
                            wallet_address=wallet_data.address,
                            status_code=response.status,
                            error=error_msg
                        )
                        return False, f"Transaction failed: {error_msg}", None
                        
        except Exception as e:
            logger.error(
                "Error executing Extended onboarding transaction",
                wallet_address=wallet_data.address,
                error=str(e)
            )
            return False, f"Execution error: {str(e)}", None
    
    async def check_transaction_status(
        self,
        transaction_hash: str,
        network: str
    ) -> Tuple[bool, str]:
        """
        Check Extended onboarding transaction status
        
        Args:
            transaction_hash: Transaction hash to check
            network: Network ("sepolia" or "mainnet")
            
        Returns:
            Tuple of (is_confirmed, status)
        """
        try:
            # For now, we'll simulate status checking
            # In production, you would use Starknet RPC or block explorer
            
            await asyncio.sleep(2)  # Simulate network delay
            
            # Mock successful transaction confirmation
            logger.info(
                "Checking Extended onboarding transaction status",
                transaction_hash=transaction_hash,
                network=network
            )
            
            # In real implementation, you would:
            # 1. Use Starknet RPC to check transaction receipt
            # 2. Parse the receipt to confirm Extended account creation
            # 3. Extract any relevant data (account ID, etc.)
            
            return True, "ACCEPTED_ON_L2"
            
        except Exception as e:
            logger.error(
                "Error checking transaction status",
                transaction_hash=transaction_hash,
                error=str(e)
            )
            return False, f"Status check failed: {str(e)}"


class ExtendedOnboardingTransactionBuilder:
    """
    Builder for Extended Exchange onboarding transaction calls
    """
    
    def __init__(self, network: str = "sepolia"):
        self.network = network
        # Extended Exchange contract addresses (these would be real addresses)
        self.contracts = {
            "sepolia": {
                "onboarding": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
                "account_registry": "0x1234567890abcdef1234567890abcdef12345678"
            },
            "mainnet": {
                "onboarding": "0xabcdef1234567890abcdef1234567890abcdef12",
                "account_registry": "0x987654321fedcba987654321fedcba9876543210"
            }
        }
    
    def build_account_registration_call(
        self,
        stark_public_key: str,
        wallet_address: str,
        referral_code: Optional[str] = None
    ) -> ExtendedOnboardingCall:
        """
        Build Extended account registration contract call
        
        Args:
            stark_public_key: Starknet public key
            wallet_address: Wallet address
            referral_code: Optional referral code
            
        Returns:
            ExtendedOnboardingCall for account registration
        """
        calldata = [
            stark_public_key,
            wallet_address,
            "1",  # tos_accepted (boolean as string)
            str(int(time.time())),  # timestamp
            "REGISTER"  # action
        ]
        
        if referral_code:
            calldata.append(referral_code)
        
        return ExtendedOnboardingCall(
            contract_address=self.contracts[self.network]["onboarding"],
            entrypoint="register_account",
            calldata=calldata
        )
    
    def build_key_registration_call(
        self,
        stark_public_key: str,
        stark_signature_r: str,
        stark_signature_s: str
    ) -> ExtendedOnboardingCall:
        """
        Build Extended key registration contract call
        
        Args:
            stark_public_key: Starknet public key
            stark_signature_r: Stark signature R component
            stark_signature_s: Stark signature S component
            
        Returns:
            ExtendedOnboardingCall for key registration
        """
        calldata = [
            stark_public_key,
            stark_signature_r,
            stark_signature_s
        ]
        
        return ExtendedOnboardingCall(
            contract_address=self.contracts[self.network]["onboarding"],
            entrypoint="register_stark_key",
            calldata=calldata
        )
    
    def build_complete_onboarding_calls(
        self,
        stark_public_key: str,
        wallet_address: str,
        stark_signature_r: str,
        stark_signature_s: str,
        referral_code: Optional[str] = None
    ) -> List[ExtendedOnboardingCall]:
        """
        Build complete set of Extended onboarding contract calls
        
        Args:
            stark_public_key: Starknet public key
            wallet_address: Wallet address
            stark_signature_r: Stark signature R component
            stark_signature_s: Stark signature S component
            referral_code: Optional referral code
            
        Returns:
            List of ExtendedOnboardingCall objects
        """
        calls = []
        
        # 1. Register account
        calls.append(self.build_account_registration_call(
            stark_public_key, wallet_address, referral_code
        ))
        
        # 2. Register Stark key
        calls.append(self.build_key_registration_call(
            stark_public_key, stark_signature_r, stark_signature_s
        ))
        
        return calls


# Service instances
cavos_transaction_service = CavosTransactionService()


def create_onboarding_transaction_builder(network: str = "sepolia") -> ExtendedOnboardingTransactionBuilder:
    """
    Create an Extended onboarding transaction builder for the specified network
    
    Args:
        network: "sepolia" or "mainnet"
        
    Returns:
        ExtendedOnboardingTransactionBuilder instance
    """
    return ExtendedOnboardingTransactionBuilder(network) 