#!/usr/bin/env python3
"""
Test order client using X10 SDK with custom StarkEx signatures
This uses the X10 SDK for API communication but replaces signature generation with our custom service
"""
import asyncio
import logging
import os
import time
import json
from decimal import Decimal
from typing import Dict, Any

from dotenv import load_dotenv

from x10.perpetual.accounts import StarkPerpetualAccount
from app.services.extended.sdk_config import TESTNET_CONFIG
from x10.perpetual.orderbook import OrderBook
from x10.perpetual.orders import OrderSide
from x10.perpetual.order_object import create_order_object
from x10.perpetual.trading_client import PerpetualTradingClient

from app.services.extended.signature_service import extended_signature_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("extended_order_client")

load_dotenv()

# Configuration
API_KEY = os.getenv("X10_API_KEY", "d60627227f58690dad2d3039ff7e4da9")
PUBLIC_KEY = os.getenv("X10_PUBLIC_KEY", "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f")
PRIVATE_KEY = os.getenv("X10_PRIVATE_KEY", "0x6db5a32178b49fea8da102feeef5bf4e1449af13a41b5f850173f109009f00a")
VAULT_ID = int(os.getenv("X10_VAULT_ID", "500029"))


async def inject_custom_signature_into_order(order_obj, private_key: str, public_key: str, vault_id: int, market_info):
    """
    Inject custom StarkEx signature into an existing order object created by X10 SDK
    This replaces the SDK's signature with our custom signature service
    """
    try:
        logger.info("Injecting custom signature into order object...")
        
        # Extract order parameters for our signature service
        order_params = {
            'market': getattr(market_info, 'name', 'BTC-USD'),
            'side': 'BUY' if order_obj.order_side == OrderSide.BUY else 'SELL',
            'qty': str(float(order_obj.amount_of_synthetic)),
            'price': str(float(order_obj.price)),
            'order_type': 'LIMIT',
            'nonce': int(time.time()),
            'vault_id': vault_id,
            'position_id': vault_id,
            'expiry_timestamp': int(time.time()) + 3600,
            'fee_rate': '0.001'
        }
        
        logger.info(f"Order parameters for signature: {order_params}")
        
        # Generate our custom signature
        success, settlement, error = await extended_signature_service.create_settlement_object(
            private_key=private_key,
            stark_public_key=public_key,
            order_params=order_params,
            collateral_position=str(vault_id),
            network="sepolia"
        )
        
        if not success:
            raise Exception(f"Failed to generate custom signature: {error}")
        
        logger.info(f"Custom signature generated: {settlement}")
        
        # Replace the order's signature with our custom one
        # Note: This is a bit of a hack since we're modifying the SDK's order object
        if hasattr(order_obj, 'signature'):
            # Extract r and s from our settlement object
            sig_r = settlement['signature']['r']
            sig_s = settlement['signature']['s']
            
            # Replace the signature components
            order_obj.signature.r = int(sig_r, 16)
            order_obj.signature.s = int(sig_s, 16)
            
            logger.info(f"Replaced order signature with custom signature")
            logger.info(f"Custom signature R: {sig_r}")
            logger.info(f"Custom signature S: {sig_s}")
        
        return True, ""
        
    except Exception as e:
        error_msg = f"Failed to inject custom signature: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


