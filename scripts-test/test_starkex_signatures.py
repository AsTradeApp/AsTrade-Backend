#!/usr/bin/env python3
"""
Test script for StarkEx signature generation using the Extended Signature Service
"""
import asyncio
import os
import time
from decimal import Decimal

from app.services.extended.signature_service import extended_signature_service


async def test_starkex_order_signature():
    """Test StarkEx order signature generation"""
    print("Testing StarkEx Order Signature Generation...")
    
    # Test credentials (use your actual credentials)
    private_key = os.getenv("X10_PRIVATE_KEY", "0x6db5a32178b49fea8da102feeef5bf4e1449af13a41b5f850173f109009f00a")
    public_key = os.getenv("X10_PUBLIC_KEY", "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f")
    vault_id = int(os.getenv("X10_VAULT_ID", "500029"))
    
    # Order parameters
    order_params = {
        'market': 'BTC-USD',
        'side': 'BUY',
        'qty': '0.001',
        'price': '95000.0',
        'order_type': 'LIMIT',
        'nonce': int(time.time()),
        'vault_id': vault_id,
        'position_id': vault_id,  # For Extended, position_id often equals vault_id
        'expiry_timestamp': int(time.time()) + 3600,  # 1 hour from now
        'fee_rate': '0.001'  # 0.1% fee
    }
    
    print(f"Order parameters: {order_params}")
    
    # Generate signature
    success, sig_r, sig_s, error = await extended_signature_service.generate_starkex_order_signature(
        private_key=private_key,
        order_params=order_params,
        network="sepolia"
    )
    
    if success:
        print(f"✅ Signature generated successfully!")
        print(f"   R: {sig_r}")
        print(f"   S: {sig_s}")
    else:
        print(f"❌ Signature generation failed: {error}")
    
    return success, sig_r, sig_s


async def test_settlement_object():
    """Test complete settlement object creation"""
    print("\nTesting Settlement Object Creation...")
    
    # Test credentials
    private_key = os.getenv("X10_PRIVATE_KEY", "0x6db5a32178b49fea8da102feeef5bf4e1449af13a41b5f850173f109009f00a")
    public_key = os.getenv("X10_PUBLIC_KEY", "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f")
    vault_id = int(os.getenv("X10_VAULT_ID", "500029"))
    
    # Order parameters
    order_params = {
        'market': 'BTC-USD',
        'side': 'BUY',
        'qty': '0.001',
        'price': '95000.0',
        'order_type': 'LIMIT',
        'nonce': int(time.time()),
        'vault_id': vault_id,
        'position_id': vault_id,
        'expiry_timestamp': int(time.time()) + 3600,
        'fee_rate': '0.001'
    }
    
    # Create settlement object
    success, settlement, error = await extended_signature_service.create_settlement_object(
        private_key=private_key,
        stark_public_key=public_key,
        order_params=order_params,
        collateral_position=str(vault_id),
        network="sepolia"
    )
    
    if success:
        print(f"✅ Settlement object created successfully!")
        print(f"   Settlement: {settlement}")
        
        # Show how it would be used in an API request
        api_order_example = {
            "id": "test-order-123",
            "market": "BTC-USD",
            "type": "LIMIT",
            "side": "BUY",
            "qty": "0.001",
            "price": "95000.0",
            "timeInForce": "GTT",
            "expiryEpochMillis": order_params['expiry_timestamp'] * 1000,
            "fee": "0.001",
            "nonce": str(order_params['nonce']),
            "settlement": settlement,
            "reduceOnly": False,
            "postOnly": True,
            "selfTradeProtectionLevel": "ACCOUNT"
        }
        
        print(f"\n📋 Complete API Order Request:")
        import json
        print(json.dumps(api_order_example, indent=2))
        
    else:
        print(f"❌ Settlement object creation failed: {error}")
    
    return success, settlement


async def main():
    """Main test function"""
    print("=" * 60)
    print("Extended Exchange StarkEx Signature Generation Test")
    print("=" * 60)
    
    # Test signature generation
    sig_success, sig_r, sig_s = await test_starkex_order_signature()
    
    # Test settlement object creation
    settlement_success, settlement = await test_settlement_object()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"✅ Signature Generation: {'PASSED' if sig_success else 'FAILED'}")
    print(f"✅ Settlement Object:    {'PASSED' if settlement_success else 'FAILED'}")
    
    if sig_success and settlement_success:
        print("\n🎉 All tests passed! You can now use these signatures with Extended Exchange.")
        print("\n💡 Next steps:")
        print("   1. Use the settlement object in your order placement API calls")
        print("   2. Make sure to use the correct vault_id and position_id from your account")
        print("   3. Adjust asset IDs if needed for different markets")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main()) 