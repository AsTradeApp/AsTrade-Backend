from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class Balance(BaseModel):
    """Account balance model"""
    asset: str
    total: Decimal
    available: Decimal
    reserved: Decimal
    unrealized_pnl: Decimal = Decimal('0')


class Position(BaseModel):
    """Position model"""
    symbol: str
    side: str  # long or short
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    liquidation_price: Optional[Decimal] = None
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    leverage: Decimal
    margin: Decimal
    maintenance_margin: Decimal
    margin_ratio: Decimal
    created_at: datetime
    updated_at: datetime


class PositionHistory(BaseModel):
    """Historical position model"""
    id: str
    symbol: str
    side: str
    size: Decimal
    entry_price: Decimal
    exit_price: Decimal
    realized_pnl: Decimal
    fees: Decimal
    opened_at: datetime
    closed_at: datetime
    duration: int  # seconds


class AccountSummary(BaseModel):
    """Account summary model"""
    total_equity: Decimal
    available_balance: Decimal
    used_margin: Decimal
    free_margin: Decimal
    margin_ratio: Decimal
    unrealized_pnl: Decimal
    total_positions: int
    open_orders: int


class LeverageInfo(BaseModel):
    """Leverage information model"""
    symbol: str
    current_leverage: Decimal
    max_leverage: Decimal
    position_size: Decimal = Decimal('0')


class FeeStructure(BaseModel):
    """Fee structure model"""
    maker_fee: Decimal
    taker_fee: Decimal
    volume_30d: Decimal
    tier_level: str
    next_tier_volume: Optional[Decimal] = None
    next_tier_maker_fee: Optional[Decimal] = None
    next_tier_taker_fee: Optional[Decimal] = None


class AccountRequest(BaseModel):
    """Base request model for account endpoints"""
    limit: int = Field(default=100, ge=1, le=1000)
    cursor: Optional[int] = None
    symbol: Optional[str] = None


class LeverageRequest(BaseModel):
    """Request model for leverage updates"""
    symbol: str
    leverage: Decimal = Field(ge=1, le=20)


class PositionRequest(BaseModel):
    """Request model for position queries"""
    symbol: Optional[str] = None
    status: Optional[str] = None  # open, closed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    cursor: Optional[int] = None 