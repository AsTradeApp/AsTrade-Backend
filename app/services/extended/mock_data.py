"""Mock data for Extended Exchange API client"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import random
import time


def get_mock_markets() -> List[Dict[str, Any]]:
    """Get mock market data"""
    return [
        {
            "symbol": "BTC-USD",
            "display_name": "BTC/USD",
            "base_asset": "BTC",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.5",
            "step_size": "0.0001",
            "min_order_size": "0.0001",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "ETH-USD",
            "display_name": "ETH/USD",
            "base_asset": "ETH",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.05",
            "step_size": "0.01",
            "min_order_size": "0.01",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "STRK-USD",
            "display_name": "STRK/USD",
            "base_asset": "STRK",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.01",
            "step_size": "0.1",
            "min_order_size": "0.1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "ADA-USD",
            "display_name": "ADA/USD",
            "base_asset": "ADA",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.001",
            "step_size": "1",
            "min_order_size": "1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "DOT-USD",
            "display_name": "DOT/USD",
            "base_asset": "DOT",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.01",
            "step_size": "0.1",
            "min_order_size": "0.1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "MATIC-USD",
            "display_name": "MATIC/USD",
            "base_asset": "MATIC",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.001",
            "step_size": "1",
            "min_order_size": "1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "LINK-USD",
            "display_name": "LINK/USD",
            "base_asset": "LINK",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.01",
            "step_size": "0.1",
            "min_order_size": "0.1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        },
        {
            "symbol": "UNI-USD",
            "display_name": "UNI/USD",
            "base_asset": "UNI",
            "quote_asset": "USD",
            "status": "active",
            "tick_size": "0.01",
            "step_size": "0.1",
            "min_order_size": "0.1",
            "maker_fee": "0.0002",
            "taker_fee": "0.0005",
            "funding_interval": 3600,
            "max_leverage": 20,
            "is_active": True
        }
    ]


def get_mock_market_stats(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get mock market statistics with dynamic pricing"""
    
    # Base prices for each market
    base_prices = {
        "BTC-USD": 43000.0,
        "ETH-USD": 2200.0,
        "STRK-USD": 1.85,
        "ADA-USD": 0.45,
        "DOT-USD": 6.5,
        "MATIC-USD": 0.75,
        "LINK-USD": 14.0,
        "UNI-USD": 8.5
    }
    
    # Generate dynamic stats for each market
    stats = []
    current_time = int(time.time())
    
    for market_symbol, base_price in base_prices.items():
        # Add some randomness to make it feel more realistic
        random_factor = random.uniform(0.95, 1.05)
        current_price = base_price * random_factor
        
        # Generate 24h ago price with some variation
        price_24h = base_price * random.uniform(0.90, 1.10)
        
        # Calculate price changes
        price_change = current_price - price_24h
        price_change_percent = (price_change / price_24h * 100) if price_24h > 0 else 0
        
        # Generate volume based on market size
        volume_base = {
            "BTC-USD": 1000000,
            "ETH-USD": 500000,
            "STRK-USD": 150000,
            "ADA-USD": 50000,
            "DOT-USD": 80000,
            "MATIC-USD": 60000,
            "LINK-USD": 120000,
            "UNI-USD": 90000
        }
        
        volume = volume_base.get(market_symbol, 50000) * random.uniform(0.8, 1.2)
        
        # Generate high/low based on current price
        high_24h = current_price * random.uniform(1.02, 1.08)
        low_24h = current_price * random.uniform(0.92, 0.98)
        
        stat = {
            "symbol": market_symbol,
            "price": f"{current_price:.2f}",
            "price_24h": f"{price_24h:.2f}",
            "volume_24h": f"{volume:.4f}",
            "high_24h": f"{high_24h:.2f}",
            "low_24h": f"{low_24h:.2f}",
            "timestamp": current_time
        }
        
        stats.append(stat)
    
    if symbol:
        return [stat for stat in stats if stat["symbol"] == symbol]
    return stats


