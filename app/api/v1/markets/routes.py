"""Market endpoints"""
from fastapi import APIRouter, Query, Path, HTTPException
from datetime import datetime
import structlog

from app.models.responses import SuccessResponse, ErrorResponse
from app.api.v1.markets.service import (
    get_all_markets,
    get_market_stats,
    get_market_orderbook,
    get_trending_markets
)

logger = structlog.get_logger()
router = APIRouter(prefix="/markets")


@router.get("/", response_model=SuccessResponse, summary="Get all markets")
async def get_markets():
    """
    Get all available markets/symbols for trading.
    
    Returns information about each trading pair including:
    - Symbol and display name
    - Tick size and step size
    - Minimum order size
    - Fee structure
    - Maximum leverage
    """
    markets = await get_all_markets()
    return SuccessResponse(data=[market.dict() for market in markets])


@router.get("/stats", response_model=SuccessResponse, summary="Get market statistics")
async def get_stats(
    symbol: str = Query(None, description="Market symbol (e.g., BTC-USD)")
):
    """
    Get market statistics for a specific symbol.
    
    Args:
        symbol: Market symbol (e.g., BTC-USD)
    
    Returns:
        Market statistics including:
        - Current price and 24h change
        - Volume (24h, 7d)
        - Number of trades
        - Open interest
        - Funding rate
    """
    stats = await get_market_stats(symbol)
    return SuccessResponse(data=[stat.dict() for stat in stats])


@router.get("/{symbol}/orderbook", response_model=SuccessResponse, summary="Get order book")
async def get_orderbook(
    symbol: str = Path(..., description="Market symbol (e.g., BTC-USD)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of levels to return")
):
    """
    Get market order book.
    
    Args:
        symbol: Market symbol (e.g., BTC-USD)
        limit: Number of price levels to return (1-1000)
    
    Returns:
        Order book with bids and asks
    """
    orderbook = await get_market_orderbook(symbol, limit)
    return SuccessResponse(data=orderbook.dict()) 


@router.get("/trending", response_model=SuccessResponse, summary="Get trending markets")
async def get_trending(
    limit: int = Query(default=10, ge=1, le=100, description="Number of markets to return")
):
    """
    Get trending markets ordered by 24h volume.
    
    Args:
        limit: Number of markets to return (1-100, default: 10)
    
    Returns:
        List of trending markets with their statistics including:
        - Current price and 24h changes
        - Trading volume
        - High/Low prices
    
    Raises:
        400: If limit is invalid
        500: If there's a server error
    """
    try:
        trending_markets = await get_trending_markets(limit)
        return SuccessResponse(
            data=trending_markets,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_LIMIT", "message": str(e)}
        )
    except Exception as e:
        logger.error("Failed to get trending markets", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"code": "MARKET_DATA_ERROR", "message": "Failed to fetch market data"}
        ) 