"""Stark trading endpoints"""
from fastapi import APIRouter, WebSocket, Query
from typing import Optional, List
import structlog

from app.models.responses import SuccessResponse
from app.api.v1.stark.models import (
    StarkOrderRequest,
    StarkOrderCancelRequest,
    StarkOrderResponse,
    StarkOrderCancelResponse,
    StarkAccountInfoResponse,
    StarkPositionResponse,
    StarkOrderDetailResponse
)
from app.api.v1.stark.service import (
    create_stark_order,
    cancel_stark_order,
    get_stark_account_info,
    initialize_stark_client,
    get_stark_positions,
    get_stark_orders
)
from app.services.price_streaming_service import (
    price_streaming_service,
    handle_price_stream_websocket
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/orders", response_model=SuccessResponse, summary="Create Stark order")
async def create_order(
    order_request: StarkOrderRequest
):
    """
    Create a new Stark perpetual trading order.
    
    Args:
        order_request: Order creation request with all order parameters
    
    Returns:
        Created order information with order ID and status
    
    This endpoint allows you to place orders on Stark perpetual markets.
    The order will be executed using the configured Stark account credentials.
    
    Example request:
    ```json
    {
        "amount_of_synthetic": "0.0001",
        "price": "100000.1", 
        "market_name": "BTC-USD",
        "side": "BUY",
        "post_only": false
    }
    ```
    """
    result = await create_stark_order(order_request)
    return SuccessResponse(data=result.dict())


@router.delete("/orders/{order_external_id}", response_model=SuccessResponse, summary="Cancel Stark order")
async def cancel_order(
    order_external_id: str
):
    """
    Cancel an existing Stark order by its external ID.
    
    Args:
        order_external_id: The external ID of the order to cancel
    
    Returns:
        Cancellation status and result information
    
    This endpoint allows you to cancel a previously placed order using its external ID.
    """
    cancel_request = StarkOrderCancelRequest(order_external_id=order_external_id)
    result = await cancel_stark_order(cancel_request)
    return SuccessResponse(data=result.dict())


@router.post("/orders/cancel", response_model=SuccessResponse, summary="Cancel Stark order (POST)")
async def cancel_order_post(
    cancel_request: StarkOrderCancelRequest
):
    """
    Cancel an existing Stark order using POST method.
    
    Args:
        cancel_request: Order cancellation request with external ID
    
    Returns:
        Cancellation status and result information
    
    Alternative endpoint for cancelling orders using POST method.
    """
    result = await cancel_stark_order(cancel_request)
    return SuccessResponse(data=result.dict())


@router.get("/positions", response_model=SuccessResponse, summary="Get user positions")
async def get_positions(
    market: Optional[str] = Query(None, description="Market filter (e.g., BTC-USD)")
):
    logger.info("Positions endpoint called", market=market)
    """
    Get user positions from Stark perpetual trading.
    
    Args:
        market: Optional market filter to get positions for a specific market
    
    Returns:
        List of user positions with detailed information
    
    This endpoint retrieves all open positions for the user account.
    Each position includes information about size, leverage, PnL, and risk management settings.
    
    Example response:
    ```json
    {
        "status": "success",
        "data": [
            {
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
        ]
    }
    ```
    """
    positions = await get_stark_positions(market=market)
    return SuccessResponse(data=[position.dict() for position in positions])


@router.get("/orders", response_model=SuccessResponse, summary="Get user orders")
async def get_orders(
    market: Optional[str] = Query(None, description="Market filter (e.g., BTC-USD)"),
    type: Optional[str] = Query(None, description="Order type filter (LIMIT, CONDITIONAL, TPSL)"),
    side: Optional[str] = Query(None, description="Order side filter (BUY, SELL)")
):
    logger.info("Orders endpoint called", market=market, order_type=type, side=side)
    """
    Get user orders from Stark perpetual trading.
    
    Args:
        market: Optional market filter to get orders for a specific market
        type: Optional order type filter
        side: Optional order side filter
    
    Returns:
        List of user orders with detailed information
    
    This endpoint retrieves all orders for the user account, including open, filled, and cancelled orders.
    Each order includes information about status, quantity, price, and execution details.
    
    Example response:
    ```json
    {
        "status": "success",
        "data": [
            {
                "id": 1775511783722512384,
                "accountId": 3017,
                "externalId": "2554612759479898620327573136214120486511160383028978112799136270841501275076",
                "market": "ETH-USD",
                "type": "LIMIT",
                "side": "BUY",
                "status": "PARTIALLY_FILLED",
                "statusReason": null,
                "price": "3300",
                "averagePrice": "3297.00",
                "qty": "0.2",
                "filledQty": "0.1",
                "payedFee": "0.0120000000000000",
                "reduceOnly": false,
                "postOnly": false,
                "createdTime": 1701563440000,
                "updatedTime": 1701563440000,
                "timeInForce": "FOK",
                "expireTime": 1712754771819
            }
        ]
    }
    ```
    """
    orders = await get_stark_orders(market=market, order_type=type, side=side)
    return SuccessResponse(data=[order.dict() for order in orders])


@router.get("/account", response_model=SuccessResponse, summary="Get Stark account info")
async def get_account_info():
    """
    Get Stark account information and status.
    
    Returns:
        Account information including vault ID, public key, and initialization status
    
    This endpoint provides information about the configured Stark trading account,
    including whether the client has been initialized.
    """
    result = await get_stark_account_info()
    return SuccessResponse(data=result.dict())


@router.post("/client/initialize", response_model=SuccessResponse, summary="Initialize Stark client")
async def initialize_client():
    """
    Initialize the Stark trading client.
    
    Returns:
        Initialization status and result
    
    This endpoint initializes the Stark trading client with the configured credentials.
    It's automatically called when placing orders, but can be called manually to test connectivity.
    """
    result = await initialize_stark_client()
    return SuccessResponse(data=result)


@router.get("/health", response_model=SuccessResponse, summary="Stark trading health check")
async def health_check():
    """
    Health check endpoint for Stark trading functionality.
    
    Returns:
        Health status of the Stark trading service
    
    This endpoint checks the status of the Stark trading service and client configuration.
    """
    try:
        account_info = await get_stark_account_info()
        price_health = await price_streaming_service.health_check()
        
        return SuccessResponse(data={
            "status": "healthy",
            "service": "stark_trading",
            "account_configured": account_info.vault is not None,
            "client_initialized": account_info.initialized,
            "price_streaming": price_health
        })
    except Exception as e:
        logger.error("Stark trading health check failed", error=str(e))
        return SuccessResponse(data={
            "status": "unhealthy",
            "service": "stark_trading",
            "error": str(e)
        })


@router.websocket("/stream/prices/{symbol}")
async def websocket_price_stream(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time price streaming using x10 perpetual orderbook.
    
    Args:
        websocket: WebSocket connection
        symbol: Trading symbol (e.g., BTC-USD)
    
    This endpoint provides real-time price updates from the x10 perpetual orderbook.
    Clients will receive price updates whenever the best bid or ask changes.
    
    Example usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/stark/stream/prices/BTC-USD');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Price update:', data);
    };
    ```
    
    Message format:
    ```json
    {
        "type": "price_update",
        "symbol": "BTC-USD",
        "price": 100250.50,
        "best_bid": 100248.25,
        "best_ask": 100252.75,
        "spread": 4.50,
        "timestamp": "2024-01-01T12:00:00.000Z"
    }
    ```
    """
    await handle_price_stream_websocket(websocket, symbol)


@router.get("/stream/prices/{symbol}/current", response_model=SuccessResponse, summary="Get current price")
async def get_current_price(symbol: str):
    """
    Get the current price for a symbol without establishing a WebSocket connection.
    
    Args:
        symbol: Trading symbol (e.g., BTC-USD)
    
    Returns:
        Current price data if available
    
    This endpoint returns the last known price from the streaming service.
    If no price data is available, it will return null.
    """
    try:
        current_price = await price_streaming_service.get_current_price(symbol)
        return SuccessResponse(data=current_price)
    except Exception as e:
        logger.error("Failed to get current price", symbol=symbol, error=str(e))
        return SuccessResponse(data=None, message=f"Failed to get price for {symbol}")


@router.post("/stream/start/{symbol}", response_model=SuccessResponse, summary="Start price streaming")
async def start_price_streaming(symbol: str):
    """
    Manually start price streaming for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., BTC-USD)
    
    Returns:
        Status of the streaming service
    
    This endpoint can be used to pre-warm the price streaming service
    before clients connect via WebSocket.
    """
    try:
        success = await price_streaming_service.start_orderbook_stream(symbol)
        return SuccessResponse(data={
            "symbol": symbol,
            "streaming": success,
            "message": f"Price streaming {'started' if success else 'failed'} for {symbol}"
        })
    except Exception as e:
        logger.error("Failed to start price streaming", symbol=symbol, error=str(e))
        return SuccessResponse(data={
            "symbol": symbol,
            "streaming": False,
            "error": str(e)
        }) 