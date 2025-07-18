import asyncio
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException

from app.config.extended_config import extended_config
from app.config.settings import settings
from app.models.responses import ErrorDetail


class ExtendedExchangeClient:
    """Extended Exchange API client with async support"""
    
    def __init__(self):
        self.base_url = extended_config.base_url
        self.headers = extended_config.headers.copy()
        self.session: Optional[httpx.AsyncClient] = None
        self._use_mock_data = not settings.extended_api_key or settings.extended_api_key == "your-extended-api-key-here"
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Initialize the HTTP session"""
        if not self._use_mock_data and self.session is None:
            timeout = httpx.Timeout(30.0, connect=5.0)
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
            
            self.session = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=timeout,
                limits=limits
            )
    
    async def disconnect(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    def _get_mock_markets(self) -> List[Dict[str, Any]]:
        """Generate mock market data"""
        markets = [
            {
                "symbol": "BTC-USD",
                "display_name": "Bitcoin / USD",
                "base_asset": "BTC",
                "quote_asset": "USD",
                "status": "active",
                "tick_size": "0.1",
                "step_size": "0.001",
                "min_order_size": "0.001",
                "max_order_size": "100.0",
                "maker_fee": "0.0002",
                "taker_fee": "0.0005",
                "funding_interval": 8,
                "max_leverage": 20,
                "is_active": True
            },
            {
                "symbol": "ETH-USD",
                "display_name": "Ethereum / USD",
                "base_asset": "ETH",
                "quote_asset": "USD",
                "status": "active",
                "tick_size": "0.01",
                "step_size": "0.01",
                "min_order_size": "0.01",
                "max_order_size": "1000.0",
                "maker_fee": "0.0002",
                "taker_fee": "0.0005",
                "funding_interval": 8,
                "max_leverage": 20,
                "is_active": True
            },
            {
                "symbol": "SOL-USD",
                "display_name": "Solana / USD",
                "base_asset": "SOL",
                "quote_asset": "USD",
                "status": "active",
                "tick_size": "0.01",
                "step_size": "0.1",
                "min_order_size": "0.1",
                "max_order_size": "10000.0",
                "maker_fee": "0.0002",
                "taker_fee": "0.0005",
                "funding_interval": 8,
                "max_leverage": 15,
                "is_active": True
            }
        ]
        return markets
    
    def _get_mock_market_stats(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Generate mock market statistics"""
        base_time = datetime.utcnow()
        stats_data = {
            "BTC-USD": {
                "symbol": "BTC-USD",
                "last_price": "95420.5",
                "price_change": "1250.3",
                "price_change_percent": "1.33",
                "high_24h": "96100.0",
                "low_24h": "93800.2",
                "volume_24h": "12500.75",
                "volume_usd_24h": "1192450000.50",
                "open_interest": "285000000.0",
                "funding_rate": "0.0001",
                "next_funding_time": (base_time + timedelta(hours=2)).isoformat(),
                "mark_price": "95425.1",
                "index_price": "95422.8"
            },
            "ETH-USD": {
                "symbol": "ETH-USD",
                "last_price": "3456.78",
                "price_change": "89.12",
                "price_change_percent": "2.64",
                "high_24h": "3500.00",
                "low_24h": "3350.25",
                "volume_24h": "45000.50",
                "volume_usd_24h": "155552250.75",
                "open_interest": "125000000.0",
                "funding_rate": "0.00015",
                "next_funding_time": (base_time + timedelta(hours=2)).isoformat(),
                "mark_price": "3457.22",
                "index_price": "3456.95"
            },
            "SOL-USD": {
                "symbol": "SOL-USD",
                "last_price": "185.45",
                "price_change": "12.85",
                "price_change_percent": "7.44",
                "high_24h": "188.90",
                "low_24h": "170.15",
                "volume_24h": "750000.25",
                "volume_usd_24h": "139087546.25",
                "open_interest": "45000000.0",
                "funding_rate": "0.0002",
                "next_funding_time": (base_time + timedelta(hours=2)).isoformat(),
                "mark_price": "185.52",
                "index_price": "185.48"
            }
        }
        
        if symbol:
            return stats_data.get(symbol, {})
        return list(stats_data.values())
    
    def _get_mock_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Generate mock order book data"""
        # Generate realistic order book based on symbol
        base_price = 95420.5 if symbol == "BTC-USD" else 3456.78 if symbol == "ETH-USD" else 185.45
        
        bids = []
        asks = []
        
        # Generate bids (buy orders) - decreasing prices
        for i in range(min(limit, 20)):
            price = base_price - (i + 1) * (base_price * 0.0001)
            size = round(0.1 + (i * 0.05), 3)
            bids.append({
                "price": f"{price:.2f}",
                "size": f"{size}",
                "num_orders": i + 1
            })
        
        # Generate asks (sell orders) - increasing prices
        for i in range(min(limit, 20)):
            price = base_price + (i + 1) * (base_price * 0.0001)
            size = round(0.1 + (i * 0.05), 3)
            asks.append({
                "price": f"{price:.2f}",
                "size": f"{size}",
                "num_orders": i + 1
            })
        
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.utcnow().isoformat(),
            "sequence": int(time.time())
        }
    
    def _get_mock_trades(self, symbol: str, limit: int = 100, cursor: Optional[int] = None) -> Dict[str, Any]:
        """Generate mock trades data"""
        base_price = 95420.5 if symbol == "BTC-USD" else 3456.78 if symbol == "ETH-USD" else 185.45
        
        trades = []
        base_time = datetime.utcnow()
        
        for i in range(min(limit, 50)):
            price_variance = (base_price * 0.001) * (0.5 - (i % 10) / 10)
            price = base_price + price_variance
            size = round(0.01 + (i % 5) * 0.1, 3)
            side = "buy" if i % 2 == 0 else "sell"
            
            trades.append({
                "id": f"trade_{int(time.time())}_{i}",
                "symbol": symbol,
                "price": f"{price:.2f}",
                "size": f"{size}",
                "side": side,
                "timestamp": (base_time - timedelta(minutes=i)).isoformat(),
                "liquidation": False
            })
        
        return {
            "data": trades,
            "pagination": {
                "cursor": cursor or int(time.time()),
                "count": len(trades),
                "has_next": len(trades) == limit,
                "has_previous": cursor is not None
            }
        }
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC signature for authenticated requests"""
        if not settings.extended_secret_key:
            raise HTTPException(status_code=401, detail="Secret key not configured")
            
        message = f"{timestamp}{method.upper()}{path}{body}"
        signature = hmac.new(
            settings.extended_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_auth_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Get authentication headers for private endpoints"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, path, body)
        
        auth_headers = {
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }
        
        return auth_headers
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auth_required: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to Extended Exchange API"""
        if self._use_mock_data:
            # Return mock data instead of making real API calls
            if path == "/markets":
                return {"data": self._get_mock_markets()}
            elif path.startswith("/markets/") and path.endswith("/stats"):
                symbol = path.split("/")[2]
                return {"data": self._get_mock_market_stats(symbol)}
            elif "/stats" in path and not path.endswith("/stats"):
                return {"data": self._get_mock_market_stats()}
            elif "/orderbook" in path:
                symbol = path.split("/")[2]
                limit = params.get("limit", 100) if params else 100
                return {"data": self._get_mock_orderbook(symbol, limit)}
            elif "/trades" in path:
                symbol = path.split("/")[2]
                limit = params.get("limit", 100) if params else 100
                cursor = params.get("cursor") if params else None
                return self._get_mock_trades(symbol, limit, cursor)
            else:
                return {"data": {"message": f"Mock endpoint {path} not implemented yet"}}
        
        if not self.session:
            await self.connect()
        
        # Real API call logic here...
        # (keeping the original implementation for when we have real API keys)
        
        # Prepare request body
        body = ""
        if data:
            body = json.dumps(data, default=str)
        
        # Prepare headers
        request_headers = self.headers.copy()
        if auth_required:
            auth_headers = self._get_auth_headers(method, path, body)
            request_headers.update(auth_headers)
        
        try:
            response = await self.session.request(
                method=method,
                url=path,
                params=params,
                content=body if body else None,
                headers=request_headers
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                await asyncio.sleep(retry_after)
                return await self._make_request(method, path, params, data, auth_required)
            
            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
            else:
                result = {"data": response.text}
            
            # Handle errors
            if response.status_code >= 400:
                error_detail = ErrorDetail(
                    code=response.status_code,
                    message=result.get("message", "Unknown error"),
                    details=result.get("details")
                )
                raise HTTPException(status_code=response.status_code, detail=error_detail.dict())
            
            return result
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}")
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="Request timeout")
    
    # Public Market Data Endpoints
    
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets"""
        result = await self._make_request("GET", "/markets")
        return result.get("data", [])
    
    async def get_market_stats(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get market statistics"""
        path = f"/markets/{symbol}/stats" if symbol else "/markets/stats"
        result = await self._make_request("GET", path)
        return result.get("data", {} if symbol else [])
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book for a symbol"""
        params = {"limit": limit}
        result = await self._make_request("GET", f"/markets/{symbol}/orderbook", params=params)
        return result.get("data", {})
    
    async def get_trades(self, symbol: str, limit: int = 100, cursor: Optional[int] = None) -> Dict[str, Any]:
        """Get recent trades for a symbol"""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._make_request("GET", f"/markets/{symbol}/trades", params=params)
    
    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get OHLCV candles for a symbol"""
        params = {
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
            
        result = await self._make_request("GET", f"/markets/{symbol}/candles", params=params)
        return result.get("data", [])
    
    async def get_funding_history(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get funding rate history for a symbol"""
        params = {"limit": limit}
        result = await self._make_request("GET", f"/markets/{symbol}/funding", params=params)
        return result.get("data", [])
    
    # Private Account Endpoints
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        result = await self._make_request("GET", "/account", auth_required=True)
        return result.get("data", {})
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        params = {"symbol": symbol} if symbol else {}
        result = await self._make_request("GET", "/positions", params=params, auth_required=True)
        return result.get("data", [])
    
    async def get_position_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get position history"""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if cursor:
            params["cursor"] = cursor
            
        return await self._make_request("GET", "/positions/history", params=params, auth_required=True)
    
    async def get_leverage(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get leverage settings"""
        params = {"symbol": symbol} if symbol else {}
        result = await self._make_request("GET", "/account/leverage", params=params, auth_required=True)
        return result.get("data", {} if symbol else [])
    
    async def set_leverage(self, symbol: str, leverage: Decimal) -> Dict[str, Any]:
        """Set leverage for a symbol"""
        data = {
            "symbol": symbol,
            "leverage": str(leverage)
        }
        result = await self._make_request("PATCH", "/account/leverage", data=data, auth_required=True)
        return result.get("data", {})
    
    async def get_fees(self) -> Dict[str, Any]:
        """Get fee structure"""
        result = await self._make_request("GET", "/account/fees", auth_required=True)
        return result.get("data", {})
    
    # Private Order Endpoints
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        result = await self._make_request("POST", "/orders", data=order_data, auth_required=True)
        return result.get("data", {})
    
    async def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get orders"""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
            
        return await self._make_request("GET", "/orders", params=params, auth_required=True)
    
    async def get_order_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get order history"""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if cursor:
            params["cursor"] = cursor
            
        return await self._make_request("GET", "/orders/history", params=params, auth_required=True)
    
    async def update_order(self, order_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing order"""
        result = await self._make_request("PATCH", f"/orders/{order_id}", data=update_data, auth_required=True)
        return result.get("data", {})
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a specific order"""
        result = await self._make_request("DELETE", f"/orders/{order_id}", auth_required=True)
        return result.get("data", {})
    
    async def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all orders"""
        data = {"symbol": symbol} if symbol else {}
        result = await self._make_request("DELETE", "/orders", data=data, auth_required=True)
        return result.get("data", {})
    
    async def get_trades_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get trade execution history"""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if cursor:
            params["cursor"] = cursor
            
        return await self._make_request("GET", "/trades", params=params, auth_required=True)
    
    # Transfers and Withdrawals
    
    async def create_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a transfer between accounts"""
        result = await self._make_request("POST", "/transfers", data=transfer_data, auth_required=True)
        return result.get("data", {})
    
    async def create_withdrawal(self, withdrawal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a withdrawal request"""
        result = await self._make_request("POST", "/withdrawals", data=withdrawal_data, auth_required=True)
        return result.get("data", {})
    
    async def get_deposits(self, limit: int = 100, cursor: Optional[int] = None) -> Dict[str, Any]:
        """Get deposit history"""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._make_request("GET", "/deposits", params=params, auth_required=True)
    
    async def get_withdrawals(self, limit: int = 100, cursor: Optional[int] = None) -> Dict[str, Any]:
        """Get withdrawal history"""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._make_request("GET", "/withdrawals", params=params, auth_required=True)


# Global client instance
extended_client = ExtendedExchangeClient() 