"""Stark trading client service"""
import asyncio
from decimal import Decimal
from typing import Optional, Dict, Any
import structlog
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent.absolute())
sys.path.insert(0, project_root)

from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.configuration import STARKNET_TESTNET_CONFIG
from x10.perpetual.orders import OrderSide
from x10.perpetual.simple_client.simple_trading_client import BlockingTradingClient

logger = structlog.get_logger()


class StarkTradingClientError(Exception):
    """Custom exception for Stark trading client errors"""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


class StarkTradingService:
    """Service for Stark perpetual trading operations"""
    
    def __init__(self):
        """Initialize the Stark trading service"""
        self.client: Optional[BlockingTradingClient] = None
        self.account: Optional[StarkPerpetualAccount] = None
        
        # Store configuration without validation (lazy loading)
        self.api_key = os.getenv("EXTENDED_API_KEY")
        self.public_key = os.getenv("EXTENDED_SECRET_PUBLIC_KE")
        self.private_key = os.getenv("EXTENDED_STARK_PRIVATE_KEY")
        self.vault = os.getenv("EXTENDED_VAULT_ID")  # Store as string initially
        
        logger.info("Stark trading service initialized (not connected)")

    def validate_configuration(self):
        """Validate all required configuration is present"""
        required_env_vars = {
            "EXTENDED_API_KEY": (self.api_key, "API key"),
            "EXTENDED_SECRET_PUBLIC_KE": (self.public_key, "Public key"),
            "EXTENDED_STARK_PRIVATE_KEY": (self.private_key, "Private key"),
            "EXTENDED_VAULT_ID": (self.vault, "Vault ID")
        }
        
        missing_vars = []
        for var_name, (value, description) in required_env_vars.items():
            if value is None:
                missing_vars.append(f"{description} ({var_name})")
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        try:
            self.vault = int(self.vault)
        except (TypeError, ValueError) as e:
            error_msg = f"Invalid EXTENDED_VAULT_ID value: must be an integer"
            logger.error(error_msg)
            raise ConfigurationError(error_msg) from e
    
    async def initialize_client(self) -> BlockingTradingClient:
        """Initialize and return the trading client"""
        try:
            # Validate configuration before proceeding
            self.validate_configuration()
            
            # Create Stark account
            self.account = StarkPerpetualAccount(
                vault=self.vault,
                private_key=self.private_key,
                public_key=self.public_key,
                api_key=self.api_key,
            )
            
            # Create trading client
            self.client = BlockingTradingClient(
                endpoint_config=STARKNET_TESTNET_CONFIG,
                account=self.account
            )
            
            logger.info("Stark trading client initialized successfully", vault=self.vault)
            return self.client
            
        except Exception as e:
            logger.error("Failed to initialize Stark trading client", error=str(e))
            raise StarkTradingClientError(f"Failed to initialize trading client: {str(e)}")
    
    async def create_order(
        self,
        amount_of_synthetic: Decimal,
        price: Decimal,
        market_name: str,
        side: str,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """
        Create and place a trading order
        
        Args:
            amount_of_synthetic: Amount of synthetic asset to trade
            price: Order price
            market_name: Market symbol (e.g., "BTC-USD")
            side: Order side ("BUY" or "SELL")
            post_only: Whether this is a post-only order
            
        Returns:
            Dict containing order information
            
        Raises:
            StarkTradingClientError: If order creation fails
        """
        try:
            if not self.client:
                await self.initialize_client()
            
            # Convert side string to OrderSide enum
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            logger.info(
                "Creating Stark order",
                amount=amount_of_synthetic,
                price=price,
                market=market_name,
                side=side,
                post_only=post_only
            )
            
            placed_order = await self.client.create_and_place_order(
                amount_of_synthetic=amount_of_synthetic,
                price=price,
                market_name=market_name,
                side=order_side,
                post_only=post_only,
            )
            
            logger.info("Stark order created successfully", order_id=placed_order.external_id)
            
            return {
                "external_id": placed_order.external_id,
                "market_name": market_name,
                "side": side,
                "amount": str(amount_of_synthetic),
                "price": str(price),
                "post_only": post_only,
                "status": "placed",
                "order_data": placed_order.__dict__ if hasattr(placed_order, '__dict__') else str(placed_order)
            }
            
        except Exception as e:
            logger.error("Failed to create Stark order", error=str(e))
            raise StarkTradingClientError(f"Failed to create order: {str(e)}")
    
    async def cancel_order(self, order_external_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            order_external_id: External ID of the order to cancel
            
        Returns:
            Dict containing cancellation status
            
        Raises:
            StarkTradingClientError: If order cancellation fails
        """
        try:
            if not self.client:
                await self.initialize_client()
            
            logger.info("Cancelling Stark order", order_id=order_external_id)
            
            result = await self.client.cancel_order(order_external_id=order_external_id)
            
            logger.info("Stark order cancelled successfully", order_id=order_external_id)
            
            return {
                "external_id": order_external_id,
                "status": "cancelled",
                "result": result.__dict__ if hasattr(result, '__dict__') else str(result)
            }
            
        except Exception as e:
            logger.error("Failed to cancel Stark order", error=str(e), order_id=order_external_id)
            raise StarkTradingClientError(f"Failed to cancel order: {str(e)}")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Dict containing account information
        """
        return {
            "vault": self.vault,
            "public_key": self.public_key,
            "api_key": self.api_key[:8] + "..." if self.api_key else None,
            "initialized": self.client is not None
        }


# Create singleton instance
stark_trading_service = StarkTradingService() 