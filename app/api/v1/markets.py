from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import structlog

from app.services.extended_client import extended_client
from app.models.responses import SuccessResponse
from app.models.markets import (
    MarketInfo, MarketStats, OrderBook, Trade, Candle, FundingRate,
    MarketRequest, CandleRequest
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
    try:
        logger.info("Fetching all markets")
        markets_data = await extended_client.get_markets()
        
        logger.info("Markets fetched successfully", count=len(markets_data))
        return SuccessResponse(data=markets_data)
        
    except Exception as e:
        logger.error("Failed to fetch markets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch markets")


@router.get("/stats", response_model=SuccessResponse, summary="Get market statistics for all symbols")
async def get_all_market_stats():
    """
    Get 24h statistics for all markets including:
    - Price changes and percentages
    - High/low prices
    - Volume and open interest
    - Funding rates
    - Mark and index prices
    """
    try:
        logger.info("Fetching all market statistics")
        stats_data = await extended_client.get_market_stats()
        
        logger.info("Market statistics fetched successfully", count=len(stats_data))
        return SuccessResponse(data=stats_data)
        
    except Exception as e:
        logger.error("Failed to fetch market statistics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch market statistics")


@router.get("/{symbol}/stats", response_model=SuccessResponse, summary="Get market statistics for specific symbol")
async def get_market_stats(symbol: str):
    """
    Get 24h statistics for a specific market symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., BTC-USD, ETH-USD)
    """
    try:
        logger.info("Fetching market statistics", symbol=symbol)
        stats_data = await extended_client.get_market_stats(symbol)
        
        logger.info("Market statistics fetched successfully", symbol=symbol)
        return SuccessResponse(data=stats_data)
        
    except Exception as e:
        logger.error("Failed to fetch market statistics", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics for {symbol}")


@router.get("/{symbol}/orderbook", response_model=SuccessResponse, summary="Get order book")
async def get_orderbook(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Number of price levels to return")
):
    """
    Get the current order book for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., BTC-USD, ETH-USD)
        limit: Number of price levels to return (1-1000)
    
    Returns:
        Order book with bids and asks, including price, size, and number of orders
    """
    try:
        logger.info("Fetching order book", symbol=symbol, limit=limit)
        orderbook_data = await extended_client.get_orderbook(symbol, limit)
        
        logger.info("Order book fetched successfully", symbol=symbol, 
                   bids_count=len(orderbook_data.get('bids', [])),
                   asks_count=len(orderbook_data.get('asks', [])))
        return SuccessResponse(data=orderbook_data)
        
    except Exception as e:
        logger.error("Failed to fetch order book", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch order book for {symbol}")


@router.get("/{symbol}/trades", response_model=SuccessResponse, summary="Get recent trades")
async def get_trades(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Number of trades to return"),
    cursor: Optional[int] = Query(default=None, description="Pagination cursor")
):
    """
    Get recent trades for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., BTC-USD, ETH-USD)
        limit: Number of trades to return (1-1000)
        cursor: Pagination cursor for fetching older trades
    
    Returns:
        List of recent trades with price, size, side, and timestamp
    """
    try:
        logger.info("Fetching trades", symbol=symbol, limit=limit, cursor=cursor)
        trades_data = await extended_client.get_trades(symbol, limit, cursor)
        
        logger.info("Trades fetched successfully", symbol=symbol, 
                   count=len(trades_data.get('data', [])))
        return SuccessResponse(
            data=trades_data.get('data', []),
            pagination=trades_data.get('pagination')
        )
        
    except Exception as e:
        logger.error("Failed to fetch trades", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch trades for {symbol}")


@router.get("/{symbol}/candles", response_model=SuccessResponse, summary="Get OHLCV candles")
async def get_candles(
    symbol: str,
    interval: str = Query(default="1h", description="Candle interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of candles to return"),
    start_time: Optional[int] = Query(default=None, description="Start timestamp (unix seconds)"),
    end_time: Optional[int] = Query(default=None, description="End timestamp (unix seconds)")
):
    """
    Get OHLCV candle data for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., BTC-USD, ETH-USD)
        interval: Time interval for candles (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        limit: Number of candles to return (1-1000)
        start_time: Start timestamp in unix seconds
        end_time: End timestamp in unix seconds
    
    Returns:
        OHLCV candle data with timestamps, prices, and volume
    """
    try:
        logger.info("Fetching candles", symbol=symbol, interval=interval, 
                   limit=limit, start_time=start_time, end_time=end_time)
        
        candles_data = await extended_client.get_candles(
            symbol, interval, limit, start_time, end_time
        )
        
        logger.info("Candles fetched successfully", symbol=symbol, interval=interval,
                   count=len(candles_data))
        return SuccessResponse(data=candles_data)
        
    except Exception as e:
        logger.error("Failed to fetch candles", symbol=symbol, interval=interval, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch candles for {symbol}")


@router.get("/{symbol}/funding", response_model=SuccessResponse, summary="Get funding rate history")
async def get_funding_history(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Number of funding records to return")
):
    """
    Get funding rate history for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g., BTC-USD, ETH-USD)
        limit: Number of funding records to return (1-1000)
    
    Returns:
        Historical funding rates with timestamps, rates, and mark/index prices
    """
    try:
        logger.info("Fetching funding history", symbol=symbol, limit=limit)
        funding_data = await extended_client.get_funding_history(symbol, limit)
        
        logger.info("Funding history fetched successfully", symbol=symbol, 
                   count=len(funding_data))
        return SuccessResponse(data=funding_data)
        
    except Exception as e:
        logger.error("Failed to fetch funding history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch funding history for {symbol}") 