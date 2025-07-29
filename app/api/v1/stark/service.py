"""Stark trading service layer"""
from typing import Dict, Any, List, Optional
import structlog
from fastapi import HTTPException

from app.services.stark_trading_client import stark_trading_service, StarkTradingClientError
from app.api.v1.stark.models import (
    StarkOrderRequest,
    StarkOrderCancelRequest,
    StarkOrderResponse,
    StarkOrderCancelResponse,
    StarkAccountInfoResponse,
    StarkPositionResponse,
    StarkOrderDetailResponse
)

logger = structlog.get_logger()


async def create_stark_order(order_request: StarkOrderRequest) -> StarkOrderResponse:
    """
    Create a new Stark order.
    
    Args:
        order_request: Stark order creation request
        
    Returns:
        Created order information
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        logger.info(
            "Creating Stark order",
            amount=order_request.amount_of_synthetic,
            price=order_request.price,
            market=order_request.market_name,
            side=order_request.side,
            post_only=order_request.post_only
        )
        
        # Call the trading service
        result = await stark_trading_service.create_order(
            amount_of_synthetic=order_request.amount_of_synthetic,
            price=order_request.price,
            market_name=order_request.market_name,
            side=order_request.side.value,
            post_only=order_request.post_only
        )
        
        # Convert to response model
        return StarkOrderResponse(**result)
        
    except StarkTradingClientError as e:
        logger.error("Stark trading client error", error=str(e))
        raise HTTPException(status_code=400, detail=f"Trading error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error creating Stark order", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def cancel_stark_order(cancel_request: StarkOrderCancelRequest) -> StarkOrderCancelResponse:
    """
    Cancel an existing Stark order.
    
    Args:
        cancel_request: Order cancellation request
        
    Returns:
        Cancellation status information
        
    Raises:
        HTTPException: If order cancellation fails
    """
    try:
        logger.info(
            "Cancelling Stark order",
            order_id=cancel_request.order_external_id
        )
        
        # Call the trading service
        result = await stark_trading_service.cancel_order(
            order_external_id=cancel_request.order_external_id
        )
        
        # Convert to response model
        return StarkOrderCancelResponse(**result)
        
    except StarkTradingClientError as e:
        logger.error("Stark trading client error", error=str(e))
        raise HTTPException(status_code=400, detail=f"Trading error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error cancelling Stark order", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_stark_positions(market: Optional[str] = None) -> List[StarkPositionResponse]:
    """
    Get user positions from Stark API.
    
    Args:
        market: Optional market filter
        
    Returns:
        List of position information
        
    Raises:
        HTTPException: If getting positions fails
    """
    try:
        logger.info("Getting Stark positions", market=market, market_type=type(market))
        
        # Call the trading service
        positions_data = await stark_trading_service.get_positions(market=market)
        
        # Convert to response models
        positions = []
        for position_data in positions_data:
            try:
                position = StarkPositionResponse(**position_data)
                positions.append(position)
            except Exception as e:
                logger.warning("Failed to parse position data", error=str(e), data=position_data)
                continue
        
        logger.info("Successfully retrieved positions", count=len(positions))
        return positions
        
    except StarkTradingClientError as e:
        logger.error("Stark trading client error", error=str(e))
        raise HTTPException(status_code=400, detail=f"Trading error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error getting Stark positions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_stark_orders(
    market: Optional[str] = None, 
    order_type: Optional[str] = None, 
    side: Optional[str] = None
) -> List[StarkOrderDetailResponse]:
    """
    Get user orders from Stark API.
    
    Args:
        market: Optional market filter
        type: Optional order type filter
        side: Optional order side filter
        
    Returns:
        List of order information
        
    Raises:
        HTTPException: If getting orders fails
    """
    try:
        logger.info("Getting Stark orders", market=market, market_type=type(market), order_type=order_type, side=side)
        
        # Call the trading service
        orders_data = await stark_trading_service.get_orders(
            market=market, 
            order_type=order_type, 
            side=side
        )
        
        # Convert to response models
        orders = []
        for order_data in orders_data:
            try:
                order = StarkOrderDetailResponse(**order_data)
                orders.append(order)
            except Exception as e:
                logger.warning("Failed to parse order data", error=str(e), data=order_data)
                continue
        
        logger.info("Successfully retrieved orders", count=len(orders))
        return orders
        
    except StarkTradingClientError as e:
        logger.error("Stark trading client error", error=str(e))
        raise HTTPException(status_code=400, detail=f"Trading error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error getting Stark orders", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_stark_account_info() -> StarkAccountInfoResponse:
    """
    Get Stark account information.
    
    Returns:
        Account information
        
    Raises:
        HTTPException: If getting account info fails
    """
    try:
        logger.info("Getting Stark account information")
        
        # Call the trading service
        result = await stark_trading_service.get_account_info()
        
        # Convert to response model
        return StarkAccountInfoResponse(**result)
        
    except Exception as e:
        logger.error("Error getting Stark account information", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def initialize_stark_client() -> Dict[str, Any]:
    """
    Initialize the Stark trading client.
    
    Returns:
        Initialization status
        
    Raises:
        HTTPException: If client initialization fails
    """
    try:
        logger.info("Initializing Stark trading client")
        
        # Initialize the client
        client = await stark_trading_service.initialize_client()
        
        return {
            "status": "initialized",
            "message": "Stark trading client initialized successfully",
            "client_initialized": client is not None
        }
        
    except StarkTradingClientError as e:
        logger.error("Stark trading client initialization error", error=str(e))
        raise HTTPException(status_code=400, detail=f"Initialization error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error initializing Stark client", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 