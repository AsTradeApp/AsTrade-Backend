"""Market models"""
from typing import Optional, List
from pydantic import BaseModel, Field
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
    """Market statistics aligned with frontend expectations"""
    symbol: str = Field(..., example="BTC-USD", description="Market symbol")
    lastPrice: float = Field(..., example=43250.50, description="Current market price")
    priceChange24h: float = Field(..., example=1100.50, description="Price change in the last 24 hours")
    priceChangePercent24h: float = Field(..., example=2.61, description="Percentage price change in the last 24 hours")
    volume24h: float = Field(..., example=1234.5678, description="Trading volume in the last 24 hours")
    high24h: float = Field(..., example=43500.00, description="Highest price in the last 24 hours")
    low24h: float = Field(..., example=42000.00, description="Lowest price in the last 24 hours")
    openPrice24h: float = Field(..., example=42150.00, description="Opening price 24 hours ago")


class OrderBookEntry(BaseModel):
    """Order book entry model"""
    price: float
    size: float


class OrderBook(BaseModel):
    """Order book model"""
    symbol: str
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: int


class Trade(BaseModel):
    """Trade model"""
    id: str
    symbol: str
    side: str
    price: float
    size: float
    timestamp: int


class Candle(BaseModel):
    """Candle model"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float 