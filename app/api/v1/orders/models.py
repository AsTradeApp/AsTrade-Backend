"""Order models for API endpoints"""
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Order type enumeration"""
    LIMIT = "limit"
    MARKET = "market"
    STOP_LIMIT = "stop_limit"
    STOP_MARKET = "stop_market"
    TWAP = "twap"


class OrderSide(str, Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    """Time in force enumeration"""
    GTC = "gtc"  # Good till cancelled
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill
    GTD = "gtd"  # Good till date


class OrderRequest(BaseModel):
    """Order creation request model"""
    symbol: str = Field(..., description="Market symbol (e.g., BTC-USD)")
    type: OrderType = Field(..., description="Order type")
    side: OrderSide = Field(..., description="Order side")
    size: Decimal = Field(..., description="Order size")
    price: Optional[Decimal] = Field(None, description="Limit price (required for limit orders)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (for stop orders)")
    time_in_force: TimeInForce = Field(default=TimeInForce.GTC, description="Time in force")
    reduce_only: bool = Field(default=False, description="Reduce only flag")
    post_only: bool = Field(default=False, description="Post only flag")
    client_id: Optional[str] = Field(None, description="Client order ID")


class OrderUpdate(BaseModel):
    """Order update request model"""
    price: Optional[Decimal] = None
    size: Optional[Decimal] = None
    client_id: Optional[str] = None


class OrderCancel(BaseModel):
    """Order cancellation request model"""
    order_id: str


class OrdersQuery(BaseModel):
    """Order query parameters model"""
    symbol: Optional[str] = None
    status: Optional[OrderStatus] = None
    limit: int = Field(default=100, ge=1, le=1000)
    cursor: Optional[str] = None


class TradeExecution(BaseModel):
    """Trade execution model"""
    id: str
    order_id: str
    symbol: str
    side: OrderSide
    size: Decimal
    price: Decimal
    fee: Decimal
    fee_asset: str
    timestamp: str


class TWAPOrderParams(BaseModel):
    """TWAP order parameters model"""
    duration: int = Field(..., description="Total duration in seconds (60-86400)")
    interval: int = Field(..., description="Interval between slices in seconds (10-3600)")
    randomize: bool = Field(default=True, description="Randomize slice timing")


class ExtendedTestOrderRequest(BaseModel):
    """Extended trading client test order request"""
    market_name: str = Field(default="BTC-USD", description="Market symbol (e.g., BTC-USD)")
    amount: Decimal = Field(default=Decimal("0.001"), description="Order amount")
    side: OrderSide = Field(default=OrderSide.BUY, description="Order side (buy/sell)")
    post_only: bool = Field(default=True, description="Post only flag")
    auto_cancel: bool = Field(default=True, description="Automatically cancel order after placement") 