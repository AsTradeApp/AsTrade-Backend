"""Mock data for Extended Exchange client"""
from decimal import Decimal
from datetime import datetime, timezone


def get_mock_markets():
    """Get mock market data"""
    return [
        {
            "symbol": "BTC-USD",
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


def get_mock_market_stats(symbol=None):
    """Get mock market statistics"""
    stats = [
        {
            "symbol": "BTC-USD",
            "price": "50000.0",
            "price_24h": "48000.0",
            "high_24h": "51000.0",
            "low_24h": "47500.0",
            "volume_24h": "1000.0",
            "volume_7d": "7000.0",
            "trades_24h": 10000,
            "open_interest": "500.0",
            "funding_rate": "0.0001",
            "next_funding_time": datetime.now(timezone.utc).isoformat()
        },
        {
            "symbol": "ETH-USD",
            "price": "3000.0",
            "price_24h": "2900.0",
            "high_24h": "3100.0",
            "low_24h": "2850.0",
            "volume_24h": "5000.0",
            "volume_7d": "35000.0",
            "trades_24h": 8000,
            "open_interest": "2000.0",
            "funding_rate": "0.0002",
            "next_funding_time": datetime.now(timezone.utc).isoformat()
        },
        {
            "symbol": "SOL-USD",
            "price": "100.0",
            "price_24h": "95.0",
            "high_24h": "102.0",
            "low_24h": "94.0",
            "volume_24h": "10000.0",
            "volume_7d": "70000.0",
            "trades_24h": 5000,
            "open_interest": "5000.0",
            "funding_rate": "0.0003",
            "next_funding_time": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    if symbol:
        return [stat for stat in stats if stat["symbol"] == symbol]
    return stats


def get_mock_orderbook(symbol, limit=100):
    """Get mock order book data"""
    return {
        "symbol": symbol,
        "bids": [
            ["49995.0", "0.1"],
            ["49990.0", "0.5"],
            ["49985.0", "1.0"]
        ][:limit],
        "asks": [
            ["50005.0", "0.2"],
            ["50010.0", "0.4"],
            ["50015.0", "0.8"]
        ][:limit],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def get_mock_account_balance():
    """Get mock account balance"""
    return {
        "total_equity": "100000.0",
        "available_balance": "80000.0",
        "used_margin": "20000.0",
        "unrealized_pnl": "5000.0",
        "realized_pnl": "2000.0",
        "positions_value": "25000.0"
    }


def get_mock_positions(symbol=None):
    """Get mock positions"""
    positions = [
        {
            "symbol": "BTC-USD",
            "side": "long",
            "size": "0.5",
            "entry_price": "48000.0",
            "mark_price": "50000.0",
            "liquidation_price": "40000.0",
            "margin": "10000.0",
            "leverage": "10",
            "unrealized_pnl": "1000.0",
            "realized_pnl": "500.0",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    if symbol:
        return [pos for pos in positions if pos["symbol"] == symbol]
    return positions


def get_mock_position_history():
    """Get mock position history"""
    return [
        {
            "symbol": "SOL-USD",
            "side": "long",
            "size": "10.0",
            "entry_price": "180.0",
            "exit_price": "185.0",
            "realized_pnl": "50.0",
            "leverage": "3.0",
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": datetime.now(timezone.utc).isoformat()
        }
    ]


def get_mock_leverage(symbol=None):
    """Get mock leverage settings"""
    leverage_data = {
        "BTC-USD": {"current": "10.0", "max": "20.0"},
        "ETH-USD": {"current": "5.0", "max": "20.0"},
        "SOL-USD": {"current": "3.0", "max": "15.0"}
    }
    
    if symbol:
        return leverage_data.get(symbol, {})
    return leverage_data


def get_mock_fees():
    """Get mock fee structure"""
    return {
        "maker_fee": "0.0002",
        "taker_fee": "0.0005",
        "trading_volume_30d": "50000.0",
        "tier": "VIP1",
        "next_tier": {
            "name": "VIP2",
            "volume_required": "100000.0",
            "maker_fee": "0.00015",
            "taker_fee": "0.0004"
        }
    } 