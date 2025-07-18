from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class MarketInfo(BaseModel):
    """Market information model"""
    symbol: str
    display_name: str
    base_asset: str
    quote_asset: str
    status: str
    tick_size: Decimal
    step_size: Decimal
    min_order_size: Decimal
    max_order_size: Optional[Decimal] = None
    maker_fee: Decimal
    taker_fee: Decimal
    funding_interval: int
    max_leverage: int
    is_active: bool = True


class MarketStats(BaseModel):
    """24h Market statistics"""
    symbol: str
    last_price: Decimal
    price_change: Decimal
    price_change_percent: Decimal
    high_24h: Decimal
    low_24h: Decimal
    volume_24h: Decimal
    volume_usd_24h: Decimal
    open_interest: Decimal
    funding_rate: Decimal
    next_funding_time: datetime
    mark_price: Decimal
    index_price: Decimal


class OrderBookLevel(BaseModel):
    """Order book price level"""
    price: Decimal
    size: Decimal
    num_orders: int = 0


class OrderBook(BaseModel):
    """Order book model"""
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime
    sequence: int


class Trade(BaseModel):
    """Trade execution model"""
    id: str
    symbol: str
    price: Decimal
    size: Decimal
    side: str  # buy or sell
    timestamp: datetime
    liquidation: bool = False


class Candle(BaseModel):
    """OHLCV candle model"""
    symbol: str
    interval: str  # 1m, 5m, 15m, 30m, 1h, 4h, 1d
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    volume_usd: Decimal
    trades: int


class FundingRate(BaseModel):
    """Funding rate model"""
    symbol: str
    funding_rate: Decimal
    funding_time: datetime
    mark_price: Decimal
    index_price: Decimal


class MarketRequest(BaseModel):
    """Request model for market data"""
    symbol: Optional[str] = None
    symbols: Optional[List[str]] = None
    limit: int = Field(default=100, ge=1, le=1000)
    cursor: Optional[int] = None


class CandleRequest(MarketRequest):
    """Request model for candle data"""
    interval: str = Field(default="1h")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None 