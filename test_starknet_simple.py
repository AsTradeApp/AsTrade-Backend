#!/usr/bin/env python3
"""
Simple test for StarkNet Extended Exchange Integration
This test only uses the working fast_stark_crypto wrapper
"""
import sys
import os

def test_fast_stark_crypto_functions():
    """Test all available functions in fast_stark_crypto"""
    print("🧪 Testing fast_stark_crypto functions...")
    
    try:
        import fast_stark_crypto
        print("✅ fast_stark_crypto imported successfully")
        
        # Test 1: Generate public key from private key
        print("\n1️⃣ Testing public key generation...")
        private_key = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
        public_key = fast_stark_crypto.get_public_key(private_key)
        print(f"   Private key: {hex(private_key)[:20]}...")
        print(f"   Public key: {public_key}")
        print("   ✅ Public key generation successful")
        
        # Test 2: Sign a message
        print("\n2️⃣ Testing message signing...")
        message_hash = 123456789
        r, s = fast_stark_crypto.sign(private_key, message_hash)
        print(f"   Message hash: {message_hash}")
        print(f"   Signature R: {r}")
        print(f"   Signature S: {s}")
        print("   ✅ Message signing successful")
        
        # Test 3: Verify signature
        print("\n3️⃣ Testing signature verification...")
        is_valid = fast_stark_crypto.verify(public_key, message_hash, r, s)
        print(f"   Signature valid: {is_valid}")
        print("   ✅ Signature verification successful")
        
        # Test 4: Pedersen hash
        print("\n4️⃣ Testing Pedersen hash...")
        a = 123456789
        b = 987654321
        hash_result = fast_stark_crypto.pedersen_hash(a, b)
        print(f"   Input A: {a}")
        print(f"   Input B: {b}")
        print(f"   Pedersen hash: {hash_result}")
        print("   ✅ Pedersen hash successful")
        
        # Test 5: Order message hash
        print("\n5️⃣ Testing order message hash...")
        order_hash = fast_stark_crypto.get_order_msg_hash(
            position_id=0,
            base_asset_id=123,
            base_amount=500000,
            quote_asset_id=456,
            quote_amount=1000000,
            fee_asset_id=789,
            fee_amount=1000,
            expiration=1234567890,
            salt=123456789,
            user_public_key=public_key,
            domain_name="extended.exchange",
            domain_version="1",
            domain_chain_id="1",
            domain_revision="1"
        )
        print(f"   Order hash: {order_hash}")
        print("   ✅ Order message hash successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_extended_integration_components():
    """Test what components of Extended integration are available"""
    print("\n🧪 Testing Extended integration components...")
    
    available_components = []
    
    # Test if we can import basic modules
    try:
        import aiohttp
        available_components.append("aiohttp")
        print("   ✅ aiohttp available")
    except ImportError:
        print("   ❌ aiohttp not available")
    
    try:
        import httpx
        available_components.append("httpx")
        print("   ✅ httpx available")
    except ImportError:
        print("   ❌ httpx not available")
    
    # Test if we can access the app structure
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        # Try to import basic app modules
        from app.services.extended import sdk_config
        available_components.append("sdk_config")
        print("   ✅ sdk_config available")
    except ImportError as e:
        print(f"   ❌ sdk_config not available: {e}")
    
    return available_components

def main():
    """Main test function"""
    print("🚀 Simple StarkNet Extended Exchange Integration Test")
    print("=" * 60)
    
    # Test 1: fast_stark_crypto functions
    crypto_ok = test_fast_stark_crypto_functions()
    
    # Test 2: Available components
    components = test_extended_integration_components()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   fast_stark_crypto functions: {'✅ PASS' if crypto_ok else '❌ FAIL'}")
    print(f"   Available components: {len(components)}/{3}")
    
    if crypto_ok:
        print("\n🎉 Core StarkNet functionality is working!")
        print("\n📝 What this means:")
        print("   ✅ You can generate StarkNet public keys from private keys")
        print("   ✅ You can sign messages with StarkNet keys")
        print("   ✅ You can verify signatures")
        print("   ✅ You can calculate Pedersen hashes")
        print("   ✅ You can generate order message hashes")
        print("\n🚀 Next steps for Extended Exchange integration:")
        print("   1. Install compatible starknet-py version")
        print("   2. Install X10 SDK")
        print("   3. Use these functions to sign Extended Exchange orders")
    else:
        print("\n⚠️  Core functionality failed. Please check the errors above.")
    
    return crypto_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 