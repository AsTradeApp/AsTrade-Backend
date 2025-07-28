import asyncio
from decimal import Decimal

from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.configuration import EndpointConfig
from x10.perpetual.orders import OrderSide
from x10.perpetual.trading_client.trading_client import PerpetualTradingClient

# Create updated TESTNET_CONFIG with correct Starknet Sepolia URLs
CORRECTED_TESTNET_CONFIG = EndpointConfig(
    chain_rpc_url="https://rpc.sepolia.org",
    api_base_url="https://api.starknet.sepolia.extended.exchange/api/v1",
    stream_url="wss://api.starknet.sepolia.extended.exchange/stream.extended.exchange/v1",
    onboarding_url="https://api.starknet.sepolia.extended.exchange",
    signing_domain="starknet.sepolia.extended.exchange",
    collateral_asset_contract="0x0C9165046063B7bCD05C6924Bbe05ed535c140a1",
    asset_operations_contract="0xe42bb60Fab4EA4905832AEbDf0f001c784dA271b",
    collateral_asset_on_chain_id="0x31857064564ed0ff978e687456963cba09c2c6985d8f9300a1de4962fafa054",
    collateral_decimals=6,
)


async def setup_and_run():
    # User account credentials
    api_key = "65e33a7ac37b6e3e21189230eb7a102d"
    public_key = "0x1bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618"
    private_key = "0x6e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4"
    vault = 500073

    # Create Stark account
    stark_account = StarkPerpetualAccount(
        vault=vault,
        private_key=private_key,
        public_key=public_key,
        api_key=api_key,
    )

    # Create PerpetualTradingClient with corrected configuration
    print("Creating PerpetualTradingClient with corrected Starknet Sepolia URLs...")
    root_trading_client = PerpetualTradingClient(
        CORRECTED_TESTNET_CONFIG,
        stark_account,
    )

    print(f"User vault: {vault}")
    print(f"User public key: {public_key}")
    print(f"User private key: {private_key}")
    print(f"Using API URL: {CORRECTED_TESTNET_CONFIG.api_base_url}")

    # Try to claim testing funds if the method exists
    try:
        print("Attempting to claim testing funds...")
        if hasattr(root_trading_client, 'testnet') and hasattr(root_trading_client.testnet, 'claim_testing_funds'):
            claim_response = await root_trading_client.testnet.claim_testing_funds()
            claim_id = claim_response.data.id if claim_response.data else None
            print(f"Claim ID: {claim_id}")

            # Check asset operations
            if claim_id:
                resp = await root_trading_client.account.asset_operations(id=claim_id)
                print(f"Asset Operations: {resp.data}")
        else:
            print("testnet.claim_testing_funds method not available")
    except Exception as e:
        print(f"Error claiming funds: {e}")

    # Get account balance before trading
    try:
        print("Getting account balance...")
        balance = await root_trading_client.account.get_balance()
        print(f"Current balance: {balance}")
    except Exception as e:
        print(f"Error getting balance: {e}")

    # Test order creation
    try:
        print("Creating and placing order...")
        placed_order = await root_trading_client.orders.create_order(
            market_name="BTC-USD",
            side=OrderSide.BUY,
            amount_of_synthetic=Decimal("0.01"),  # Smaller amount for testing
            price=Decimal("62133.6"),
            post_only=False,
        )

        print(f"Order placed: {placed_order}")

        # Cancel the order
        if hasattr(placed_order, 'id'):
            print(f"Cancelling order with ID: {placed_order.id}")
            await root_trading_client.orders.cancel_order(order_id=placed_order.id)
            print("Order cancelled successfully")
        elif hasattr(placed_order, 'external_id'):
            print(f"Cancelling order with external ID: {placed_order.external_id}")
            await root_trading_client.orders.cancel_order(external_id=placed_order.external_id)
            print("Order cancelled successfully")
            
    except Exception as e:
        print(f"Error with order operations: {e}")
        # Try alternative order creation method
        try:
            print("Trying alternative order creation...")
            placed_order = await root_trading_client.place_order(
                market_name="BTC-USD",
                side=OrderSide.BUY,
                amount_of_synthetic=Decimal("0.01"),
                price=Decimal("62133.6"),
                post_only=False,
            )
            print(f"Order placed with alternative method: {placed_order}")
        except Exception as e2:
            print(f"Alternative order creation also failed: {e2}")


if __name__ == "__main__":
    asyncio.run(setup_and_run())