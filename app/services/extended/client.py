"""Extended Exchange API client"""
from typing import Optional, Dict, Any, List
import aiohttp
import structlog
from app.config.extended_config import extended_config
from app.services.extended.mock_data import (
    get_mock_markets,
    get_mock_market_stats,
    get_mock_orderbook,
    get_mock_trades,
    get_mock_candles,
    get_mock_account_balance,
    get_mock_positions,
    get_mock_position_history,
    get_mock_leverage,
    get_mock_fees
)

logger = structlog.get_logger()


class ExtendedExchangeClient:
    """Extended Exchange API client"""
    def __init__(self):
        self.config = extended_config
        self.session = None
        self.mock_enabled = True  # TODO: Get from config

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.config.headers
            )
        return self.session

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Extended Exchange API"""
        if self.mock_enabled:
            # Return mock data based on endpoint
            if endpoint == "/markets":
                return get_mock_markets()
            elif endpoint == "/markets/stats":
                return get_mock_market_stats(params.get("symbol") if params else None)
            elif endpoint == "/markets/orderbook":
                return get_mock_orderbook(params["symbol"], params.get("limit", 100))
            elif endpoint == "/markets/trades":
                return get_mock_trades(params["symbol"], params.get("limit", 100))
            elif endpoint == "/markets/candles":
                return get_mock_candles(
                    params["symbol"],
                    params.get("interval", "1h"),
                    params.get("limit", 100)
                )
            elif endpoint == "/account/balance":
                return get_mock_account_balance()
            elif endpoint == "/positions":
                return get_mock_positions(params.get("symbol") if params else None)
            elif endpoint == "/positions/history":
                return get_mock_position_history()
            elif endpoint == "/account/leverage":
                return get_mock_leverage()
            elif endpoint == "/account/fees":
                return get_mock_fees()
            else:
                raise NotImplementedError(f"Mock endpoint {endpoint} not implemented")

        url = f"{self.config.base_url}{endpoint}"
        session = await self._get_session()

        try:
            async with session.request(
                method,
                url,
                params=params,
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error("API request failed", error=str(e), endpoint=endpoint)
            raise

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets"""
        return await self._make_request("GET", "/markets")

    async def get_market_stats(
        self,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get market statistics"""
        params = {"symbol": symbol} if symbol else None
        return await self._make_request("GET", "/markets/stats", params=params)

    async def get_orderbook(
        self,
        symbol: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get market order book"""
        params = {"symbol": symbol, "limit": limit}
        return await self._make_request("GET", "/markets/orderbook", params=params)

    async def get_trades(
        self,
        symbol: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent market trades"""
        params = {"symbol": symbol, "limit": limit}
        return await self._make_request("GET", "/markets/trades", params=params)

    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get market candle data"""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return await self._make_request("GET", "/markets/candles", params=params)

    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        return await self._make_request("GET", "/account/balance")

    async def get_positions(
        self,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get open positions"""
        params = {"symbol": symbol} if symbol else None
        return await self._make_request("GET", "/positions", params=params)

    async def get_position_history(self) -> List[Dict[str, Any]]:
        """Get position history"""
        return await self._make_request("GET", "/positions/history")

    async def get_leverage(self) -> Dict[str, Any]:
        """Get account leverage settings"""
        return await self._make_request("GET", "/account/leverage")

    async def get_fees(self) -> Dict[str, Any]:
        """Get account fee structure"""
        return await self._make_request("GET", "/account/fees")


# Create singleton instance
extended_client = ExtendedExchangeClient() 