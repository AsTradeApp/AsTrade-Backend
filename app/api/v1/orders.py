from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
import structlog

from app.services.extended_client import extended_client
from app.models.responses import SuccessResponse
from app.models.orders import (
    Order, OrderRequest, OrderUpdate, OrderCancel, OrdersQuery,
    TradeExecution, TWAPOrderParams, OrderType, OrderSide, OrderStatus
)

logger = structlog.get_logger()
router = APIRouter(prefix="/orders")


@router.post("/", response_model=SuccessResponse, summary="Create new order")
async def create_order(order_request: OrderRequest):
    """
    Create a new trading order.
    
    Args:
        order_request: Order creation request with all order parameters
    
    Returns:
        Created order information with order ID and status
    
    Order Types:
        - limit: Limit order with specified price
        - market: Market order executed immediately at best available price
        - stop_limit: Stop-limit order triggered when stop price is reached
        - stop_market: Stop-market order triggered when stop price is reached
        - twap: Time-weighted average price order
    """
    try:
        logger.info("Creating order", 
                   symbol=order_request.symbol,
                   type=order_request.type,
                   side=order_request.side,
                   size=order_request.size,
                   price=order_request.price)
        
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
        
        logger.info("Order created successfully", 
                   order_id=result.get('id'),
                   symbol=order_request.symbol,
                   status=result.get('status'))
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to create order", 
                    symbol=order_request.symbol,
                    type=order_request.type,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create order")


@router.get("/", response_model=SuccessResponse, summary="Get orders")
async def get_orders(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    status: Optional[OrderStatus] = Query(default=None, description="Filter by order status"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of orders to return"),
    cursor: Optional[int] = Query(default=None, description="Pagination cursor")
):
    """
    Get orders based on filters.
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
        status: Optional status filter (pending, open, filled, cancelled, etc.)
        limit: Number of orders to return (1-1000)
        cursor: Pagination cursor for fetching older orders
    
    Returns:
        List of orders matching the filters
    """
    try:
        logger.info("Fetching orders", symbol=symbol, status=status, 
                   limit=limit, cursor=cursor)
        
        status_str = status.value if status else None
        orders_data = await extended_client.get_orders(
            symbol=symbol,
            status=status_str,
            limit=limit,
            cursor=cursor
        )
        
        logger.info("Orders fetched successfully", symbol=symbol, status=status,
                   count=len(orders_data.get('data', [])))
        return SuccessResponse(
            data=orders_data.get('data', []),
            pagination=orders_data.get('pagination')
        )
        
    except Exception as e:
        logger.error("Failed to fetch orders", symbol=symbol, status=status, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch orders")


@router.get("/history", response_model=SuccessResponse, summary="Get order history")
async def get_order_history(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of orders to return"),
    cursor: Optional[int] = Query(default=None, description="Pagination cursor")
):
    """
    Get historical orders (filled, cancelled, rejected orders).
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
        limit: Number of orders to return (1-1000)
        cursor: Pagination cursor for fetching older orders
    
    Returns:
        List of historical orders
    """
    try:
        logger.info("Fetching order history", symbol=symbol, limit=limit, cursor=cursor)
        
        history_data = await extended_client.get_order_history(
            symbol=symbol,
            limit=limit,
            cursor=cursor
        )
        
        logger.info("Order history fetched successfully", symbol=symbol,
                   count=len(history_data.get('data', [])))
        return SuccessResponse(
            data=history_data.get('data', []),
            pagination=history_data.get('pagination')
        )
        
    except Exception as e:
        logger.error("Failed to fetch order history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch order history")


@router.patch("/{order_id}", response_model=SuccessResponse, summary="Update order")
async def update_order(order_id: str, order_update: OrderUpdate):
    """
    Update an existing order.
    
    Args:
        order_id: ID of the order to update
        order_update: Order update parameters
    
    Returns:
        Updated order information
    
    Note:
        Only certain order parameters can be updated (size, price, stop_price)
        Order must be in 'open' or 'pending' status to be updated
    """
    try:
        logger.info("Updating order", order_id=order_id, 
                   size=order_update.size, price=order_update.price)
        
        # Convert update request to API format
        update_data = {}
        if order_update.size:
            update_data["size"] = str(order_update.size)
        if order_update.price:
            update_data["price"] = str(order_update.price)
        if order_update.stop_price:
            update_data["stop_price"] = str(order_update.stop_price)
        
        result = await extended_client.update_order(order_id, update_data)
        
        logger.info("Order updated successfully", order_id=order_id)
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to update order", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update order")


@router.delete("/{order_id}", response_model=SuccessResponse, summary="Cancel order")
async def cancel_order(order_id: str):
    """
    Cancel a specific order.
    
    Args:
        order_id: ID of the order to cancel
    
    Returns:
        Cancellation confirmation
    """
    try:
        logger.info("Cancelling order", order_id=order_id)
        
        result = await extended_client.cancel_order(order_id)
        
        logger.info("Order cancelled successfully", order_id=order_id)
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to cancel order", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel order")


