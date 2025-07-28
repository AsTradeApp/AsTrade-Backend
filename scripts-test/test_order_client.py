import asyncio
import logging
import logging.config
import logging.handlers
import os
import time
import json
import aiohttp
from asyncio import run
from decimal import Decimal
from typing import Dict, Any

from dotenv import load_dotenv

from x10.perpetual.accounts import StarkPerpetualAccount
from app.services.extended.sdk_config import TESTNET_CONFIG
from x10.perpetual.orderbook import OrderBook
from x10.perpetual.orders import OrderSide
from x10.perpetual.order_object import create_order_object
from x10.perpetual.simple_client.simple_trading_client import BlockingTradingClient
from x10.perpetual.trading_client import PerpetualTradingClient

# Import the signature service for Extended Exchange compatibility
from app.services.extended.signature_service import extended_signature_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OrderTest")

load_dotenv()

# Use environment variables if available, otherwise fallback to hardcoded values
API_KEY = os.getenv("X10_API_KEY", "d60627227f58690dad2d3039ff7e4da9")
PUBLIC_KEY = os.getenv("X10_PUBLIC_KEY", "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f")
PRIVATE_KEY = os.getenv("X10_PRIVATE_KEY", "0x6db5a32178b49fea8da102feeef5bf4e1449af13a41b5f850173f109009f00a")
VAULT_ID = int(os.getenv("X10_VAULT_ID", "500029"))


async def create_extended_exchange_order(
    market: str,
    side: str,
    qty: str,
    price: str,
    vault_id: int,
    private_key: str,
    public_key: str
):
    """
    Create an order directly for Extended Exchange using their specific signature format
    """
    try:
        import uuid
        
        # Generate order parameters
        order_id = str(uuid.uuid4())
        nonce_int = int(time.time())  # Keep as integer for consistency
        nonce_str = str(nonce_int)    # String version for API
        expiry_timestamp = int(time.time()) + 3600  # 1 hour from now
        expiry_millis = expiry_timestamp * 1000
        
        # Order parameters for Extended Exchange signature service
        # CRITICAL: These must match exactly what Extended Exchange uses for verification
        order_params = {
            'market': market,
            'side': side.upper(),
            'qty': qty,
            'price': price,
            'order_type': 'LIMIT',
            'nonce': nonce_int,  # Use integer for signature generation (as Extended Exchange expects)
            'vault_id': vault_id,
            'position_id': vault_id,
            'expiry_timestamp': expiry_timestamp,  # Use seconds for signature
            'fee_rate': '0.0005'  # Standard fee rate
        }
        
        logger.info(f"Creating Extended Exchange order with params: {order_params}")
        logger.info(f"Signature nonce (int): {nonce_int}, API nonce (str): {nonce_str}")
        
        # Generate signature using Extended Exchange service
        success, settlement, error = await extended_signature_service.create_settlement_object(
            private_key=private_key,
            stark_public_key=public_key,
            order_params=order_params,
            collateral_position=str(vault_id),
            network="sepolia"
        )
        
        if not success:
            raise Exception(f"Failed to generate signature: {error}")
        
        # Create the complete order request for Extended Exchange API
        # CRITICAL: These values must match what Extended Exchange expects for verification
        # Following Extended Exchange API format exactly (not X10 SDK internal format)
        order_request = {
            "id": order_id,
            "market": market,
            "type": "LIMIT",
            "side": side.upper(),
            "qty": qty,  # Extended Exchange API expects string
            "price": price,  # Extended Exchange API expects string
            "timeInForce": "GTT",
            "expiryEpochMillis": expiry_millis,  # Extended Exchange API uses camelCase
            "fee": str(order_params['fee_rate']),  # Extended Exchange API expects string
            "nonce": nonce_str,  # Extended Exchange API expects string
            "settlement": settlement,
            "selfTradeProtectionLevel": "ACCOUNT",
            "postOnly": True,
            "reduceOnly": False
        }
        
        logger.info(f"Created Extended Exchange order: {order_id}")
        logger.info(f"Settlement signature R: {settlement['signature']['r']}")
        logger.info(f"Settlement signature S: {settlement['signature']['s']}")
        
        return True, order_request, ""
        
    except Exception as e:
        error_msg = f"Failed to create Extended Exchange order: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, {}, error_msg


def create_custom_signing_function(private_key_hex: str):
    """
    Create a signing function that uses X10's built-in crypto for proper StarkEx compatibility
    """
    def sign_function(message_hash: int):
        try:
            # Use X10's signing function directly for maximum compatibility
            from x10.utils.starkex import sign
            private_key_int = int(private_key_hex.replace('0x', ''), 16)
            return sign(private_key_int, message_hash)
        except Exception as e:
            logger.error(f"Signing failed: {e}")
            raise e
    
    return sign_function


