"""Stark trading client service"""
import asyncio
from decimal import Decimal
from typing import Optional, Dict, Any, List
import structlog
import os
import sys
from pathlib import Path
import threading
import aiohttp
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the project root
    project_root = Path(__file__).parent.parent.parent.absolute()
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  Environment file {env_file} not found")
except ImportError:
    print("⚠️  python-dotenv not installed, environment variables must be set manually")

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


class StarkTradingService:
    """Service for Stark perpetual trading operations"""
    
    def __init__(self):
        """Initialize the Stark trading service"""
        self.client: Optional[BlockingTradingClient] = None
        self.account: Optional[StarkPerpetualAccount] = None
        self._initialization_lock = threading.Lock()
        self._is_initializing = False
        
        # Load configuration from environment variables with proper error handling
        self.api_key = os.getenv("EXTENDED_API_KEY")
        self.public_key = os.getenv("EXTENDED_SECRET_PUBLIC_KEY") 
        self.private_key = os.getenv("EXTENDED_STARK_PRIVATE_KEY")
        
        # Handle vault ID with proper error checking
        vault_id = os.getenv("EXTENDED_VAULT_ID")
        if vault_id is None:
            logger.warning("EXTENDED_VAULT_ID environment variable not set, using default value 0")
            self.vault = 0
        else:
            try:
                self.vault = int(vault_id)
            except ValueError:
                logger.error("Invalid EXTENDED_VAULT_ID value, must be an integer", vault_id=vault_id)
                raise StarkTradingClientError(f"Invalid EXTENDED_VAULT_ID value: {vault_id}")
        
        # Validate that all required environment variables are set
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that all required environment variables are set"""
        missing_vars = []
        
        if not self.api_key:
            missing_vars.append("EXTENDED_API_KEY")
        if not self.public_key:
            missing_vars.append("EXTENDED_SECRET_PUBLIC_KEY")
        if not self.private_key:
            missing_vars.append("EXTENDED_STARK_PRIVATE_KEY")
            
        if missing_vars:
            logger.error("Missing required environment variables", missing_vars=missing_vars)
            raise StarkTradingClientError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please set these variables before using the Stark trading service."
            )
        
        logger.info("Stark trading service configuration validated successfully", vault=self.vault)
    
    async def initialize_client(self) -> BlockingTradingClient:
        """Initialize and return the trading client"""
        # Check if already initialized
        if self.client is not None:
            return self.client
            
        # Use lock to prevent concurrent initialization
        with self._initialization_lock:
            # Double-check after acquiring lock
            if self.client is not None:
                return self.client
                
            if self._is_initializing:
                # Another thread is initializing, wait a bit and check again
                import time
                time.sleep(0.1)
                if self.client is not None:
                    return self.client
                else:
                    raise StarkTradingClientError("Client initialization in progress, please try again")
            
            try:
                self._is_initializing = True
                logger.info("Initializing Stark trading client", vault=self.vault)
                
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
                self.client = None  # Reset on failure
                raise StarkTradingClientError(f"Failed to initialize trading client: {str(e)}")
            finally:
                self._is_initializing = False
    
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
            # Ensure client is initialized
            if not self.client:
                await self.initialize_client()
            
            if not self.client:
                raise StarkTradingClientError("Failed to initialize trading client")
            
            # Validate and format inputs
            if amount_of_synthetic <= 0:
                raise StarkTradingClientError("Amount must be greater than 0")
            if price <= 0:
                raise StarkTradingClientError("Price must be greater than 0")
            
            # Ensure proper precision for Stark API
            # Round price to integer for compatibility
            formatted_price = Decimal(str(int(price)))
            
            # Market-specific precision for amount
            precision_map = {
                'BTC-USD': Decimal('0.0001'),  # 4 decimal places
                'ETH-USD': Decimal('0.01'),    # 2 decimal places
                'STRK-USD': Decimal('0.1'),    # 1 decimal place
                'MATIC-USD': Decimal('1'),     # 0 decimal places
            }
            
            # Get precision for the market, default to BTC precision
            precision = precision_map.get(market_name, Decimal('0.0001'))
            formatted_amount = amount_of_synthetic.quantize(precision)
            
            logger.info(
                "Formatted order amounts",
                original_amount=amount_of_synthetic,
                formatted_amount=formatted_amount,
                market=market_name,
                precision=precision
            )
            
            # Convert side string to OrderSide enum
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            logger.info(
                "Creating Stark order",
                amount=formatted_amount,
                price=formatted_price,
                market=market_name,
                side=side,
                post_only=post_only
            )
            
            placed_order = await self.client.create_and_place_order(
                amount_of_synthetic=formatted_amount,
                price=formatted_price,
                market_name=market_name,
                side=order_side,
                post_only=post_only,
            )
            
            logger.info("Stark order created successfully", order_id=placed_order.external_id)
            
            return {
                "external_id": placed_order.external_id,
                "market_name": market_name,
                "side": side,
                "amount": str(formatted_amount),
                "price": str(formatted_price),
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
            # Ensure client is initialized
            if not self.client:
                await self.initialize_client()
            
            if not self.client:
                raise StarkTradingClientError("Failed to initialize trading client")
            
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
    
    async def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user positions from Stark API
        
        Args:
            market: Optional market filter (e.g., "BTC-USD")
            
        Returns:
            List of position data
            
        Raises:
            StarkTradingClientError: If API call fails
        """
        try:
            # Ensure client is initialized
            if not self.client:
                await self.initialize_client()
            
            if not self.client:
                raise StarkTradingClientError("Failed to initialize trading client")
            
            # Build URL with optional market parameter
            url = "https://api.starknet.sepolia.extended.exchange/api/v1/user/positions"
            if market:
                url += f"?market={market}"
            
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            logger.info("Fetching positions from Stark API", url=url, market=market, market_type=type(market))
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Stark API error", status=response.status, error=error_text)
                        raise StarkTradingClientError(f"API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    if data.get("status") != "OK":
                        logger.error("Stark API returned error status", data=data)
                        raise StarkTradingClientError(f"API returned error: {data}")
                    
                    positions = data.get("data", [])
                    logger.info("Successfully fetched positions", count=len(positions))
                    
                    return positions
                    
        except aiohttp.ClientError as e:
            logger.error("Network error fetching positions", error=str(e))
            raise StarkTradingClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Failed to fetch positions", error=str(e))
            raise StarkTradingClientError(f"Failed to fetch positions: {str(e)}")
    
    async def get_orders(self, market: Optional[str] = None, order_type: Optional[str] = None, side: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user orders from Stark API
        
        Args:
            market: Optional market filter (e.g., "BTC-USD")
            type: Optional order type filter (e.g., "LIMIT", "CONDITIONAL", "TPSL")
            side: Optional order side filter (e.g., "BUY", "SELL")
            
        Returns:
            List of order data
            
        Raises:
            StarkTradingClientError: If API call fails
        """
        try:
            # Ensure client is initialized
            if not self.client:
                await self.initialize_client()
            
            if not self.client:
                raise StarkTradingClientError("Failed to initialize trading client")
            
            # Build URL with optional parameters
            url = "https://api.starknet.sepolia.extended.exchange/api/v1/user/orders"
            params = []
            
            if market:
                params.append(f"market={market}")
            if order_type:
                params.append(f"type={order_type}")
            if side:
                params.append(f"side={side}")
            
            if params:
                url += "?" + "&".join(params)
            
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            logger.info("Fetching orders from Stark API", url=url, market=market, market_type=type(market), order_type=order_type)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Stark API error", status=response.status, error=error_text)
                        raise StarkTradingClientError(f"API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    if data.get("status") != "OK":
                        logger.error("Stark API returned error status", data=data)
                        raise StarkTradingClientError(f"API returned error: {data}")
                    
                    orders = data.get("data", [])
                    logger.info("Successfully fetched orders", count=len(orders))
                    
                    return orders
                    
        except aiohttp.ClientError as e:
            logger.error("Network error fetching orders", error=str(e))
            raise StarkTradingClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Failed to fetch orders", error=str(e))
            raise StarkTradingClientError(f"Failed to fetch orders: {str(e)}")
    
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