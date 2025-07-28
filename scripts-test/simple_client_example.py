import asyncio
from decimal import Decimal

from x10.perpetual.accounts import StarkPerpetualAccount
from app.services.extended.sdk_config import ExtendedEndpointConfig
from app.config.extended_config import extended_config
from x10.perpetual.orders import OrderSide
from x10.perpetual.simple_client.simple_trading_client import BlockingTradingClient


async def setup_and_run():
    api_key = "d60627227f58690dad2d3039ff7e4da9"
    public_key = "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f"
    private_key = "0x6db5a32178b49fea8da102feeef5bf4e1449af13a41b5f850173f109009f00a"
    vault = 500029

    # Create custom endpoint config with your API key
    custom_config = ExtendedEndpointConfig(
        base_url=extended_config.TESTNET_BASE_URL,
        onboarding_url=extended_config.TESTNET_ONBOARDING_URL,
        signing_domain=extended_config.TESTNET_SIGNING_DOMAIN_NEW,
        ws_url=extended_config.TESTNET_WS_URL
    )
    
    # Override the headers properties to include your API key
    custom_config._api_key = api_key  # Store the API key
    
    # Monkey patch the headers methods to use our API key
    def custom_headers():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AsTrade/1.0.0 (compatible; MyApp/1.0; +https://extended.exchange)",
            "X-Api-Key": api_key
        }
    
    def custom_ws_headers():
        return {
            "User-Agent": "AsTrade/1.0.0 (compatible; MyApp/1.0; +https://extended.exchange)",
            "X-Api-Key": api_key
        }
    
    # Replace the property methods
    custom_config.__class__.headers = property(lambda self: custom_headers())
    custom_config.__class__.ws_headers = property(lambda self: custom_ws_headers())

    stark_account = StarkPerpetualAccount(
        vault=vault,
        private_key=private_key,
        public_key=public_key,
        api_key=api_key,
    )

    client = BlockingTradingClient(endpoint_config=custom_config, account=stark_account)

    placed_order = await client.create_and_place_order(
        amount_of_synthetic=Decimal("1"),
        price=Decimal("62133.6"),
        market_name="BTC-USD",
        side=OrderSide.BUY,
        post_only=False,
    )

    print(placed_order)

    # await client.cancel_order(order_external_id=placed_order.external_id)


if __name__ == "__main__":
    asyncio.run(main=setup_and_run())