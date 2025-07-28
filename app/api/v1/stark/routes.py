"""Stark trading endpoints"""
from fastapi import APIRouter
import structlog

from app.models.responses import SuccessResponse
from app.api.v1.stark.models import (
    StarkOrderRequest,
    StarkOrderCancelRequest,
    StarkOrderResponse,
    StarkOrderCancelResponse,
    StarkAccountInfoResponse
)
from app.api.v1.stark.service import (
    create_stark_order,
    cancel_stark_order,
    get_stark_account_info,
    initialize_stark_client
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
        return SuccessResponse(data={
            "status": "healthy",
            "service": "stark_trading",
            "account_configured": account_info.vault is not None,
            "client_initialized": account_info.initialized
        })
    except Exception as e:
        logger.error("Stark trading health check failed", error=str(e))
        return SuccessResponse(data={
            "status": "unhealthy",
            "service": "stark_trading",
            "error": str(e)
        }) 