async def place_order_direct_api(order_request, api_key: str):
    """
    Place an order directly via Extended Exchange API endpoint using a pre-built order request
    """
    try:
        # Extended Exchange API endpoint
        api_url = "https://api.starknet.sepolia.extended.exchange/api/v1/user/order"
        
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }
        
        logger.info(f"Placing order via Extended Exchange direct API...")
        logger.info(f"API URL: {api_url}")
        logger.info(f"Request payload: {json.dumps(order_request, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=order_request, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Order placed successfully via Extended Exchange API!")
                    logger.info(f"Response: {json.dumps(result, indent=2)}")
                    return True, result
                else:
                    logger.error(f"Extended Exchange API request failed with status {response.status}")
                    logger.error(f"Response: {response_text}")
                    return False, {"error": f"HTTP {response.status}: {response_text}"}
                    
    except Exception as e:
        logger.error(f"Error making Extended Exchange API call: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, {"error": str(e)}


async def get_user_vault_id():
    """Get the user's vault ID from their account information"""
    logger.info("Fetching user account information to get vault ID...")
    
    # Create a temporary trading client to get account info
    temp_account = StarkPerpetualAccount(
        vault=0,  # Use 0 as placeholder since we need to get the real vault ID
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        api_key=API_KEY,
    )
    
    temp_client = PerpetualTradingClient(
        endpoint_config=TESTNET_CONFIG,
        stark_account=temp_account,
    )
    
    try:
        # Try to get account info which should contain vault ID
        account_info = await temp_client.account.get_balance()
        logger.info("Account info retrieved successfully")
        logger.info(f"Account info: {account_info.to_pretty_json()}")
        
        # The vault ID might be in account details - let's also try to get account details
        # For now, let's look at what we can get from available endpoints
        
        return None  # We'll extract vault ID from the response
        
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return None


async def setup_and_run():
    logger.info("Setting up Stark account and trading client...")
    
    # Quick test of get_order_msg_hash function to verify it works
    try:
        import fast_stark_crypto
        logger.info("Testing get_order_msg_hash with known test values...")
        
        # Use exact values from test_order_msg_rust_integration.py
        synth_id = "0x4254432d3600000000000000000000"
        collateral_id = "0x31857064564ed0ff978e687456963cba09c2c6985d8f9300a1de4962fafa054"
        test_hash = fast_stark_crypto.get_order_msg_hash(
            position_id=10002,
            base_asset_id=int(synth_id, 16),
            base_amount=1000,
            quote_asset_id=int(collateral_id, 16),
            quote_amount=-43445117,
            fee_asset_id=int(collateral_id, 16),
            fee_amount=21723,
            expiration=1706836137,
            salt=1473459052,
            user_public_key=int("0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f", 16),
            domain_name="Perpetuals",
            domain_version="v0",
            domain_chain_id="SN_SEPOLIA",
            domain_revision="1",
        )
        
        expected_hash = int("0x58454e78c25644cbcab59444736d573f169fb0996dafe1900a05e2ac50567f0", 16)
        logger.info(f"Test hash result: {hex(test_hash)}")
        logger.info(f"Expected hash:    {hex(expected_hash)}")
        logger.info(f"Hash test passed: {test_hash == expected_hash}")
        
    except Exception as e:
        logger.error(f"Hash test failed: {e}")
    
    # First, let's try to get the correct vault ID
    vault_id_from_api = await get_user_vault_id()
    
    # Use the API vault ID if found, otherwise use the configured one
    actual_vault_id = vault_id_from_api if vault_id_from_api else VAULT_ID
    logger.info(f"Using vault ID: {actual_vault_id}")
    
    # Create account with custom signing function that uses X10's crypto
    stark_account = StarkPerpetualAccount(
        vault=actual_vault_id,
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        api_key=API_KEY,
    )
    
    # Override the signing function to use X10's built-in crypto
    stark_account.sign = create_custom_signing_function(PRIVATE_KEY)
    
    logger.info(f"Account created with vault ID: {actual_vault_id}")
    logger.info(f"Using X10's built-in crypto for signing")
    
    trading_client = PerpetualTradingClient(
        endpoint_config=TESTNET_CONFIG,
        stark_account=stark_account,
    )
    
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
            # Create order directly for Extended Exchange using their specific signature format
            success, order_request, error = await create_extended_exchange_order(
                market="BTC-USD",
                side="BUY",
                qty=str(order_amount),
                price=str(order_price),
                vault_id=VAULT_ID,
                private_key=PRIVATE_KEY,
                public_key=PUBLIC_KEY
            )
            
            if not success:
                logger.error(f"Failed to create Extended Exchange order: {error}")
                return
            
            logger.info(f"Extended Exchange order created successfully")
            logger.info(f"Order ID: {order_request['id']}")
            
            # Place the order using Extended Exchange direct API call
            success, api_result = await place_order_direct_api(order_request, API_KEY)
            
            if success:
                logger.info(f"Order placed successfully via Extended Exchange API!")
                logger.info(f"API Response: {api_result}")
                
                # Extract order ID from the response if available
                order_id = api_result.get('id') or api_result.get('orderId') or order_request['id']
                
                # Wait a moment, then try to cancel the order for testing purposes
                await asyncio.sleep(5)
                logger.info(f"Order placement test completed. Order ID: {order_id}")
                logger.info("Note: Cancellation via API would require a separate endpoint call")
            else:
                logger.error(f"Failed to place order via Extended Exchange API: {api_result}")
                return
        
        except Exception as e:
            logger.error(f"Error placing or cancelling order: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    else:
        logger.warning("Could not get best bid/ask prices from orderbook")

    logger.info("Order test completed")


if __name__ == "__main__":
    asyncio.run(setup_and_run())