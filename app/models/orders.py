from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from enum import Enum


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
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    """Time in force enumeration"""
    GTC = "gtc"  # Good Till Cancel
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


class Order(BaseModel):
    """Order model"""
    id: str
    client_id: Optional[str] = None
    symbol: str
    type: OrderType
    side: OrderSide
    size: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus
    filled_size: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    fees: Decimal = Decimal('0')
    reduce_only: bool = False
    post_only: bool = False
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class OrderRequest(BaseModel):
    """Order creation request"""
    symbol: str
    type: OrderType
    side: OrderSide
    size: Decimal = Field(gt=0)
    price: Optional[Decimal] = Field(default=None, gt=0)
    stop_price: Optional[Decimal] = Field(default=None, gt=0)
    time_in_force: TimeInForce = TimeInForce.GTC
    client_id: Optional[str] = None
    reduce_only: bool = False
    post_only: bool = False
    
    @validator('price')
    def validate_price(cls, v, values):
        order_type = values.get('type')
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError(f'{order_type} orders require a price')
        return v
    
    @validator('stop_price')
    def validate_stop_price(cls, v, values):
        order_type = values.get('type')
        if order_type in [OrderType.STOP_LIMIT, OrderType.STOP_MARKET] and v is None:
            raise ValueError(f'{order_type} orders require a stop_price')
        return v


class OrderUpdate(BaseModel):
    """Order update request"""
    order_id: str
    size: Optional[Decimal] = Field(default=None, gt=0)
    price: Optional[Decimal] = Field(default=None, gt=0)
    stop_price: Optional[Decimal] = Field(default=None, gt=0)


class OrderCancel(BaseModel):
    """Order cancellation request"""
    order_id: Optional[str] = None
    client_id: Optional[str] = None
    symbol: Optional[str] = None  # For mass cancellation


class OrdersQuery(BaseModel):
    """Orders query request"""
    symbol: Optional[str] = None
    status: Optional[OrderStatus] = None
    type: Optional[OrderType] = None
    side: Optional[OrderSide] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    cursor: Optional[int] = None


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
    liquidity: str  # maker or taker
    timestamp: datetime


class TWAPOrderParams(BaseModel):
    """TWAP order parameters"""
    duration: int = Field(ge=60, le=86400)  # seconds, 1 min to 24 hours
    interval: int = Field(ge=10, le=3600)   # seconds, 10 sec to 1 hour
    randomize: bool = False
    
    @validator('interval')
    def validate_interval(cls, v, values):
        duration = values.get('duration', 0)
        if v > duration:
            raise ValueError('Interval cannot be greater than duration')
        return v 