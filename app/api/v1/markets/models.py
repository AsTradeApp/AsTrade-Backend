"""Market models for API endpoints"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class MarketInfo(BaseModel):
    """Market information model"""
    symbol: str
    base_asset: str
    quote_asset: str
    status: str
    tick_size: float
    step_size: float
    min_order_size: float
    max_order_size: float
    maker_fee: float
    taker_fee: float
    funding_interval: int
    max_leverage: int
    is_active: bool


class MarketStats(BaseModel):
    """Market statistics model"""
    symbol: str
    price: float
    price_24h: float
    volume_24h: float
    volume_7d: float
    trades_24h: int
    open_interest: float
    funding_rate: float
    next_funding_time: str


class OrderBook(BaseModel):
    """Order book model"""
    symbol: str
    bids: List[List[float]]  # [price, size]
    asks: List[List[float]]  # [price, size]
    timestamp: str


class Trade(BaseModel):
    """Trade model"""
    id: str
    symbol: str
    side: str
    size: float
    price: float
    timestamp: str
    liquidation: bool


class Candle(BaseModel):
    """OHLCV candle model"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class FundingRate(BaseModel):
    """Funding rate model"""
    symbol: str
    rate: float
    timestamp: str
    next_rate: Optional[float]
    next_time: str 


class TrendingMarketStats(BaseModel):
    """Model for trending market statistics"""
    symbol: str = Field(..., example="BTC-USDT", description="Market symbol")
    lastPrice: float = Field(..., example=43250, description="Current market price")
    priceChange24h: float = Field(..., example=1250, description="Absolute price change in 24h")
    priceChangePercent24h: float = Field(..., example=2.3, description="Percentage price change in 24h")
    volume24h: float = Field(..., example=1250000, description="Trading volume in last 24h")
    high24h: float = Field(..., example=44000, description="Highest price in 24h")
    low24h: float = Field(..., example=42500, description="Lowest price in 24h")
    openPrice24h: float = Field(..., example=42800, description="Opening price 24h ago") 