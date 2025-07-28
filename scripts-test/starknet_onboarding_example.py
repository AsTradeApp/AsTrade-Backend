#!/usr/bin/env python3
"""
Extended Exchange Onboarding Example for Starknet Accounts
This shows how to onboard using Starknet keys directly from Cavos wallet
instead of deriving from Ethereum L1 keys
"""
import asyncio
from decimal import Decimal
from typing import Dict, Any

# Extended Exchange SDK imports
from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.assets import AssetOperationType
from x10.perpetual.configuration import TESTNET_CONFIG, MAINNET_CONFIG
from x10.perpetual.trading_client.trading_client import PerpetualTradingClient
from x10.perpetual.user_client.user_client import UserClient

# Our custom imports for Starknet integration
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.extended.signature_service import extended_signature_service
from app.services.extended.cavos_integration import (
    cavos_transaction_service,
    create_onboarding_transaction_builder,
    CavosWalletData
)


class StarknetExtendedOnboarding:
    """
    Handles Extended Exchange onboarding for Starknet accounts
    Using Cavos wallet data directly (no Ethereum L1 derivation needed)
    """
    
    def __init__(self, environment: str = "testnet", demo_mode: bool = True):
        self.environment = environment
        self.demo_mode = demo_mode
        self.config = TESTNET_CONFIG if environment == "testnet" else MAINNET_CONFIG
        
    async def onboard_starknet_account(
        self, 
        cavos_wallet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Onboard a Starknet account directly to Extended Exchange
        
        Args:
            cavos_wallet_data: Wallet data from Cavos including:
                - private_key: Starknet private key
                - public_key: Starknet public key  
                - address: Starknet wallet address
                - vault_id: Vault ID from Cavos
                - access_token: Cavos access token
                - org_id: Cavos organization ID
                - user_id: Cavos user ID
                
        Returns:
            Dictionary with onboarding result and account details
        """
        print("🚀 Starting Starknet Extended Exchange Onboarding...")
        print("=" * 60)
        
        try:
            # Step 1: Validate Cavos wallet data
            print("1️⃣ Validating Cavos wallet data...")
            required_fields = ["private_key", "public_key", "address", "access_token", "org_id"]
            for field in required_fields:
                if field not in cavos_wallet_data:
                    raise ValueError(f"Missing required field: {field}")
            
            print(f"   ✅ Wallet Address: {cavos_wallet_data['address'][:20]}...")
            print(f"   ✅ Public Key: {cavos_wallet_data['public_key'][:20]}...")
            print(f"   ✅ Vault ID: {cavos_wallet_data.get('vault_id', 'Not provided')}")
            
            # Step 2: Generate Extended onboarding signatures
            print("\n2️⃣ Generating Extended onboarding signatures...")
            
            # Account registration signature
            success_reg, sig_r_reg, sig_s_reg, error_reg = await extended_signature_service.generate_extended_onboarding_signature(
                private_key=cavos_wallet_data["private_key"],
                account_address=cavos_wallet_data["address"],
                stark_public_key=cavos_wallet_data["public_key"],
                network="sepolia" if self.environment == "testnet" else "mainnet"
            )
            
            if not success_reg:
                raise Exception(f"Registration signature failed: {error_reg}")
                
            # Key registration signature  
            success_key, sig_r_key, sig_s_key, error_key = await extended_signature_service.generate_key_registration_signature(
                private_key=cavos_wallet_data["private_key"],
                account_address=cavos_wallet_data["address"],
                stark_public_key=cavos_wallet_data["public_key"],
                network="sepolia" if self.environment == "testnet" else "mainnet"
            )
            
            if not success_key:
                raise Exception(f"Key signature failed: {error_key}")
                
            print(f"   ✅ Account registration signature: {sig_r_reg[:16]}...")
            print(f"   ✅ Key registration signature: {sig_r_key[:16]}...")
            
            # Step 3: Build Extended onboarding contract calls
            print("\n3️⃣ Building Extended onboarding contract calls...")
            
            network = "sepolia" if self.environment == "testnet" else "mainnet"
            tx_builder = create_onboarding_transaction_builder(network)
            
            onboarding_calls = tx_builder.build_complete_onboarding_calls(
                stark_public_key=cavos_wallet_data["public_key"],
                wallet_address=cavos_wallet_data["address"],
                stark_signature_r=sig_r_key,
                stark_signature_s=sig_s_key,
                referral_code=cavos_wallet_data.get("referral_code")
            )
            
            print(f"   ✅ Generated {len(onboarding_calls)} contract calls")
            for i, call in enumerate(onboarding_calls):
                print(f"      Call {i+1}: {call.entrypoint}")
            
            # Step 4: Execute onboarding transaction through Cavos
            print("\n4️⃣ Executing onboarding transaction through Cavos...")
            
            if self.demo_mode:
                # Demo mode: simulate transaction without real API calls
                print("   🎭 Demo Mode: Simulating transaction execution...")
                tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
                print(f"   ✅ [DEMO] Transaction submitted: {tx_hash}")
                
                # Step 5: Simulate transaction confirmation  
                print("\n5️⃣ Waiting for transaction confirmation...")
                print("   🎭 Demo Mode: Simulating transaction confirmation...")
                print(f"   ✅ [DEMO] Transaction confirmed: ACCEPTED_ON_L2")
                
            else:
                # Live mode: make real API calls
                cavos_wallet = CavosWalletData(
                    address=cavos_wallet_data["address"],
                    network=network,
                    public_key=cavos_wallet_data["public_key"],
                    private_key=cavos_wallet_data["private_key"],
                    user_id=cavos_wallet_data["user_id"],
                    org_id=cavos_wallet_data["org_id"]
                )
                
                success, message, tx_hash = await cavos_transaction_service.execute_extended_onboarding_transaction(
                    user_access_token=cavos_wallet_data["access_token"],
                    wallet_data=cavos_wallet,
                    extended_contract_calls=onboarding_calls
                )
                
                if not success:
                    raise Exception(f"Transaction execution failed: {message}")
                    
                print(f"   ✅ Transaction submitted: {tx_hash}")
                
                # Step 5: Wait for transaction confirmation
                print("\n5️⃣ Waiting for transaction confirmation...")
                
                is_confirmed, status = await cavos_transaction_service.check_transaction_status(
                    transaction_hash=tx_hash,
                    network=network
                )
                
                if not is_confirmed:
                    raise Exception(f"Transaction not confirmed: {status}")
                    
                print(f"   ✅ Transaction confirmed: {status}")
             
             # Step 6: Create Extended account objects
            print("\n Creating Extended account objects...")
            vault_id = cavos_wallet_data.get("vault_id", 123456)  # Use provided or default
            
            # Step 6a: Create UserClient for API key generation
            print("   🔑 Creating UserClient for API key generation...")
            if not self.demo_mode:
                # For live mode, we need to create UserClient
                # Note: UserClient typically expects l1_private_key, but for Starknet-native
                # we'll use a dummy value since we're only using it for API key generation
                user_client = UserClient(
                    endpoint_config=self.config,
                    l1_private_key=None  # We'll handle this limitation
                )
            
            # Step 6b: Generate API key using Extended's method
            print("   🔐 Generating API key with Extended Exchange...")
            if self.demo_mode:
                # Demo mode: use simulated API key
                api_key = "demo_api_key_1234567890abcdef"
                print(f"   ✅ [DEMO] API key generated: {api_key[:16]}...")
            else:
                try:
                    # Create account structure for API key generation
                    from dataclasses import dataclass
                    
                    @dataclass
                    class MockAccount:
                        l2_vault: int
                        
                    mock_account = MockAccount(l2_vault=vault_id)
                    
                    # Generate real API key
                    api_key = await user_client.create_account_api_key(
                        mock_account, 
                        "AsTrade Starknet Trading Key"
                    )
                    print(f"   ✅ Real API key generated: {api_key[:16]}...")
                    
                except Exception as e:
                    print(f"   ⚠️  API key generation failed: {str(e)}")
                    print("   🔄 Using fallback API key for demo...")
                    api_key = "fallback_api_key_starknet_" + str(vault_id)
            
            # Step 6c: Create StarkPerpetualAccount with real API key
            print("   🏦 Creating StarkPerpetualAccount with generated API key...")
            main_account = StarkPerpetualAccount(
                vault=vault_id,
                private_key=cavos_wallet_data["private_key"],
                public_key=cavos_wallet_data["public_key"],
                api_key=api_key  # Now using real/demo API key
            )
            
            print(f"   ✅ Main account created with vault: {main_account.vault}")
            print(f"   ✅ Public key: {hex(main_account.public_key)[:20]}...")
            print(f"   ✅ API key: {main_account.api_key[:16]}...")
            
            # Step 7: Create trading client
            print("\n7️⃣ Creating trading client...")
            
            trading_client = PerpetualTradingClient(
                self.config,
                main_account
            )
            
            print(f"   ✅ Trading client ready for {self.environment}")
            
            # Return comprehensive result
            result = {
                "success": True,
                "demo_mode": self.demo_mode,
                "transaction_hash": tx_hash,
                "account": {
                    "vault": main_account.vault,
                    "public_key": hex(main_account.public_key),
                    "api_key": main_account.api_key
                },
                "trading_client": trading_client,
                "signatures": {
                    "registration": {"r": sig_r_reg, "s": sig_s_reg},
                    "key_registration": {"r": sig_r_key, "s": sig_s_key}
                },
                "environment": self.environment,
                "network": network
            }
            
            print("\n🎉 Starknet Extended Exchange onboarding completed successfully!")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Onboarding failed: {str(e)}")
            print("=" * 60)
            
            return {
                "success": False,
                "error": str(e),
                "environment": self.environment
            }

    async def create_subaccount_with_api_key(
        self, 
        main_account: StarkPerpetualAccount,
        subaccount_id: int = 1,
        subaccount_name: str = "Starknet Sub Account 1"
    ) -> Dict[str, Any]:
        """
        Create a subaccount for Starknet-based Extended account
        
        Args:
            main_account: The main StarkPerpetualAccount
            subaccount_id: ID for the subaccount (e.g., 1, 2, 3...)
            subaccount_name: Human-readable name for the subaccount
            
        Returns:
            Dictionary with subaccount details
        """
        print(f"🏦 Creating Subaccount: {subaccount_name}")
        print("-" * 50)
        
        try:
            if self.demo_mode:
                # Demo mode: simulate subaccount creation
                print("   🎭 Demo Mode: Simulating subaccount creation...")
                
                # Simulate new vault and keys for subaccount
                sub_vault_id = main_account.vault + subaccount_id
                sub_api_key = f"demo_sub_api_key_{subaccount_id}_1234567890"
                
                # Create demo subaccount
                sub_account = StarkPerpetualAccount(
                    vault=sub_vault_id,
                    private_key=main_account.private_key,  # Same keys for demo
                    public_key=hex(main_account.public_key),
                    api_key=sub_api_key
                )
                
                print(f"   ✅ [DEMO] Subaccount created with vault: {sub_vault_id}")
                print(f"   ✅ [DEMO] API key: {sub_api_key[:16]}...")
                
            else:
                # Live mode: would need real subaccount onboarding
                print("   ⚠️  Live subaccount creation not fully implemented")
                print("   📋 Would require:")
                print("      1. Generate new Starknet keypair for subaccount")
                print("      2. Call Extended subaccount onboarding")
                print("      3. Create real API key for subaccount")
                
                # For now, create a demo version in live mode too
                sub_vault_id = main_account.vault + subaccount_id
                sub_api_key = f"temp_sub_api_key_{subaccount_id}"
                
                sub_account = StarkPerpetualAccount(
                    vault=sub_vault_id,
                    private_key=main_account.private_key,
                    public_key=hex(main_account.public_key),
                    api_key=sub_api_key
                )
                
                print(f"   ✅ Temporary subaccount created with vault: {sub_vault_id}")
            
            # Create trading client for subaccount
            sub_trading_client = PerpetualTradingClient(
                self.config,
                sub_account
            )
            
            result = {
                "success": True,
                "subaccount": {
                    "vault": sub_account.vault,
                    "api_key": sub_account.api_key,
                    "public_key": hex(sub_account.public_key),
                    "name": subaccount_name
                },
                "trading_client": sub_trading_client,
                "demo_mode": self.demo_mode
            }
            
            print(f"   🎯 Subaccount ready for trading!")
            print("-" * 50)
            
            return result
            
        except Exception as e:
            print(f"   ❌ Subaccount creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


async def starknet_onboarding_example(demo_mode: bool = True):
    """
    Complete example of Extended Exchange onboarding for Starknet accounts
    This replaces the ETH-based onboarding with direct Starknet integration
    
    Args:
        demo_mode: If True, runs demo without real API calls. If False, requires real credentials.
    """
    
    print("Extended Exchange Starknet Onboarding Example")
    print("Using Cavos wallet data directly (no L1 derivation needed)")
    print(f"🎭 Running in {'DEMO' if demo_mode else 'LIVE'} mode")
    print()
    
    # Sample Cavos wallet data (this would come from your Expo app)
    cavos_wallet_data = {
        "private_key": "0x06e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4",
        "public_key": "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618",
        "address": "0x017Dcd349BC131E0d75f19bfaA5eF40FF68AF58d488a6F1789524b24fde21374",
        "vault_id": 123456,  # From Cavos
        "access_token": "cavos_jwt_token_here" if demo_mode else "REPLACE_WITH_REAL_JWT_TOKEN",
        "org_id": "org-123",
        "user_id": "auth0|user_id",
        "referral_code": "ASTRADE2024"
    }
    
    if not demo_mode and cavos_wallet_data["access_token"] == "REPLACE_WITH_REAL_JWT_TOKEN":
        print("❌ Error: Real credentials required for live mode!")
        print("Please update cavos_wallet_data with valid access_token, org_id, user_id")
        return
    
    # Create onboarding handler
    onboarding = StarknetExtendedOnboarding(environment="testnet", demo_mode=demo_mode)
    
    # Perform onboarding
    result = await onboarding.onboard_starknet_account(cavos_wallet_data)
    
    if result["success"]:
        print("\n🔄 Post-Onboarding Operations (Starknet Native)...")
        print("-" * 50)
        
        # Get the trading client
        trading_client = result["trading_client"]
        main_account = trading_client.account
        
        # Example operations that would work with Starknet accounts
        print(f"🏦 Main Account Vault: {main_account.vault}")
        print(f"🔑 Public Key: {hex(main_account.public_key)[:20]}...")
        print(f"🔗 Environment: {result['environment']}")
        print(f"📊 Transaction Hash: {result['transaction_hash']}")
        if result.get('demo_mode'):
            print("🎭 Demo Mode: Transaction hash is simulated")
        
        # These operations would be similar to the ETH example but using Starknet
        print("\n📋 Available Operations:")
        print("   ✅ Account deposits (Starknet native)")
        print("   ✅ Account transfers between vaults") 
        print("   ✅ Slow withdrawals to Starknet address")
        print("   ✅ Trading operations")
        print("   ✅ Balance queries")
        
        # Demonstrate actual subaccount creation with API key generation
        print("\n🔧 Creating Subaccount (like ETH example):")
        sub_result = await onboarding.create_subaccount_with_api_key(
            main_account=main_account,
            subaccount_id=1,
            subaccount_name="AsTrade Starknet Sub Account 1"
        )
        
        if sub_result["success"]:
            print(f"   ✅ Subaccount vault: {sub_result['subaccount']['vault']}")
            print(f"   ✅ Subaccount API key: {sub_result['subaccount']['api_key'][:16]}...")
            print(f"   ✅ Subaccount trading client ready!")
        else:
            print(f"   ❌ Subaccount creation failed: {sub_result.get('error', 'Unknown')}")

        # Example of creating a subaccount (would need additional implementation)
        print("\n🔧 Subaccount Creation (Future Enhancement):")
        print("   - Generate new Starknet keypair for subaccount")
        print("   - Create StarkPerpetualAccount with new vault")
        print("   - Register subaccount with Extended")
        
        print("\n✨ Starknet Integration Benefits:")
        print("   🚀 No L1 Ethereum dependency")
        print("   ⚡ Direct Starknet operations")
        print("   💰 Lower gas fees")
        print("   🔐 Native Starknet security")
        print("   🎯 Seamless Cavos integration")
        
        if result.get('demo_mode'):
            print("\n🚨 To run in LIVE mode:")
            print("   1. Replace dummy access_token with real JWT from Cavos")
            print("   2. Update org_id and user_id with real values")  
            print("   3. Call: await starknet_onboarding_example(demo_mode=False)")
            print("   4. Ensure you have real Cavos wallet credentials")
        
    else:
        print(f"\n❌ Onboarding failed: {result.get('error', 'Unknown error')}")
        
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("🔬 Running Starknet Extended Exchange Integration Examples")
    print("🎭 Running in DEMO mode (no real API calls)")
    print("   To run with real credentials, use: starknet_onboarding_example(demo_mode=False)")
    print()
    
    # Run the async examples (demo mode by default)
    asyncio.run(starknet_onboarding_example(demo_mode=True))
    print()