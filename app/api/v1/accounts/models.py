"""Account models for API endpoints"""
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel


class AccountBalance(BaseModel):
    """Account balance response model"""
    total_equity: Decimal
    available_balance: Decimal
    used_margin: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    collateral: Dict[str, Dict[str, Decimal]]


class AccountPosition(BaseModel):
    """Account position model"""
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


class UserInfo(BaseModel):
    """User information model"""
    user_id: str
    email: Optional[str]
    provider: Optional[str]
    wallet_address: Optional[str]


class AccountBalanceResponse(BaseModel):
    """Combined response model for account balance endpoint"""
    user_info: UserInfo
    balance: AccountBalance 