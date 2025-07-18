from typing import Dict, Any
from app.config.settings import settings


class ExtendedExchangeConfig:
    """Configuration for Extended Exchange API integration"""
    
    # API Endpoints
    TESTNET_BASE_URL = "https://api.testnet.extended.exchange/api/v1"
    MAINNET_BASE_URL = "https://api.extended.exchange/api/v1"
    
    TESTNET_WS_URL = "wss://api.testnet.extended.exchange/stream.extended.exchange/v1"
    MAINNET_WS_URL = "wss://api.extended.exchange/stream.extended.exchange/v1"
    
    @property
    def base_url(self) -> str:
        """Get the appropriate base URL based on environment"""
        if settings.extended_environment == "mainnet":
            return self.MAINNET_BASE_URL
        return self.TESTNET_BASE_URL
    
    @property
    def ws_url(self) -> str:
        """Get the appropriate WebSocket URL based on environment"""
        if settings.extended_environment == "mainnet":
            return self.MAINNET_WS_URL
        return self.TESTNET_WS_URL
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get the default headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if settings.extended_api_key:
            headers["X-Api-Key"] = settings.extended_api_key
            
        return headers
    
    # Rate Limits
    STANDARD_RATE_LIMIT = {
        "requests": 1000,
        "period": 60  # seconds
    }
    
    MARKET_MAKER_RATE_LIMIT = {
        "requests": 60000,
        "period": 300  # 5 minutes
    }
    
    # WebSocket Channels
    WS_CHANNELS = {
        "orderbook": "orderbook.{symbol}",
        "trades": "trades.{symbol}",
        "candles": "candles.{symbol}.{interval}",
        "funding": "funding.{symbol}",
        "account": "account",
        "orders": "orders",
        "positions": "positions"
    }
    
    # Order Types
    ORDER_TYPES = ["limit", "market", "stop_limit", "stop_market", "twap"]
    
    # Order Sides
    ORDER_SIDES = ["buy", "sell"]
    
    # Time in Force
    TIME_IN_FORCE = ["gtc", "ioc", "fok"]
    
    # Position Modes
    POSITION_MODES = ["one_way", "hedge"]
    
    # Available Markets (will be fetched dynamically)
    DEFAULT_MARKETS = [
        "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "WIF-USD",
        "PEPE-USD", "ARB-USD", "OP-USD", "AVAX-USD", "LINK-USD"
    ]
    
    # Leverage Limits
    MAX_LEVERAGE = {
        "BTC-USD": 20,
        "ETH-USD": 20,
        "SOL-USD": 15,
        "default": 10
    }
    
    # Minimum Order Sizes (in USD)
    MIN_ORDER_SIZE = {
        "BTC-USD": 5.0,
        "ETH-USD": 5.0,
        "SOL-USD": 5.0,
        "default": 5.0
    }


# Global configuration instance
extended_config = ExtendedExchangeConfig() 