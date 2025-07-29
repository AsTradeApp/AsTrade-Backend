"""Stark trading models for API endpoints"""
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class StarkOrderSide(str, Enum):
    """Stark order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class StarkOrderRequest(BaseModel):
    """Stark order creation request model"""
    amount_of_synthetic: Decimal = Field(..., description="Amount of synthetic asset to trade", gt=0)
    price: Decimal = Field(..., description="Order price", gt=0)
    market_name: str = Field(..., description="Market symbol (e.g., BTC-USD)")
    side: StarkOrderSide = Field(..., description="Order side (BUY or SELL)")
    post_only: bool = Field(default=False, description="Whether this is a post-only order")
    
    class Config:
        """Pydantic config"""
        json_encoders = {
            Decimal: str
        }
        schema_extra = {
            "example": {
                "amount_of_synthetic": "0.0001",
                "price": "100000.1",
                "market_name": "BTC-USD",
                "side": "BUY",
                "post_only": False
            }
        }


class StarkOrderCancelRequest(BaseModel):
    """Stark order cancellation request model"""
    order_external_id: str = Field(..., description="External ID of the order to cancel")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "order_external_id": "order_12345"
            }
        }


class StarkOrderResponse(BaseModel):
    """Stark order response model"""
    external_id: str = Field(..., description="External order ID")
    market_name: str = Field(..., description="Market symbol")
    side: str = Field(..., description="Order side")
    amount: str = Field(..., description="Order amount")
    price: str = Field(..., description="Order price")
    post_only: bool = Field(..., description="Post-only flag")
    status: str = Field(..., description="Order status")
    order_data: Any = Field(..., description="Raw order data from Stark client")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "external_id": "order_12345",
                "market_name": "BTC-USD",
                "side": "BUY",
                "amount": "0.0001",
                "price": "100000.1",
                "post_only": False,
                "status": "placed",
                "order_data": {}
            }
        }


class StarkOrderCancelResponse(BaseModel):
    """Stark order cancellation response model"""
    external_id: str = Field(..., description="External order ID")
    status: str = Field(..., description="Cancellation status")
    result: Any = Field(..., description="Raw cancellation result from Stark client")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "external_id": "order_12345",
                "status": "cancelled",
                "result": {}
            }
        }


class StarkAccountInfoResponse(BaseModel):
    """Stark account information response model"""
    vault: int = Field(..., description="Vault ID")
    public_key: str = Field(..., description="Public key")
    api_key: Optional[str] = Field(None, description="Masked API key")
    initialized: bool = Field(..., description="Whether client is initialized")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "vault": 500029,
                "public_key": "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f",
                "api_key": "d6062722...",
                "initialized": True
            }
        }


class StarkPositionResponse(BaseModel):
    """Stark position response model"""
    id: int = Field(..., description="Position ID")
    accountId: int = Field(..., description="Account ID")
    market: str = Field(..., description="Market symbol")
    side: str = Field(..., description="Position side (LONG/SHORT)")
    leverage: str = Field(..., description="Leverage used")
    size: str = Field(..., description="Position size")
    value: str = Field(..., description="Position value")
    openPrice: str = Field(..., description="Open price")
    markPrice: str = Field(..., description="Current mark price")
    liquidationPrice: str = Field(..., description="Liquidation price")
    margin: str = Field(..., description="Margin used")
    unrealisedPnl: str = Field(..., description="Unrealized PnL")
    realisedPnl: str = Field(..., description="Realized PnL")
    tpTriggerPrice: Optional[str] = Field(None, description="Take profit trigger price")
    tpLimitPrice: Optional[str] = Field(None, description="Take profit limit price")
    slTriggerPrice: Optional[str] = Field(None, description="Stop loss trigger price")
    slLimitPrice: Optional[str] = Field(None, description="Stop loss limit price")
    adl: str = Field(..., description="ADL (Auto-Deleveraging) value")
    maxPositionSize: str = Field(..., description="Maximum position size")
    createdTime: int = Field(..., description="Creation timestamp")
    updatedTime: int = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "id": 1,
                "accountId": 1,
                "market": "BTC-USD",
                "side": "LONG",
                "leverage": "10",
                "size": "0.1",
                "value": "4000",
                "openPrice": "39000",
                "markPrice": "40000",
                "liquidationPrice": "38200",
                "margin": "20",
                "unrealisedPnl": "1000",
                "realisedPnl": "1.2",
                "tpTriggerPrice": "41000",
                "tpLimitPrice": "41500",
                "slTriggerPrice": "39500",
                "slLimitPrice": "39000",
                "adl": "2.5",
                "maxPositionSize": "0.2",
                "createdTime": 1701563440000,
                "updatedTime": 1701563440
            }
        }


class StarkOrderDetailResponse(BaseModel):
    """Stark order detail response model"""
    id: int = Field(..., description="Order ID")
    accountId: int = Field(..., description="Account ID")
    externalId: str = Field(..., description="External order ID")
    market: str = Field(..., description="Market symbol")
    type: str = Field(..., description="Order type")
    side: str = Field(..., description="Order side")
    status: str = Field(..., description="Order status")
    statusReason: Optional[str] = Field(None, description="Status reason")
    price: Optional[str] = Field(None, description="Order price")
    averagePrice: Optional[str] = Field(None, description="Average filled price")
    qty: str = Field(..., description="Order quantity")
    filledQty: Optional[str] = Field(None, description="Filled quantity")
    payedFee: Optional[str] = Field(None, description="Paid fee")
    reduceOnly: bool = Field(..., description="Reduce-only flag")
    postOnly: bool = Field(..., description="Post-only flag")
    createdTime: int = Field(..., description="Creation timestamp")
    updatedTime: int = Field(..., description="Last update timestamp")
    timeInForce: str = Field(..., description="Time in force")
    expireTime: int = Field(..., description="Expiration timestamp")
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "id": 1775511783722512384,
                "accountId": 3017,
                "externalId": "2554612759479898620327573136214120486511160383028978112799136270841501275076",
                "market": "ETH-USD",
                "type": "LIMIT",
                "side": "BUY",
                "status": "PARTIALLY_FILLED",
                "statusReason": None,
                "price": "3300",
                "averagePrice": "3297.00",
                "qty": "0.2",
                "filledQty": "0.1",
                "payedFee": "0.0120000000000000",
                "reduceOnly": False,
                "postOnly": False,
                "createdTime": 1701563440000,
                "updatedTime": 1701563440000,
                "timeInForce": "FOK",
                "expireTime": 1712754771819
            }
        } 