"""Extended Exchange API client with async support"""
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
from app.services.extended.mock_data import (
    get_mock_account_balance,
    get_mock_positions,
    get_mock_position_history,
    get_mock_leverage,
    get_mock_fees,
    get_mock_markets
)


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

    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate signature for private endpoints"""
        if not settings.extended_secret_key:
            return ""
            
        message = f"{timestamp}{method}{path}{body}"
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
                return {"data": get_mock_markets()}
            elif path == "/account":
                return {"data": get_mock_account_balance()}
            elif path == "/positions":
                return {"data": get_mock_positions()}
            elif path.startswith("/positions/"):
                return {"data": get_mock_position_history()}
            elif path == "/leverage":
                return {"data": get_mock_leverage()}
            elif path == "/fees":
                return {"data": get_mock_fees()}
            else:
                return {"data": {"message": f"Mock endpoint {path} not implemented yet"}}
        
        if not self.session:
            await self.connect()
        
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

    # Public API methods
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all markets"""
        result = await self._make_request("GET", "/markets")
        return result.get("data", [])

    # Account methods
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        result = await self._make_request("GET", "/account", auth_required=True)
        return result.get("data", {})
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        params = {"symbol": symbol} if symbol else {}
        result = await self._make_request("GET", "/positions", params=params, auth_required=True)
        return result.get("data", []) 