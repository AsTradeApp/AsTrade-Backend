"""
Real-time price streaming service using x10 perpetual orderbook.
Integrates with Stark trading for live BTC-USD price updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Set, Optional, Callable
from dataclasses import dataclass

import structlog
from fastapi import WebSocket

# Import x10 perpetual dependencies
try:
    from x10.perpetual.configuration import STARKNET_TESTNET_CONFIG
    from x10.perpetual.orderbook import OrderBook
    X10_AVAILABLE = True
except ImportError:
    X10_AVAILABLE = False
    structlog.get_logger().warning("x10 perpetual not available, using fallback mode")

logger = structlog.get_logger()

@dataclass
class PriceUpdate:
    """Real-time price update from orderbook"""
    symbol: str
    price: float
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    timestamp: str
    
    def to_dict(self) -> dict:
        return {
            "type": "price_update",
            "symbol": self.symbol,
            "price": self.price,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": self.spread,
            "timestamp": self.timestamp,
        }

class PriceStreamingService:
    """Service for streaming real-time price data from x10 orderbook"""
    
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.orderbooks: Dict[str, OrderBook] = {}
        self.current_prices: Dict[str, PriceUpdate] = {}
        self.is_running = False
        
    async def start_orderbook_stream(self, symbol: str = "BTC-USD"):
        """Start real-time orderbook streaming for a symbol"""
        if not X10_AVAILABLE:
            logger.error("x10 perpetual not available, cannot start orderbook stream")
            return False
            
        if symbol in self.orderbooks:
            logger.info(f"Orderbook stream already running for {symbol}")
            return True
            
        try:
            logger.info(f"Starting orderbook stream for {symbol}")
            
            # Callbacks for best bid/ask changes
            def on_best_ask_change(best_ask):
                asyncio.create_task(self._handle_price_update(symbol, best_ask=best_ask))
                
            def on_best_bid_change(best_bid):
                asyncio.create_task(self._handle_price_update(symbol, best_bid=best_bid))
            
            # Create and start orderbook
            orderbook = await OrderBook.create(
                STARKNET_TESTNET_CONFIG,
                market_name=symbol,
                start=True,
                best_ask_change_callback=on_best_ask_change,
                best_bid_change_callback=on_best_bid_change,
            )
            
            self.orderbooks[symbol] = orderbook
            self.is_running = True
            
            logger.info(f"Successfully started orderbook stream for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start orderbook stream for {symbol}: {e}")
            return False
    
    async def _handle_price_update(self, symbol: str, best_bid=None, best_ask=None):
        """Handle price updates from orderbook callbacks"""
        try:
            current_price = self.current_prices.get(symbol)
            
            # Initialize or update current price data
            if current_price is None:
                best_bid_price = best_bid.price if best_bid else None
                best_ask_price = best_ask.price if best_ask else None
            else:
                best_bid_price = best_bid.price if best_bid else current_price.best_bid
                best_ask_price = best_ask.price if best_ask else current_price.best_ask
            
            # Calculate mid price and spread
            if best_bid_price and best_ask_price:
                mid_price = float((Decimal(str(best_bid_price)) + Decimal(str(best_ask_price))) / 2)
                spread = float(Decimal(str(best_ask_price)) - Decimal(str(best_bid_price)))
            elif best_bid_price:
                mid_price = float(best_bid_price)
                spread = None
            elif best_ask_price:
                mid_price = float(best_ask_price)
                spread = None
            else:
                return  # No price data available
            
            # Create price update
            price_update = PriceUpdate(
                symbol=symbol,
                price=mid_price,
                best_bid=float(best_bid_price) if best_bid_price else None,
                best_ask=float(best_ask_price) if best_ask_price else None,
                spread=spread,
                timestamp=datetime.utcnow().isoformat()
            )
            
            self.current_prices[symbol] = price_update
            
            # Broadcast to all connected clients
            await self._broadcast_price_update(symbol, price_update)
            
        except Exception as e:
            logger.error(f"Error handling price update for {symbol}: {e}")
    
    async def _broadcast_price_update(self, symbol: str, price_update: PriceUpdate):
        """Broadcast price update to all connected WebSocket clients"""
        if symbol not in self.connections or not self.connections[symbol]:
            return
            
        message = json.dumps(price_update.to_dict())
        disconnected_clients = set()
        
        for websocket in self.connections[symbol].copy():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send price update to client: {e}")
                disconnected_clients.add(websocket)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.connections[symbol].discard(client)
    
    async def add_websocket_connection(self, websocket: WebSocket, symbol: str):
        """Add a new WebSocket connection for price updates"""
        await websocket.accept()
        
        if symbol not in self.connections:
            self.connections[symbol] = set()
        
        self.connections[symbol].add(websocket)
        
        # Start orderbook streaming if not already running
        if symbol not in self.orderbooks:
            await self.start_orderbook_stream(symbol)
        
        # Send current price if available
        if symbol in self.current_prices:
            try:
                await websocket.send_text(json.dumps(self.current_prices[symbol].to_dict()))
            except Exception as e:
                logger.warning(f"Failed to send initial price to new client: {e}")
        
        logger.info(f"Added WebSocket connection for {symbol}")
    
    async def remove_websocket_connection(self, websocket: WebSocket, symbol: str):
        """Remove a WebSocket connection"""
        if symbol in self.connections:
            self.connections[symbol].discard(websocket)
            
            # Stop orderbook stream if no more connections
            if not self.connections[symbol] and symbol in self.orderbooks:
                try:
                    await self.orderbooks[symbol].stop()
                    del self.orderbooks[symbol]
                    logger.info(f"Stopped orderbook stream for {symbol} (no more connections)")
                except Exception as e:
                    logger.warning(f"Error stopping orderbook for {symbol}: {e}")
        
        logger.info(f"Removed WebSocket connection for {symbol}")
    
    async def get_current_price(self, symbol: str) -> Optional[dict]:
        """Get the current price for a symbol"""
        if symbol in self.current_prices:
            return self.current_prices[symbol].to_dict()
        return None
    
    async def health_check(self) -> dict:
        """Health check for the price streaming service"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "x10_available": X10_AVAILABLE,
            "active_streams": list(self.orderbooks.keys()),
            "total_connections": sum(len(conns) for conns in self.connections.values()),
            "current_prices": {symbol: price.price for symbol, price in self.current_prices.items()}
        }
    
    async def stop_all_streams(self):
        """Stop all orderbook streams"""
        for symbol, orderbook in self.orderbooks.items():
            try:
                await orderbook.stop()
                logger.info(f"Stopped orderbook stream for {symbol}")
            except Exception as e:
                logger.warning(f"Error stopping orderbook for {symbol}: {e}")
        
        self.orderbooks.clear()
        self.connections.clear()
        self.current_prices.clear()
        self.is_running = False
        logger.info("Stopped all price streaming services")

