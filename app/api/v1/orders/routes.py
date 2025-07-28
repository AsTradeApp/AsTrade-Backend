"""Order endpoints"""
from fastapi import APIRouter, Depends, Query
import structlog

from app.models.responses import SuccessResponse
from app.services.database import get_supabase
from app.api.v1.orders.models import (
    OrderRequest,
    OrdersQuery,
    OrderStatus,
    ExtendedTestOrderRequest
)
from app.api.v1.orders.service import (
    create_order,
    get_orders,
    test_extended_trading_client
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=SuccessResponse, summary="Create new order")
async def create_new_order(
    order_request: OrderRequest,
    db = Depends(get_supabase)
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
    db = Depends(get_supabase)
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
    result = await get_orders(db, query)
    return SuccessResponse(
        data=result.get('data', []),
        pagination=result.get('pagination')
    )


@router.post("/test-extended", response_model=SuccessResponse, summary="Test Extended Trading Client")
async def test_extended_client(
    test_request: ExtendedTestOrderRequest = ExtendedTestOrderRequest(),
    current_user: User = Depends(get_current_user)
):
    """
    Test the Extended trading client functionality.
    
    This endpoint tests the full Extended trading flow similar to test_order_client.py:
    1. Initialize the Extended trading client
    2. Get account information
    3. Place a test order with the specified parameters
    4. Optionally cancel the order automatically
    
    Args:
        test_request: Test order parameters (optional, uses defaults if not provided)
    
    Returns:
        Test results including:
        - Account information
        - Order placement result
        - Order cancellation result (if auto_cancel is enabled)
        - Step-by-step execution log
    
    **Environment Variables Required:**
    - EXTENDED_API_KEY: Your Extended API key
    - EXTENDED_SECRET_KEY: Your Extended secret key
    - EXTENDED_STARK_PRIVATE_KEY: Your Stark private key
    - EXTENDED_VAULT_ID: Your vault ID
    
    **Default Test Parameters:**
    - Market: BTC-USD
    - Amount: 0.001 BTC
    - Side: BUY
    - Post Only: True
    - Auto Cancel: True
    """
    result = await test_extended_trading_client(current_user, test_request)
    return SuccessResponse(data=result)


@router.post("/test-extended-demo", response_model=SuccessResponse, summary="Demo Extended Trading Client (No Auth)")
async def test_extended_client_demo(
    test_request: ExtendedTestOrderRequest = ExtendedTestOrderRequest()
):
    """
    Demo endpoint to test the Extended trading client functionality without authentication.
    
    This endpoint tests the full Extended trading flow similar to test_order_client.py:
    1. Initialize the Extended trading client
    2. Get account information  
    3. Place a test order with the specified parameters
    4. Optionally cancel the order automatically
    
    **⚠️ Note: This is a demo endpoint that doesn't require authentication.**
    **Use /test-extended for production with proper user authentication.**
    
    Args:
        test_request: Test order parameters (optional, uses defaults if not provided)
    
    Returns:
        Test results including:
        - Account information
        - Order placement result
        - Order cancellation result (if auto_cancel is enabled)
        - Step-by-step execution log
    
    **Environment Variables Required:**
    - EXTENDED_API_KEY: Your Extended API key
    - EXTENDED_SECRET_KEY: Your Extended secret key
    - EXTENDED_STARK_PRIVATE_KEY: Your Stark private key
    - EXTENDED_VAULT_ID: Your vault ID
    
    **Default Test Parameters:**
    - Market: BTC-USD
    - Amount: 0.001 BTC
    - Side: BUY
    - Post Only: True
    - Auto Cancel: True
    """
    # Create a mock user for testing
    from app.models.database import User
    mock_user = User(
        id="demo_user_123",
        email="demo@astrade.com",
        username="demo_user",
        is_active=True
    )
    
    result = await test_extended_trading_client(mock_user, test_request)
    return SuccessResponse(data=result) 