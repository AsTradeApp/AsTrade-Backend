"""Order service layer"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
import structlog
import asyncio
from fastapi import HTTPException

from app.services.extended_client import extended_client
from app.services.extended.extended_client import extended_trading_client
from app.models.database import User
from app.api.v1.orders.models import (
    OrderRequest,
    OrderUpdate,
    OrderCancel,
    OrdersQuery,
    TWAPOrderParams,
    ExtendedTestOrderRequest,
    OrderType,
    OrderSide,
    OrderStatus
)
from x10.perpetual.orders import OrderSide as X10OrderSide

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


async def test_extended_trading_client(user: User, test_request: ExtendedTestOrderRequest) -> Dict[str, Any]:
    """
    Test the Extended trading client functionality similar to test_order_client.py
    
    Args:
        user: Authenticated user
        test_request: Test order parameters
        
    Returns:
        Test results with account info, order placement, and cancellation results
        
    Raises:
        HTTPException: If test fails
    """
    try:
        logger.info(
            "Starting Extended trading client test",
            user_id=user.id,
            market=test_request.market_name,
            amount=test_request.amount,
            side=test_request.side
        )
        
        results = {
            "success": True,
            "steps": [],
            "account_info": None,
            "order_placed": None,
            "order_cancelled": None
        }
        
        # Step 1: Initialize and get account info
        try:
            logger.info("Step 1: Getting account information")
            account_info = await extended_trading_client.get_account_info()
            results["steps"].append({
                "step": "get_account_info",
                "success": account_info.get("success", False),
                "data": account_info
            })
            results["account_info"] = account_info
            
            if not account_info.get("success"):
                raise Exception(f"Failed to get account info: {account_info.get('error')}")
                
        except Exception as e:
            logger.error("Failed to get account info", error=str(e))
            results["steps"].append({
                "step": "get_account_info",
                "success": False,
                "error": str(e)
            })
            results["success"] = False
            return results
        
        # Step 2: Calculate order price (for demo, use a simple price calculation)
        # In a real scenario, you would get market data from orderbook
        demo_price = Decimal("65000")  # Demo price for BTC-USD
        if test_request.side == OrderSide.BUY:
            order_price = demo_price * Decimal("0.999")  # Slightly below market for buy
        else:
            order_price = demo_price * Decimal("1.001")  # Slightly above market for sell
        
        # Step 3: Place test order
        try:
            logger.info("Step 2: Placing test order")
            
            # Convert API OrderSide to X10 OrderSide
            x10_side = X10OrderSide.BUY if test_request.side == OrderSide.BUY else X10OrderSide.SELL
            
            # Generate unique external ID
            external_id = f"test_order_{user.id}_{int(asyncio.get_event_loop().time())}"
            
            order_result = await extended_trading_client.create_and_place_order(
                amount_of_synthetic=test_request.amount,
                price=order_price,
                market_name=test_request.market_name,
                side=x10_side,
                post_only=test_request.post_only,
                external_id=external_id
            )
            
            results["steps"].append({
                "step": "place_order",
                "success": order_result.get("success", False),
                "data": order_result
            })
            results["order_placed"] = order_result
            
            if not order_result.get("success"):
                raise Exception(f"Failed to place order: {order_result.get('error')}")
            
            logger.info("Order placed successfully", external_id=external_id)
            
        except Exception as e:
            logger.error("Failed to place order", error=str(e))
            results["steps"].append({
                "step": "place_order",
                "success": False,
                "error": str(e)
            })
            results["success"] = False
            # Continue to show what we managed to do
        
        # Step 4: Cancel order if auto_cancel is enabled and order was placed
        if test_request.auto_cancel and results["order_placed"] and results["order_placed"].get("success"):
            try:
                # Wait a moment before cancelling
                await asyncio.sleep(2)
                
                logger.info("Step 3: Cancelling test order")
                placed_order = results["order_placed"]["order"]
                
                cancel_result = await extended_trading_client.cancel_order(
                    order_external_id=placed_order["external_id"]
                )
                
                results["steps"].append({
                    "step": "cancel_order",
                    "success": cancel_result.get("success", False),
                    "data": cancel_result
                })
                results["order_cancelled"] = cancel_result
                
                if not cancel_result.get("success"):
                    logger.warning(f"Failed to cancel order: {cancel_result.get('error')}")
                else:
                    logger.info("Order cancelled successfully")
                    
            except Exception as e:
                logger.error("Failed to cancel order", error=str(e))
                results["steps"].append({
                    "step": "cancel_order",
                    "success": False,
                    "error": str(e)
                })
        
        # Determine overall success
        if all(step.get("success", False) for step in results["steps"]):
            results["success"] = True
            results["message"] = "All test steps completed successfully"
        else:
            results["success"] = False
            results["message"] = "Some test steps failed"
        
        logger.info(
            "Extended trading client test completed",
            user_id=user.id,
            overall_success=results["success"],
            steps_completed=len(results["steps"])
        )
        
        return results
        
    except Exception as e:
        logger.error(
            "Extended trading client test failed",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Extended trading client test failed: {str(e)}"
        ) 