"""Order endpoints"""
from fastapi import APIRouter, Depends, Query
import structlog

from app.models.responses import SuccessResponse
from app.models.database import User
from app.services.database import get_current_user
from app.api.v1.orders.models import (
    OrderRequest,
    OrdersQuery,
    OrderStatus
)
from app.api.v1.orders.service import (
    create_order,
    get_orders
)

logger = structlog.get_logger()
router = APIRouter(prefix="/orders")


@router.post("/", response_model=SuccessResponse, summary="Create new order")
async def create_new_order(
    order_request: OrderRequest,
    current_user: User = Depends(get_current_user)
):
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
    result = await create_order(current_user, order_request)
    return SuccessResponse(data=result)


@router.get("/", response_model=SuccessResponse, summary="Get orders")
async def get_user_orders(
    symbol: str = Query(None, description="Filter by symbol"),
    status: OrderStatus = Query(None, description="Filter by order status"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of orders to return"),
    cursor: str = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_user)
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
    query = OrdersQuery(
        symbol=symbol,
        status=status,
        limit=limit,
        cursor=cursor
    )
    result = await get_orders(current_user, query)
    return SuccessResponse(
        data=result.get('data', []),
        pagination=result.get('pagination')
    ) 