# Global singleton instance
price_streaming_service = PriceStreamingService()

# WebSocket endpoint handler
async def handle_price_stream_websocket(websocket: WebSocket, symbol: str):
    """Handle WebSocket connections for price streaming"""
    try:
        await price_streaming_service.add_websocket_connection(websocket, symbol)
        
        # Keep connection alive and handle client messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Handle ping/pong for connection keep-alive
                if data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif data.get("type") == "subscribe":
                    # Client requesting to subscribe to updates
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "symbol": symbol,
                        "message": f"Subscribed to {symbol} price updates"
                    }))
                    
            except Exception as e:
                logger.warning(f"WebSocket message handling error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error for {symbol}: {e}")
    finally:
        await price_streaming_service.remove_websocket_connection(websocket, symbol)

# Fallback price service for when x10 is not available
class FallbackPriceService:
    """Fallback service that generates realistic price data when x10 is not available"""
    
    def __init__(self):
        self.base_prices = {"BTC-USD": 100000}
        self.running_tasks = {}
    
    async def start_mock_stream(self, symbol: str, websocket_connections: Set[WebSocket]):
        """Start mock price streaming for testing"""
        if symbol in self.running_tasks:
            return
            
        async def mock_price_generator():
            while symbol in self.running_tasks and websocket_connections:
                try:
                    # Generate realistic price movement
                    base_price = self.base_prices.get(symbol, 50000)
                    change = (asyncio.get_event_loop().time() % 1000 - 500) * 2  # ±$1000 variation
                    current_price = base_price + change
                    
                    bid_ask_spread = base_price * 0.0001  # 0.01% spread
                    best_bid = current_price - (bid_ask_spread / 2)
                    best_ask = current_price + (bid_ask_spread / 2)
                    
                    price_update = {
                        "type": "price_update",
                        "symbol": symbol,
                        "price": round(current_price, 2),
                        "best_bid": round(best_bid, 2),
                        "best_ask": round(best_ask, 2),
                        "spread": round(bid_ask_spread, 2),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    # Send to all connected clients
                    message = json.dumps(price_update)
                    for ws in websocket_connections.copy():
                        try:
                            await ws.send_text(message)
                        except:
                            websocket_connections.discard(ws)
                    
                    await asyncio.sleep(2)  # Update every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Mock price generation error: {e}")
                    await asyncio.sleep(5)
        
        task = asyncio.create_task(mock_price_generator())
        self.running_tasks[symbol] = task
        
    def stop_mock_stream(self, symbol: str):
        """Stop mock price streaming"""
        if symbol in self.running_tasks:
            self.running_tasks[symbol].cancel()
            del self.running_tasks[symbol]

# Global fallback service
fallback_price_service = FallbackPriceService() 