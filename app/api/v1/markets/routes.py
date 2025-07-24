"""Market routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.models.markets import (
    MarketInfo,
    MarketStats,
    OrderBook,
    Trade,
    Candle
)
from app.models.responses import SuccessResponse
from app.services.database import get_db
from app.api.v1.markets.service import (
    get_markets,
    get_market_stats,
    get_market_orderbook,
    get_market_trades,
    get_market_candles,
    get_trending_markets
)

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/", response_model=SuccessResponse, summary="Get all markets")
async def get_all_markets_route() -> SuccessResponse:
    """Get all available markets"""
    markets = await get_markets()
    return SuccessResponse(data=markets)


@router.get("/trending", response_model=SuccessResponse, summary="Get trending markets")
async def get_trending_markets_route(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of markets to return")
) -> SuccessResponse:
    """Get trending markets sorted by 24h volume"""
    markets = await get_trending_markets(limit)
    return SuccessResponse(data=markets)


@router.get("/stats", response_model=SuccessResponse, summary="Get market statistics")
async def get_market_stats_route(
    symbol: Optional[str] = None
) -> SuccessResponse:
    """Get market statistics"""
    stats = await get_market_stats(symbol)
    return SuccessResponse(data=stats)


@router.get("/{symbol}/orderbook", response_model=SuccessResponse, summary="Get market order book")
async def get_market_orderbook_route(
    symbol: str = Path(..., description="Market symbol")
) -> SuccessResponse:
    """Get market order book"""
    orderbook = await get_market_orderbook(symbol)
    return SuccessResponse(data=orderbook)


@router.get("/{symbol}/trades", response_model=SuccessResponse, summary="Get market trades")
async def get_market_trades_route(
    symbol: str = Path(..., description="Market symbol")
) -> SuccessResponse:
    """Get recent market trades"""
    trades = await get_market_trades(symbol)
    return SuccessResponse(data=trades)


@router.get("/{symbol}/candles", response_model=SuccessResponse, summary="Get market candles")
async def get_market_candles_route(
    symbol: str = Path(..., description="Market symbol"),
    interval: str = Query("1h", description="Candle interval")
) -> SuccessResponse:
    """Get market candle data"""
    candles = await get_market_candles(symbol, interval)
    return SuccessResponse(data=candles) 