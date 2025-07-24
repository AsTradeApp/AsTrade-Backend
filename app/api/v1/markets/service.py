"""Market service layer"""
from typing import List, Optional
from fastapi import HTTPException
import structlog

from app.models.markets import (
    MarketInfo,
    MarketStats,
    OrderBook,
    Trade,
    Candle
)
from app.services.extended.client import extended_client

logger = structlog.get_logger()


async def get_markets() -> List[MarketInfo]:
    """Get all available markets"""
    try:
        markets_data = await extended_client.get_markets()
        return [MarketInfo(**market) for market in markets_data]
    except Exception as e:
        logger.error("Failed to get markets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch markets")


async def get_market_stats(symbol: Optional[str] = None) -> List[MarketStats]:
    """
    Get market statistics aligned with frontend expectations
    
    Transforms Extended Exchange data format to match frontend needs:
    - Renames fields
    - Calculates price changes
    - Formats response
    """
    try:
        stats_data = await extended_client.get_market_stats(symbol)
        
        # Transform data to match frontend format
        transformed_stats = []
        for stat in stats_data:
            # Get required values
            current_price = float(stat.get("price", 0))
            price_24h = float(stat.get("price_24h", 0))
            
            # Calculate price changes
            price_change = current_price - price_24h
            price_change_percent = (price_change / price_24h * 100) if price_24h > 0 else 0
            
            # Create transformed stat object
            transformed_stat = {
                "symbol": stat["symbol"],
                "lastPrice": current_price,
                "priceChange24h": price_change,
                "priceChangePercent24h": round(price_change_percent, 2),
                "volume24h": float(stat.get("volume_24h", 0)),
                "high24h": float(stat.get("high_24h", 0)),
                "low24h": float(stat.get("low_24h", 0)),
                "openPrice24h": price_24h
            }
            
            transformed_stats.append(MarketStats(**transformed_stat))
        
        return transformed_stats
        
    except Exception as e:
        logger.error("Failed to get market stats", error=str(e), symbol=symbol)
        raise HTTPException(status_code=500, detail="Failed to fetch market statistics")


async def get_trending_markets(limit: int = 10) -> List[MarketStats]:
    """
    Get trending markets sorted by 24h volume
    
    Args:
        limit: Maximum number of markets to return
    
    Returns:
        List of market statistics sorted by volume
    """
    try:
        # Get all market stats
        all_stats = await get_market_stats()
        
        # Sort by volume (descending) and take top N
        sorted_stats = sorted(
            all_stats,
            key=lambda x: x.volume24h,
            reverse=True
        )
        
        return sorted_stats[:limit]
        
    except Exception as e:
        logger.error("Failed to get trending markets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch trending markets")


async def get_market_orderbook(symbol: str) -> OrderBook:
    """Get market order book"""
    try:
        orderbook_data = await extended_client.get_orderbook(symbol)
        return OrderBook(**orderbook_data)
    except Exception as e:
        logger.error("Failed to get orderbook", error=str(e), symbol=symbol)
        raise HTTPException(status_code=500, detail="Failed to fetch order book")


async def get_market_trades(symbol: str) -> List[Trade]:
    """Get recent market trades"""
    try:
        trades_data = await extended_client.get_trades(symbol)
        return [Trade(**trade) for trade in trades_data]
    except Exception as e:
        logger.error("Failed to get trades", error=str(e), symbol=symbol)
        raise HTTPException(status_code=500, detail="Failed to fetch trades")


async def get_market_candles(
    symbol: str,
    interval: str = "1h"
) -> List[Candle]:
    """Get market candle data"""
    try:
        candles_data = await extended_client.get_candles(symbol, interval)
        return [Candle(**candle) for candle in candles_data]
    except Exception as e:
        logger.error("Failed to get candles", error=str(e), symbol=symbol)
        raise HTTPException(status_code=500, detail="Failed to fetch candle data") 