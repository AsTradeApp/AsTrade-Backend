"""Stark trading models for API endpoints"""
from typing import Optional, Dict, Any
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