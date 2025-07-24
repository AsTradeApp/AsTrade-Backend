"""Extended Exchange API client"""
import os
import aiohttp
import structlog
from typing import Optional, Dict, Any, List

from app.services.extended.mock_data import (
    get_mock_markets,
    get_mock_market_stats,
    get_mock_orderbook,
    get_mock_account_balance,
    get_mock_positions
)

logger = structlog.get_logger()


class ExtendedExchangeClient:
    """Extended Exchange API client"""
    
    def __init__(self):
        """Initialize client"""
        self.base_url = os.getenv("EXTENDED_API_URL", "https://api.extended.io")
        self.api_key = os.getenv("EXTENDED_API_KEY")
        self.secret_key = os.getenv("EXTENDED_SECRET_KEY")
        self.environment = os.getenv("EXTENDED_ENVIRONMENT", "testnet")
        self.is_mock = os.getenv("EXTENDED_MOCK_ENABLED", "true").lower() == "true"
        self.session = None
        
    async def connect(self):
        """Create HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }
            )
            logger.info("Connected to Extended Exchange API", base_url=self.base_url)
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from Extended Exchange API")
    
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets"""
        if self.is_mock:
            return get_mock_markets()
            
        async with self.session.get("/v1/markets") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_market_stats(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get market statistics"""
        if self.is_mock:
            return get_mock_market_stats(symbol)
            
        params = {"symbol": symbol} if symbol else {}
        async with self.session.get("/v1/markets/stats", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get market order book"""
        if self.is_mock:
            return get_mock_orderbook(symbol, limit)
            
        params = {"symbol": symbol, "limit": limit}
        async with self.session.get("/v1/markets/orderbook", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        if self.is_mock:
            return get_mock_account_balance()
            
        async with self.session.get("/v1/account/balance") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get positions"""
        if self.is_mock:
            return get_mock_positions(symbol)
            
        params = {"symbol": symbol} if symbol else {}
        async with self.session.get("/v1/positions", params=params) as response:
            response.raise_for_status()
            return await response.json()


# Create singleton instance
extended_client = ExtendedExchangeClient() 