def get_mock_orderbook(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """Get mock order book data"""
    return {
        "symbol": symbol,
        "bids": [
            ["43200.50", "0.1234"],
            ["43150.00", "0.2345"],
            ["43100.50", "0.3456"]
        ],
        "asks": [
            ["43300.00", "0.1234"],
            ["43350.50", "0.2345"],
            ["43400.00", "0.3456"]
        ],
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
    }


def get_mock_trades(symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get mock trades data"""
    return [
        {
            "id": "123456",
            "symbol": symbol,
            "side": "buy",
            "price": "43250.50",
            "size": "0.1234",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "id": "123457",
            "symbol": symbol,
            "side": "sell",
            "price": "43255.00",
            "size": "0.2345",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000) - 1000
        }
    ]


def get_mock_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get mock candle data"""
    return [
        {
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "open": "43200.50",
            "high": "43300.00",
            "low": "43100.00",
            "close": "43250.50",
            "volume": "123.4567"
        },
        {
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000) - 3600000,
            "open": "43150.00",
            "high": "43250.00",
            "low": "43050.00",
            "close": "43200.50",
            "volume": "234.5678"
        }
    ]


def get_mock_account_balance() -> Dict[str, Any]:
    """Get mock account balance"""
    return {
        "total_equity": "12345.67",
        "total_margin": "1234.56",
        "free_margin": "11111.11",
        "margin_ratio": "0.1",
        "balances": [
            {
                "asset": "USD",
                "free": "10000.00",
                "locked": "2345.67"
            },
            {
                "asset": "BTC",
                "free": "1.2345",
                "locked": "0.1234"
            }
        ]
    }


def get_mock_positions(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get mock positions data"""
    positions = [
        {
            "symbol": "BTC-USD",
            "side": "long",
            "size": "0.1234",
            "entry_price": "42150.00",
            "mark_price": "43250.50",
            "pnl": "135.67",
            "margin": "1234.56",
            "leverage": "10"
        },
        {
            "symbol": "ETH-USD",
            "side": "short",
            "size": "2.3456",
            "entry_price": "2250.25",
            "mark_price": "2150.00",
            "pnl": "235.67",
            "margin": "2345.67",
            "leverage": "10"
        }
    ]
    
    if symbol:
        return [pos for pos in positions if pos["symbol"] == symbol]
    return positions


def get_mock_position_history() -> List[Dict[str, Any]]:
    """Get mock position history"""
    return [
        {
            "symbol": "BTC-USD",
            "side": "long",
            "size": "0.1234",
            "entry_price": "42150.00",
            "exit_price": "43250.50",
            "pnl": "135.67",
            "margin": "1234.56",
            "leverage": "10",
            "opened_at": int(datetime.now(timezone.utc).timestamp() * 1000) - 86400000,
            "closed_at": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "symbol": "ETH-USD",
            "side": "short",
            "size": "2.3456",
            "entry_price": "2250.25",
            "exit_price": "2150.00",
            "pnl": "235.67",
            "margin": "2345.67",
            "leverage": "10",
            "opened_at": int(datetime.now(timezone.utc).timestamp() * 1000) - 172800000,
            "closed_at": int(datetime.now(timezone.utc).timestamp() * 1000) - 86400000
        }
    ]


def get_mock_leverage() -> Dict[str, Any]:
    """Get mock leverage settings"""
    return {
        "max_leverage": 20,
        "current_leverage": 10,
        "maintenance_margin_ratio": 0.05,
        "initial_margin_ratio": 0.1
    }


def get_mock_fees() -> Dict[str, Any]:
    """Get mock fee structure"""
    return {
        "maker_fee": "0.0002",
        "taker_fee": "0.0005",
        "funding_interval": 3600,
        "next_funding_time": int(datetime.now(timezone.utc).timestamp() * 1000) + 1800000,
        "funding_rate": "0.0001"
    } 