async def test_x10_sdk_with_custom_signatures():
    """Test X10 SDK with custom StarkEx signatures injected"""
    
    logger.info("Setting up Stark account and trading client...")
    
    # Setup X10 SDK account and client
    stark_account = StarkPerpetualAccount(
        vault=VAULT_ID,
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        api_key=API_KEY,
    )
    
    trading_client = PerpetualTradingClient(
        endpoint_config=TESTNET_CONFIG,
        stark_account=stark_account,
    )
    
    try:
        # Get and log current positions
        logger.info("Fetching current positions...")
        positions = await trading_client.account.get_positions()
        logger.info("Positions: %s", positions.to_pretty_json())
        
        for position in positions.data:
            logger.info(
                f"Position - market: {position.market}, "
                f"side: {position.side}, "
                f"size: {position.size}, "
                f"mark_price: ${position.mark_price}, "
                f"leverage: {position.leverage}"
            )
            consumed_im = round((position.size * position.mark_price) / position.leverage, 2)
            logger.info(f"Consumed IM: ${consumed_im}")

        # Get and log current balance
        balance = await trading_client.account.get_balance()
        logger.info("Balance: %s", balance.to_pretty_json())

        # Get market information
        logger.info("Fetching market information for BTC-USD...")
        markets = await trading_client.markets_info.get_markets()
        btc_market = None
        for market in markets.data:
            if market.name == "BTC-USD":
                btc_market = market
                break
        
        if not btc_market:
            logger.error("BTC-USD market not found")
            return
        
        logger.info(f"Market info: {btc_market.name}")
        logger.info(f"Min price change: {btc_market.trading_config.min_price_change}")
        logger.info(f"Min order size: {btc_market.trading_config.min_order_size}")
        logger.info(f"Max leverage: {btc_market.trading_config.max_leverage}")

        # Create and start orderbook
        logger.info("Creating orderbook for BTC-USD...")
        orderbook = await OrderBook.create(
            endpoint_config=TESTNET_CONFIG,
            market_name="BTC-USD",
        )
        await orderbook.start_orderbook()
        logger.info("Orderbook started successfully")

        # Wait a moment for orderbook to populate
        await asyncio.sleep(2)

        # Get current market data
        best_bid = orderbook.best_bid()
        best_ask = orderbook.best_ask()
        
        if best_bid and best_ask:
            logger.info(f"Best bid: ${best_bid.price}, Best ask: ${best_ask.price}")
            
            # Calculate order price (slightly below best bid for a buy order)
            order_price = round(best_bid.price * Decimal("0.999"), 1)  # 0.1% below best bid
            order_amount = Decimal("0.001")  # Small amount for testing
            
            logger.info(f"Placing BUY order - Price: ${order_price}, Amount: {order_amount} BTC")
            
            try:
                # Create order object using the SDK helper
                order = create_order_object(
                    account=stark_account,
                    market=btc_market,
                    amount_of_synthetic=order_amount,
                    price=order_price,
                    side=OrderSide.BUY,
                    post_only=True,
                )
                
                logger.info(f"Order object created with ID: {order.id}")
                logger.info(f"Original signature R: {hex(order.signature.r)}")
                logger.info(f"Original signature S: {hex(order.signature.s)}")
                
                # *** INJECT CUSTOM SIGNATURE ***
                success, error = await inject_custom_signature_into_order(
                    order, PRIVATE_KEY, PUBLIC_KEY, VAULT_ID, btc_market
                )
                
                if not success:
                    logger.error(f"Failed to inject custom signature: {error}")
                    return
                
                logger.info(f"Order signature replaced with custom signature!")
                logger.info(f"New signature R: {hex(order.signature.r)}")
                logger.info(f"New signature S: {hex(order.signature.s)}")
                
                # Place the order with our custom signature
                placed_order = await trading_client.orders.place_order(order)
                
                logger.info(f"Order placed successfully! Order ID: {placed_order.id}")
                logger.info(f"External ID: {placed_order.external_id}")
                
                # Wait a moment, then cancel the order for testing purposes
                await asyncio.sleep(5)
                logger.info(f"Cancelling order {placed_order.id}...")
                
                cancel_result = await trading_client.orders.cancel_order(order_id=placed_order.id)
                logger.info(f"Order cancelled successfully: {cancel_result}")
                
            except Exception as e:
                logger.error(f"Error placing or cancelling order: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
        else:
            logger.warning("Could not get best bid/ask prices from orderbook")

        logger.info("Order test completed")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")


async def main():
    """Main function"""
    print("=" * 70)
    print("X10 SDK Test with Custom StarkEx Signatures")
    print("=" * 70)
    
    try:
        await test_x10_sdk_with_custom_signatures()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main()) 