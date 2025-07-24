"""Order service layer"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
import structlog
from fastapi import HTTPException

from app.services.extended_client import extended_client
from app.models.database import User
from app.api.v1.orders.models import (
    OrderRequest,
    OrderUpdate,
    OrderCancel,
    OrdersQuery,
    TWAPOrderParams,
    OrderType,
    OrderSide,
    OrderStatus
)

logger = structlog.get_logger()


async def create_order(user: User, order_request: OrderRequest) -> Dict[str, Any]:
    """
    Create a new order.
    
    Args:
        user: Authenticated user
        order_request: Order creation request
        
    Returns:
        Created order information
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        logger.info(
            "Creating order",
            user_id=user.id,
            symbol=order_request.symbol,
            type=order_request.type,
            side=order_request.side,
            size=order_request.size
        )
        
        # Convert order request to API format
        order_data = {
            "symbol": order_request.symbol,
            "type": order_request.type.value,
            "side": order_request.side.value,
            "size": str(order_request.size),
            "time_in_force": order_request.time_in_force.value,
            "reduce_only": order_request.reduce_only,
            "post_only": order_request.post_only
        }
        
        if order_request.price:
            order_data["price"] = str(order_request.price)
        if order_request.stop_price:
            order_data["stop_price"] = str(order_request.stop_price)
        if order_request.client_id:
            order_data["client_id"] = order_request.client_id
            
        result = await extended_client.create_order(order_data)
        
        logger.info(
            "Order created successfully",
            user_id=user.id,
            order_id=result.get('id'),
            symbol=order_request.symbol
        )
        return result
        
    except Exception as e:
        logger.error(
            "Failed to create order",
            user_id=user.id,
            symbol=order_request.symbol,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to create order")


async def get_orders(user: User, query: OrdersQuery) -> Dict[str, Any]:
    """
    Get user orders.
    
    Args:
        user: Authenticated user
        query: Order query parameters
        
    Returns:
        List of orders with pagination
        
    Raises:
        HTTPException: If orders fetch fails
    """
    try:
        logger.info(
            "Fetching orders",
            user_id=user.id,
            symbol=query.symbol,
            status=query.status
        )
        
        result = await extended_client.get_orders(
            symbol=query.symbol,
            status=query.status.value if query.status else None,
            limit=query.limit,
            cursor=query.cursor
        )
        
        logger.info(
            "Orders fetched successfully",
            user_id=user.id,
            count=len(result.get('data', []))
        )
        return result
        
    except Exception as e:
        logger.error(
            "Failed to fetch orders",
            user_id=user.id,
            symbol=query.symbol,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to fetch orders") 