@router.delete("/", response_model=SuccessResponse, summary="Cancel all orders")
async def cancel_all_orders(
    symbol: Optional[str] = Query(default=None, description="Cancel orders for specific symbol only")
):
    """
    Cancel all open orders or all orders for a specific symbol.
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD). If not provided, cancels all orders
    
    Returns:
        Mass cancellation confirmation with number of cancelled orders
    """
    try:
        logger.info("Cancelling all orders", symbol=symbol)
        
        result = await extended_client.cancel_all_orders(symbol)
        
        logger.info("Orders cancelled successfully", symbol=symbol, 
                   cancelled_count=result.get('cancelled_count', 0))
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to cancel orders", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel orders")


@router.get("/trades", response_model=SuccessResponse, summary="Get trade history")
async def get_trades(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of trades to return"),
    cursor: Optional[int] = Query(default=None, description="Pagination cursor")
):
    """
    Get trade execution history.
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
        limit: Number of trades to return (1-1000)
        cursor: Pagination cursor for fetching older trades
    
    Returns:
        List of executed trades with order IDs, prices, sizes, and fees
    """
    try:
        logger.info("Fetching trade history", symbol=symbol, limit=limit, cursor=cursor)
        
        trades_data = await extended_client.get_trades_history(
            symbol=symbol,
            limit=limit,
            cursor=cursor
        )
        
        logger.info("Trade history fetched successfully", symbol=symbol,
                   count=len(trades_data.get('data', [])))
        return SuccessResponse(
            data=trades_data.get('data', []),
            pagination=trades_data.get('pagination')
        )
        
    except Exception as e:
        logger.error("Failed to fetch trade history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch trade history")


@router.post("/twap", response_model=SuccessResponse, summary="Create TWAP order")
async def create_twap_order(
    order_request: OrderRequest,
    twap_params: TWAPOrderParams = Body(..., description="TWAP-specific parameters")
):
    """
    Create a Time-Weighted Average Price (TWAP) order.
    
    Args:
        order_request: Base order parameters (must have type=twap)
        twap_params: TWAP-specific parameters (duration, interval, randomization)
    
    Returns:
        Created TWAP order information
    
    TWAP Parameters:
        - duration: Total time to execute the order (60 seconds to 24 hours)
        - interval: Time between each slice execution (10 seconds to 1 hour)
        - randomize: Whether to randomize slice timing to reduce market impact
    """
    try:
        if order_request.type != OrderType.TWAP:
            raise HTTPException(status_code=400, detail="Order type must be 'twap' for TWAP orders")
        
        logger.info("Creating TWAP order", 
                   symbol=order_request.symbol,
                   side=order_request.side,
                   size=order_request.size,
                   duration=twap_params.duration,
                   interval=twap_params.interval)
        
        # Convert to API format
        order_data = {
            "symbol": order_request.symbol,
            "type": "twap",
            "side": order_request.side.value,
            "size": str(order_request.size),
            "twap_params": {
                "duration": twap_params.duration,
                "interval": twap_params.interval,
                "randomize": twap_params.randomize
            }
        }
        
        if order_request.client_id:
            order_data["client_id"] = order_request.client_id
        
        result = await extended_client.create_order(order_data)
        
        logger.info("TWAP order created successfully", 
                   order_id=result.get('id'),
                   symbol=order_request.symbol)
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to create TWAP order", 
                    symbol=order_request.symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create TWAP order") 