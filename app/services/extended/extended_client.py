"""Extended Exchange Trading Client using x10 library"""
import asyncio
from decimal import Decimal
from typing import Optional, Dict, Any, List
import structlog

from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.configuration import TESTNET_CONFIG, MAINNET_CONFIG
from x10.perpetual.orders import OrderSide
from x10.perpetual.simple_client.simple_trading_client import BlockingTradingClient

from app.config.settings import settings

logger = structlog.get_logger()


class ExtendedTradingClient:
    """Extended Exchange Trading Client using x10 library"""
    
    def __init__(self):
        """Initialize the trading client"""
        self.client: Optional[BlockingTradingClient] = None
        self.account: Optional[StarkPerpetualAccount] = None
        self._initialized = False
        
    def _validate_credentials(self) -> None:
        """Validate that all required credentials are present"""
        required_fields = [
            ("EXTENDED_API_KEY", settings.extended_api_key),
            ("EXTENDED_SECRET_KEY", settings.extended_secret_key),
            ("EXTENDED_STARK_PRIVATE_KEY", settings.extended_stark_private_key),
            ("EXTENDED_VAULT_ID", settings.extended_vault_id)
        ]
        
        missing_fields = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing_fields.append(field_name)
        
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    async def initialize(self) -> None:
        """Initialize the Stark account and trading client"""
        if self._initialized:
            return
            
        try:
            self._validate_credentials()
            
            # Create Stark account
            self.account = StarkPerpetualAccount(
                vault=settings.extended_vault_id,
                private_key=settings.extended_stark_private_key,
                public_key=settings.extended_secret_key,  # Using secret_key as public_key as per example pattern
                api_key=settings.extended_api_key,
            )
            
            # Choose configuration based on environment
            config = TESTNET_CONFIG if settings.extended_environment == "testnet" else MAINNET_CONFIG
            
            # Create trading client
            self.client = await BlockingTradingClient.create(
                endpoint_config=config, 
                account=self.account
            )
            
            self._initialized = True
            logger.info(
                "Extended trading client initialized successfully",
                environment=settings.extended_environment,
                vault_id=settings.extended_vault_id
            )
            
        except Exception as e:
            logger.error("Failed to initialize Extended trading client", error=str(e))
            raise
    
    async def ensure_initialized(self) -> None:
        """Ensure the client is initialized before any operation"""
        if not self._initialized:
            await self.initialize()
    
    async def create_and_place_order(
        self,
        amount_of_synthetic: Decimal,
        price: Decimal,
        market_name: str,
        side: OrderSide,
        post_only: bool = False,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create and place an order
        
        Args:
            amount_of_synthetic: Amount to trade
            price: Price per unit
            market_name: Market symbol (e.g., "BTC-USD")
            side: OrderSide.BUY or OrderSide.SELL
            post_only: Whether this is a post-only order
            external_id: Optional external order ID
            
        Returns:
            Dict containing order information
        """
        await self.ensure_initialized()
        
        try:
            logger.info(
                "Creating and placing order",
                market=market_name,
                amount=str(amount_of_synthetic),
                price=str(price),
                side=side.value,
                post_only=post_only,
                external_id=external_id
            )
            
            placed_order = await self.client.create_and_place_order(
                amount_of_synthetic=amount_of_synthetic,
                price=price,
                market_name=market_name,
                side=side,
                post_only=post_only,
                external_id=external_id or f"order_{asyncio.get_event_loop().time()}"
            )
            
            logger.info("Order placed successfully", order_id=placed_order.external_id)
            
            return {
                "success": True,
                "order": {
                    "external_id": placed_order.external_id,
                    "market_name": market_name,
                    "amount": str(amount_of_synthetic),
                    "price": str(price),
                    "side": side.value,
                    "post_only": post_only,
                    "status": "placed"
                }
            }
            
        except Exception as e:
            logger.error("Failed to place order", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, order_external_id: str) -> Dict[str, Any]:
        """
        Cancel an order by external ID
        
        Args:
            order_external_id: External ID of the order to cancel
            
        Returns:
            Dict containing cancellation result
        """
        await self.ensure_initialized()
        
        try:
            logger.info("Cancelling order", order_id=order_external_id)
            
            await self.client.cancel_order(order_external_id=order_external_id)
            
            logger.info("Order cancelled successfully", order_id=order_external_id)
            
            return {
                "success": True,
                "message": f"Order {order_external_id} cancelled successfully"
            }
            
        except Exception as e:
            logger.error("Failed to cancel order", error=str(e), order_id=order_external_id)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def place_buy_order(
        self,
        market_name: str,
        amount: Decimal,
        price: Decimal,
        post_only: bool = False,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method to place a buy order"""
        return await self.create_and_place_order(
            amount_of_synthetic=amount,
            price=price,
            market_name=market_name,
            side=OrderSide.BUY,
            post_only=post_only,
            external_id=external_id
        )
    
    async def place_sell_order(
        self,
        market_name: str,
        amount: Decimal,
        price: Decimal,
        post_only: bool = False,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method to place a sell order"""
        return await self.create_and_place_order(
            amount_of_synthetic=amount,
            price=price,
            market_name=market_name,
            side=OrderSide.SELL,
            post_only=post_only,
            external_id=external_id
        )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        await self.ensure_initialized()
        
        try:
            return {
                "success": True,
                "account": {
                    "vault_id": settings.extended_vault_id,
                    "environment": settings.extended_environment,
                    "api_key": settings.extended_api_key[:8] + "..." if settings.extended_api_key else None,
                    "initialized": self._initialized
                }
            }
        except Exception as e:
            logger.error("Failed to get account info", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self) -> None:
        """Clean up resources"""
        if self.client:
            try:
                # Note: The x10 client doesn't have an explicit close method in the example
                # If it does in the actual implementation, it should be called here
                pass
            except Exception as e:
                logger.error("Error closing trading client", error=str(e))
        
        self._initialized = False
        logger.info("Extended trading client closed")


# Create singleton instance
extended_trading_client = ExtendedTradingClient()
