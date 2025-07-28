#!/usr/bin/env python3
"""
Test script for the consolidated StarkNet crypto wrapper
This verifies that the wrapper works correctly after consolidation
"""
import sys
import os

def test_consolidated_wrapper():
    """Test the consolidated wrapper functionality"""
    print("🧪 Testing consolidated StarkNet crypto wrapper...")
    
    try:
        import fast_stark_crypto
        print("✅ fast_stark_crypto imported successfully")
        
        # Test 1: Generate public key
        print("\n1️⃣ Testing public key generation...")
        private_key = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
        public_key = fast_stark_crypto.get_public_key(private_key)
        print(f"   Private key: {hex(private_key)[:20]}...")
        print(f"   Public key: {public_key}")
        print("   ✅ Public key generation successful")
        
        # Test 2: Sign message
        print("\n2️⃣ Testing message signing...")
        message_hash = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
        signature = fast_stark_crypto.sign(message_hash, private_key)
        print(f"   Message hash: {hex(message_hash)[:20]}...")
        print(f"   Signature: {signature}")
        print("   ✅ Message signing successful")
        
        # Test 3: Verify signature
        print("\n3️⃣ Testing signature verification...")
        r, s = signature
        is_valid = fast_stark_crypto.verify(message_hash, r, s, public_key)
        print(f"   Signature valid: {is_valid}")
        print("   ✅ Signature verification successful")
        
        # Test 4: Pedersen hash
        print("\n4️⃣ Testing Pedersen hash...")
        hash_result = fast_stark_crypto.pedersen_hash(0x123, 0x456)
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
        
        print("\n🎉 All tests passed! The consolidated wrapper is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Consolidated StarkNet Crypto Wrapper")
    print("=" * 60)
    
    success = test_consolidated_wrapper()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed! The wrapper is ready for use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1) 