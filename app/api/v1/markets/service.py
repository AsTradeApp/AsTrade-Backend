"""Market service layer"""
from typing import List, Optional, Dict, Any
import structlog
from fastapi import HTTPException

from app.services.extended_client import extended_client
from app.api.v1.markets.models import (
    MarketInfo,
    MarketStats,
    OrderBook,
    Trade,
    Candle,
    FundingRate,
    TrendingMarketStats
)

logger = structlog.get_logger()


async def get_all_markets() -> List[MarketInfo]:
    """
    Get all available markets.
    
    Returns:
        List of market information
        
    Raises:
        HTTPException: If markets fetch fails
    """
    try:
        logger.info("Fetching all markets")
        markets_data = await extended_client.get_markets()
        
        # Convert to Pydantic models
        markets = [MarketInfo(**market) for market in markets_data]
        
        logger.info("Markets fetched successfully", count=len(markets))
        return markets
        
    except Exception as e:
        logger.error("Failed to fetch markets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch markets")


async def get_market_stats(symbol: Optional[str] = None) -> List[MarketStats]:
    """
    Get market statistics.
    
    Args:
        symbol: Optional symbol filter
        
    Returns:
        List of market statistics
        
    Raises:
        HTTPException: If stats fetch fails
    """
    try:
        logger.info("Fetching market stats", symbol=symbol)
        stats_data = await extended_client.get_market_stats(symbol)
        
        # Convert to Pydantic models
        stats = []
        for stat in stats_data:
            try:
                # Convert numeric strings to Decimal
                stat_copy = stat.copy()
                for key in ["price", "price_24h", "volume_24h", "volume_7d", "open_interest", "funding_rate"]:
                    if key in stat_copy and isinstance(stat_copy[key], str):
                        stat_copy[key] = float(stat_copy[key])
                stats.append(MarketStats(**stat_copy))
            except Exception as e:
                logger.error("Failed to convert market stat", stat=stat, error=str(e))
                continue
        
        logger.info("Market stats fetched successfully", symbol=symbol)
        return stats
        
    except Exception as e:
        logger.error("Failed to fetch market stats", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch market stats")


async def get_market_orderbook(symbol: str, limit: int = 100) -> OrderBook:
    """
    Get market order book.
    
    Args:
        symbol: Market symbol
        limit: Number of levels to return
        
    Returns:
        Order book data
        
    Raises:
        HTTPException: If orderbook fetch fails
    """
    try:
        logger.info("Fetching orderbook", symbol=symbol, limit=limit)
        orderbook_data = await extended_client.get_orderbook(symbol, limit)
        
        # Convert string prices and sizes to Decimal
        orderbook_copy = orderbook_data.copy()
        orderbook_copy["bids"] = [[float(p), float(s)] for p, s in orderbook_data["bids"]]
        orderbook_copy["asks"] = [[float(p), float(s)] for p, s in orderbook_data["asks"]]
        
        # Convert to Pydantic model
        orderbook = OrderBook(**orderbook_copy)
        
        logger.info("Orderbook fetched successfully", symbol=symbol)
        return orderbook
        
    except Exception as e:
        logger.error("Failed to fetch orderbook", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch orderbook") 


async def get_trending_markets(limit: int = 10) -> List[TrendingMarketStats]:
    """
    Get trending markets ordered by 24h volume.
    
    Args:
        limit: Number of markets to return (default: 10)
        
    Returns:
        List of trending market statistics
    """
    try:
        # Get all market stats
        all_stats = await extended_client.get_market_stats()
        
        # Convert to TrendingMarketStats and sort by volume
        trending_markets = []
        for stat in all_stats:
            # Convert string values to float
            last_price = float(stat.get("price", 0))
            open_price = float(stat.get("price_24h", last_price))
            volume = float(stat.get("volume_24h", 0))
            high = float(stat.get("high_24h", last_price))
            low = float(stat.get("low_24h", last_price))
            
            # Calculate price changes
            price_change = last_price - open_price
            price_change_percent = (price_change / open_price * 100) if open_price > 0 else 0
            
            trending_markets.append(
                TrendingMarketStats(
                    symbol=stat["symbol"],
                    lastPrice=last_price,
                    priceChange24h=price_change,
                    priceChangePercent24h=round(price_change_percent, 2),
                    volume24h=volume,
                    high24h=high,
                    low24h=low,
                    openPrice24h=open_price
                )
            )
        
        # Sort by volume (descending) and limit results
        trending_markets.sort(key=lambda x: x.volume24h, reverse=True)
        return trending_markets[:limit]
        
    except Exception as e:
        logger.error("Failed to get trending markets", error=str(e))
        return [] 