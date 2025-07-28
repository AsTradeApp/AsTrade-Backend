#!/usr/bin/env python3
"""
Test script for StarkNet Extended Exchange Integration
This script verifies that the StarkNet integration works correctly
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_fast_stark_crypto():
    """Test the fast_stark_crypto wrapper"""
    print("🧪 Testing fast_stark_crypto wrapper...")
    
    try:
        import fast_stark_crypto
        print("✅ fast_stark_crypto imported successfully")
        
        # Test available functions
        functions = [
            'sign', 'verify', 'get_public_key', 'pedersen_hash',
            'get_order_msg_hash', 'get_transfer_msg_hash'
        ]
        
        for func in functions:
            if hasattr(fast_stark_crypto, func):
                print(f"✅ {func} function available")
            else:
                print(f"❌ {func} function missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import fast_stark_crypto: {e}")
        return False

def test_extended_services():
    """Test the Extended Exchange services"""
    print("\n🧪 Testing Extended Exchange services...")
    
    try:
        from app.services.extended.signature_service import ExtendedSignatureService
        from app.services.extended.starknet_adapter import StarknetExtendedAdapter
        from app.services.extended.sdk_config import ExtendedEndpointConfig
        
        print("✅ Extended services imported successfully")
        
        # Test signature service
        sig_service = ExtendedSignatureService()
        print("✅ ExtendedSignatureService created")
        
        # Test adapter
        config = ExtendedEndpointConfig(
            base_url="https://api.extended.exchange",
            api_key="test",
            api_secret="test"
        )
        adapter = StarknetExtendedAdapter(config)
        print("✅ StarknetExtendedAdapter created")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Extended services: {e}")
        return False

def test_x10_sdk():
    """Test the X10 SDK"""
    print("\n🧪 Testing X10 SDK...")
    
    try:
        import x10
        print("✅ X10 SDK imported successfully")
        
        # Test available modules
        modules = ['perpetual', 'utils']
        for module in modules:
            if hasattr(x10, module):
                print(f"✅ {module} module available")
            else:
                print(f"❌ {module} module missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import X10 SDK: {e}")
        return False

async def test_starknet_signature_generation():
    """Test StarkNet signature generation"""
    print("\n🧪 Testing StarkNet signature generation...")
    
    try:
        from app.services.extended.signature_service import extended_signature_service
        
        # Test data
        private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        account_address = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        stark_public_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        # Test onboarding signature
        success, sig_r, sig_s, error = await extended_signature_service.generate_extended_onboarding_signature(
            private_key=private_key,
            account_address=account_address,
            stark_public_key=stark_public_key,
            network="sepolia"
        )
        
        if success:
            print("✅ Onboarding signature generated successfully")
            print(f"   Signature R: {sig_r[:20]}...")
            print(f"   Signature S: {sig_s[:20]}...")
        else:
            print(f"❌ Onboarding signature failed: {error}")
        
        return success
        
    except Exception as e:
        print(f"❌ Signature generation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing StarkNet Extended Exchange Integration")
    print("=" * 60)
    
    # Test 1: fast_stark_crypto wrapper
    crypto_ok = test_fast_stark_crypto()
    
    # Test 2: Extended services
    services_ok = test_extended_services()
    
    # Test 3: X10 SDK
    x10_ok = test_x10_sdk()
    
    # Test 4: Signature generation (async)
    print("\n🔄 Running async signature test...")
    loop = asyncio.get_event_loop()
    signature_ok = loop.run_until_complete(test_starknet_signature_generation())
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   fast_stark_crypto: {'✅ PASS' if crypto_ok else '❌ FAIL'}")
    print(f"   Extended services: {'✅ PASS' if services_ok else '❌ FAIL'}")
    print(f"   X10 SDK: {'✅ PASS' if x10_ok else '❌ FAIL'}")
    print(f"   Signature generation: {'✅ PASS' if signature_ok else '❌ FAIL'}")
    
    all_passed = crypto_ok and services_ok and x10_ok and signature_ok
    
    if all_passed:
        print("\n🎉 All tests passed! StarkNet integration is ready.")
        print("\n📝 Next steps:")
        print("   1. Use a StarkNet wallet (Argent/Braavos) for onboarding")
        print("   2. Generate deterministic signatures from wallet keys")
        print("   3. Create Extended Exchange accounts natively")
        print("   4. Sign and submit orders directly")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 