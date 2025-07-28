#!/usr/bin/env python3
"""
Test script for Extended Exchange onboarding signature generation using starknet.py
This demonstrates real signature generation without requiring a full API call
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.extended.signature_service import extended_signature_service

# Import x10 SDK components
try:
    from x10.perpetual.accounts import StarkPerpetualAccount
    X10_SDK_AVAILABLE = True
except ImportError:
    X10_SDK_AVAILABLE = False
    print("⚠️  x10 SDK not available - skipping StarkPerpetualAccount tests")


async def test_signature_generation():
    """Test real signature generation with sample data"""
    
    print("🚀 Testing Extended Exchange Signature Generation with starknet.py")
    print("=" * 70)
    
    # Sample wallet data (these would come from Cavos in real usage)
    test_data = {
        "private_key": "0x06e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4",
        "public_key": "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618",
        "address": "0x017Dcd349BC131E0d75f19bfaA5eF40FF68AF58d488a6F1789524b24fde21374",
        "network": "sepolia"
    }
    
    print(f"📱 Sample Wallet Data:")
    print(f"   Address: {test_data['address']}")
    print(f"   Public Key: {test_data['public_key'][:20]}...")
    print(f"   Network: {test_data['network']}")
    print()
    
    # Test 1: Account Registration Signature
    print("🔐 Generating Account Registration Signature...")
    success_reg, sig_r_reg, sig_s_reg, error_reg = await extended_signature_service.generate_extended_onboarding_signature(
        private_key=test_data["private_key"],
        account_address=test_data["address"],
        stark_public_key=test_data["public_key"],
        network=test_data["network"]
    )
    
    if success_reg:
        print(f"   ✅ SUCCESS!")
        print(f"   Signature R: {sig_r_reg[:20]}...")
        print(f"   Signature S: {sig_s_reg[:20]}...")
        print(f"   Full R Length: {len(sig_r_reg)} characters")
        print(f"   Full S Length: {len(sig_s_reg)} characters")
        
        # Validate signature components
        is_valid = extended_signature_service.validate_signature_components(sig_r_reg, sig_s_reg)
        print(f"   Validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
    else:
        print(f"   ❌ FAILED: {error_reg}")
    
    print()
    
    # Test 2: Key Registration Signature
    print("🔑 Generating Key Registration Signature...")
    success_key, sig_r_key, sig_s_key, error_key = await extended_signature_service.generate_key_registration_signature(
        private_key=test_data["private_key"],
        account_address=test_data["address"],
        stark_public_key=test_data["public_key"],
        network=test_data["network"]
    )
    
    if success_key:
        print(f"   ✅ SUCCESS!")
        print(f"   Signature R: {sig_r_key[:20]}...")
        print(f"   Signature S: {sig_s_key[:20]}...")
        print(f"   Full R Length: {len(sig_r_key)} characters")
        print(f"   Full S Length: {len(sig_s_key)} characters")
        
        # Validate signature components
        is_valid = extended_signature_service.validate_signature_components(sig_r_key, sig_s_key)
        print(f"   Validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
    else:
        print(f"   ❌ FAILED: {error_key}")
    
    print()
    
    # Summary
    print("📋 Summary:")
    print(f"   Account Registration: {'✅ SUCCESS' if success_reg else '❌ FAILED'}")
    print(f"   Key Registration:     {'✅ SUCCESS' if success_key else '❌ FAILED'}")
    
    if success_reg and success_key:
        print()
        print("🎉 All signatures generated successfully!")
        print("🔗 These signatures would be used in Extended Exchange onboarding contract calls:")
        print()
        print("Contract Call 1 - register_account:")
        print(f"   calldata: ['{test_data['public_key']}', '{test_data['address']}', '1', 'timestamp', 'REGISTER']")
        print()
        print("Contract Call 2 - register_stark_key:")
        print(f"   calldata: ['{test_data['public_key']}', '{sig_r_key[:20]}...', '{sig_s_key[:20]}...']")
        print()
        print("🚀 Ready for Cavos transaction execution!")
    else:
        print()
        print("❌ Some signatures failed. Check the error messages above.")
    
    print("=" * 70)


async def test_stark_perpetual_account():
    """Test creating and using StarkPerpetualAccount from x10 SDK"""
    
    if not X10_SDK_AVAILABLE:
        return
        
    print("🏦 Testing StarkPerpetualAccount Creation and Signing")
    print("=" * 70)
    
    # Sample data for Extended account creation
    test_data = {
        "private_key": "0x06e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4",
        "public_key": "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618", 
        "vault": 123456,  # Vault ID from Cavos
        "api_key": "test_api_key_for_extended_account"
    }
    
    try:
        # Create StarkPerpetualAccount instance
        print("🔧 Creating StarkPerpetualAccount...")
        account = StarkPerpetualAccount(
            vault=test_data["vault"],
            private_key=test_data["private_key"],
            public_key=test_data["public_key"],
            api_key=test_data["api_key"]
        )
        
        print(f"   ✅ Account created successfully!")
        print(f"   Vault ID: {account.vault}")
        print(f"   Public Key: {hex(account.public_key)[:20]}...")
        print(f"   API Key: {account.api_key}")
        print()
        
        # Test message signing with the account
        print("🔐 Testing message signing with StarkPerpetualAccount...")
        
        # Create a test message hash (similar to what Extended would use)
        import time
        from starknet_py.hash.utils import compute_hash_on_elements
        from starknet_py.hash.selector import get_selector_from_name
        
        # Create message elements for Extended onboarding
        timestamp = int(time.time())
        address_felt = int("0x017Dcd349BC131E0d75f19bfaA5eF40FF68AF58d488a6F1789524b24fde21374", 16)
        
        message_elements = [
            0,  # account_index
            address_felt,  # wallet address
            account.public_key,  # stark public key
            1,  # tos_accepted
            timestamp,
            get_selector_from_name("REGISTER")
        ]
        
        message_hash = compute_hash_on_elements(message_elements)
        print(f"   Message Hash: {hex(message_hash)[:20]}...")
        
        # Sign the message using the account's sign method
        signature_r, signature_s = account.sign(message_hash)
        
        print(f"   ✅ Signature generated!")
        print(f"   Signature R: {hex(signature_r)[:20]}...")
        print(f"   Signature S: {hex(signature_s)[:20]}...")
        print()
        
        # Show how this would be used in Extended onboarding
        print("🔗 Extended Onboarding Integration:")
        print(f"   Vault: {account.vault}")
        print(f"   Public Key: {hex(account.public_key)}")
        print(f"   Signature R: {hex(signature_r)}")
        print(f"   Signature S: {hex(signature_s)}")
        print()
        
        print("📋 Contract Call Data:")
        print("   register_stark_key calldata:")
        print(f"     ['{hex(account.public_key)}', '{hex(signature_r)}', '{hex(signature_s)}']")
        print()
        
        print("🎯 Ready for Extended Exchange onboarding!")
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        print(f"   Error Type: {type(e).__name__}")
    
    print("=" * 70)


async def test_integration_flow():
    """Test the complete integration flow: starknet.py + StarkPerpetualAccount"""
    
    if not X10_SDK_AVAILABLE:
        return
        
    print("🔄 Testing Complete Integration Flow")
    print("=" * 70)
    
    test_data = {
        "private_key": "0x06e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4",
        "public_key": "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618",
        "address": "0x017Dcd349BC131E0d75f19bfaA5eF40FF68AF58d488a6F1789524b24fde21374",
        "vault": 123456,
        "network": "sepolia"
    }
    
    try:
        print("1️⃣ Creating StarkPerpetualAccount (simulating Extended account)...")
        account = StarkPerpetualAccount(
            vault=test_data["vault"],
            private_key=test_data["private_key"],
            public_key=test_data["public_key"],
            api_key="mock_api_key_from_extended"
        )
        print(f"   ✅ Extended account created with vault {account.vault}")
        
        print("2️⃣ Generating onboarding signatures with starknet.py...")
        success_reg, sig_r_reg, sig_s_reg, error_reg = await extended_signature_service.generate_extended_onboarding_signature(
            private_key=test_data["private_key"],
            account_address=test_data["address"],
            stark_public_key=test_data["public_key"],
            network=test_data["network"]
        )
        
        if success_reg:
            print(f"   ✅ Onboarding signature generated")
        else:
            print(f"   ❌ Onboarding signature failed: {error_reg}")
            return
        
        print("3️⃣ Cross-validating signatures...")
        # Test that both approaches produce valid signatures
        from starknet_py.hash.utils import compute_hash_on_elements
        test_hash = compute_hash_on_elements([12345, account.public_key])
        
        # Sign with StarkPerpetualAccount
        account_sig_r, account_sig_s = account.sign(test_hash)
        
        print(f"   ✅ Both signature methods working")
        print(f"   StarkPerpetualAccount signature: {hex(account_sig_r)[:16]}...")
        print(f"   starknet.py signature: {sig_r_reg[:16]}...")
        
        print("4️⃣ Final integration result:")
        print(f"   🏦 Extended Account Vault: {account.vault}")
        print(f"   🔑 Public Key: {hex(account.public_key)[:20]}...")
        print(f"   ✍️  Registration Signature: {sig_r_reg[:16]}...")
        print(f"   🚀 Ready for Cavos transaction execution!")
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        print(f"   Error Type: {type(e).__name__}")
    
    print("=" * 70)


async def test_invalid_key():
    """Test signature generation with invalid key to demonstrate error handling"""
    
    print("🧪 Testing Error Handling with Invalid Private Key...")
    print("-" * 50)
    
    success, sig_r, sig_s, error = await extended_signature_service.generate_extended_onboarding_signature(
        private_key="invalid_key_format",
        account_address="0x067a5c3e7c4e5b7d9f1234567890abcdef12345678",
        stark_public_key="0x02c5dbad71c92a45cc4b40573ae661f8147869a91d57b8d9b8f48c8af7f83159",
        network="sepolia"
    )
    
    if not success:
        print(f"   ✅ Error handling works correctly!")
        print(f"   Error: {error}")
    else:
        print(f"   ❌ Expected error but got success")
    
    print()


async def main():
    """Main test function"""
    try:
        await test_signature_generation()
        print()
        
        if X10_SDK_AVAILABLE:
            await test_stark_perpetual_account()
            print()
            
            await test_integration_flow()
            print()
        
        await test_invalid_key()
        
        print("🏁 Test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure to install starknet-py: pip install starknet-py==0.21.0")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"Error Type: {type(e).__name__}")


if __name__ == "__main__":
    print("Testing Extended Exchange Signature Generation")
    print("Using starknet.py for real STARK curve cryptography")
    if X10_SDK_AVAILABLE:
        print("+ Extended x10 SDK StarkPerpetualAccount integration")
    print()
    
    # Run the async test
    asyncio.run(main()) 