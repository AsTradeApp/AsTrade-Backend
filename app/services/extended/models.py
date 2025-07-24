"""Models for Extended Exchange client"""
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel


class MarketInfo(BaseModel):
    """Market information model"""
    symbol: str
    base_asset: str
    quote_asset: str
    status: str
    tick_size: Decimal
    step_size: Decimal
    min_order_size: Decimal
    max_order_size: Decimal
    maker_fee: Decimal
    taker_fee: Decimal
    funding_interval: int
    max_leverage: int
    is_active: bool


class Balance(BaseModel):
    """Account balance model"""
    total_equity: Decimal
    available_balance: Decimal
    used_margin: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    collateral: Dict[str, Dict[str, Decimal]]


class Position(BaseModel):
    """Position model"""
    symbol: str
    side: str
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    liquidation_price: Decimal
    unrealized_pnl: Decimal
    leverage: Decimal
    margin: Decimal
    margin_ratio: Decimal
    created_at: str


class LeverageInfo(BaseModel):
    """Leverage information model"""
    current: Decimal
    max: Decimal


class FeeStructure(BaseModel):
    """Fee structure model"""
    maker_fee: Decimal
    taker_fee: Decimal
    trading_volume_30d: Decimal
    tier: str
    next_tier: Optional[Dict[str, Any]] 