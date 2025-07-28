"""
Example WebSocket endpoint for price streaming based on x10 perpetual orderbook streaming.
This shows how to implement real-time BTC-USD price streaming for the frontend.

Usage:
- Frontend connects to ws://localhost:8000/api/v1/stark/stream/prices/BTC-USD
- Server streams real-time price updates
- Can be extended to support multiple symbols
"""

import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger()

# Connection manager for WebSocket connections
class PriceStreamManager:
    def __init__(self):
        # Maps symbol to set of connected websockets
        self.connections: Dict[str, Set[WebSocket]] = {}
        # Background tasks for each symbol
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, symbol: str):
        """Add a new connection for a symbol"""
        await websocket.accept()
        
        if symbol not in self.connections:
            self.connections[symbol] = set()
            
        self.connections[symbol].add(websocket)
        
        # Start streaming for this symbol if not already started
        if symbol not in self.streaming_tasks:
            self.streaming_tasks[symbol] = asyncio.create_task(
                self._stream_prices(symbol)
            )
            
        logger.info(f"Client connected to {symbol} price stream")
        
    async def disconnect(self, websocket: WebSocket, symbol: str):
        """Remove a connection"""
        if symbol in self.connections:
            self.connections[symbol].discard(websocket)
            
            # Stop streaming if no more connections
            if not self.connections[symbol]:
                if symbol in self.streaming_tasks:
                    self.streaming_tasks[symbol].cancel()
                    del self.streaming_tasks[symbol]
                del self.connections[symbol]
                
        logger.info(f"Client disconnected from {symbol} price stream")
        
    async def _stream_prices(self, symbol: str):
        """Stream price updates for a symbol"""
        while symbol in self.connections and self.connections[symbol]:
            try:
                # This would normally fetch from your actual price source
                # For demo, we'll generate realistic price data
                price_data = await self._get_price_data(symbol)
                
                # Send to all connected clients
                if self.connections.get(symbol):
                    disconnected = set()
                    for websocket in self.connections[symbol].copy():
                        try:
                            await websocket.send_text(json.dumps(price_data))
                        except Exception as e:
                            logger.error(f"Failed to send to client: {e}")
                            disconnected.add(websocket)
                    
                    # Remove disconnected clients
                    for ws in disconnected:
                        self.connections[symbol].discard(ws)
                        
                # Update every 2 seconds (adjust as needed)
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                logger.info(f"Price streaming cancelled for {symbol}")
                break
            except Exception as e:
                logger.error(f"Error in price streaming: {e}")
                await asyncio.sleep(5)  # Wait before retry
                
    async def _get_price_data(self, symbol: str) -> dict:
        """
        Get current price data for a symbol.
        In production, this would call your actual price API or x10 client.
        """
        
        # Example implementation - replace with actual price fetching
        if symbol == "BTC-USD":
            # Simulate realistic BTC price movements
            import random
            base_price = 100000
            change = (random.random() - 0.5) * 1000  # ±$500 variation
            current_price = base_price + change
            
            return {
                "type": "price_update",
                "symbol": symbol,
                "price": round(current_price, 2),
                "change24h": round(change, 2),
                "changePercent24h": round((change / base_price) * 100, 4),
                "high24h": round(base_price + 2000, 2),
                "low24h": round(base_price - 2000, 2),
                "volume24h": 1500000000,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        # Default/fallback data
        return {
            "type": "price_update",
            "symbol": symbol,
            "price": 50000.0,
            "change24h": 0.0,
            "changePercent24h": 0.0,
            "high24h": 51000.0,
            "low24h": 49000.0,
            "volume24h": 1000000000,
            "timestamp": datetime.utcnow().isoformat(),
        }

# Global manager instance
price_manager = PriceStreamManager()

# WebSocket endpoint for price streaming
async def price_stream_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for streaming prices.
    
    Usage: ws://localhost:8000/api/v1/stark/stream/prices/{symbol}
    """
    try:
        await price_manager.connect(websocket, symbol)
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (e.g., ping/pong)
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                # Invalid JSON from client
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"Price stream error: {e}")
    finally:
        await price_manager.disconnect(websocket, symbol)

# Alternative: Using x10 perpetual client for real data
async def x10_orderbook_stream(symbol: str = "BTC-USD"):
    """
    Example of how to integrate x10 perpetual orderbook streaming.
    This would be used instead of the mock price generation.
    """
    try:
        # This is based on your provided example
        from x10.perpetual.configuration import TESTNET_CONFIG
        from x10.perpetual.stream_client import PerpetualStreamClient
        
        stream_client = PerpetualStreamClient(api_url=TESTNET_CONFIG.stream_url)
        
        async with stream_client.subscribe_to_orderbooks(symbol) as stream:
            while True:
                try:
                    orderbook_data = await stream.recv()
                    
                    # Transform orderbook data to price data format
                    if orderbook_data and 'asks' in orderbook_data and orderbook_data['asks']:
                        best_ask = orderbook_data['asks'][0][0]  # Best ask price
                        best_bid = orderbook_data['bids'][0][0] if orderbook_data['bids'] else best_ask
                        mid_price = (best_ask + best_bid) / 2
                        
                        price_data = {
                            "type": "price_update",
                            "symbol": symbol,
                            "price": mid_price,
                            "best_bid": best_bid,
                            "best_ask": best_ask,
                            "timestamp": datetime.utcnow().isoformat(),
                            "orderbook": orderbook_data  # Include full orderbook if needed
                        }
                        
                        # Send to all connected clients for this symbol
                        if symbol in price_manager.connections:
                            for websocket in price_manager.connections[symbol].copy():
                                try:
                                    await websocket.send_text(json.dumps(price_data))
                                except Exception as e:
                                    logger.error(f"Failed to send orderbook data: {e}")
                                    
                except Exception as e:
                    logger.error(f"Orderbook stream error: {e}")
                    await asyncio.sleep(5)  # Wait before retry
                    
    except Exception as e:
        logger.error(f"Failed to start x10 orderbook stream: {e}")

# FastAPI router integration example
"""
To integrate this into your FastAPI routes, add this to routes.py:

from fastapi import WebSocket
from .websocket_example import price_stream_endpoint

@router.websocket("/stream/prices/{symbol}")
async def websocket_price_stream(websocket: WebSocket, symbol: str):
    await price_stream_endpoint(websocket, symbol)
""" 