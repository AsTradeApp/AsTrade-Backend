from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from decimal import Decimal
import structlog

from app.services.extended_client import extended_client
from app.models.responses import SuccessResponse
from app.models.accounts import (
    Balance, Position, PositionHistory, AccountSummary, 
    LeverageInfo, FeeStructure, LeverageRequest, PositionRequest
)

logger = structlog.get_logger()
router = APIRouter(prefix="/account")


@router.get("/balance", response_model=SuccessResponse, summary="Get account balance")
async def get_account_balance():
    """
    Get current account balance information.
    
    Returns:
        Account balance with total, available, and reserved amounts
        Unrealized PnL from open positions
    """
    try:
        logger.info("Fetching account balance")
        balance_data = await extended_client.get_account_balance()
        
        logger.info("Account balance fetched successfully")
        return SuccessResponse(data=balance_data)
        
    except Exception as e:
        logger.error("Failed to fetch account balance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch account balance")


@router.get("/positions", response_model=SuccessResponse, summary="Get open positions")
async def get_positions(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol")
):
    """
    Get all open positions or positions for a specific symbol.
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
    
    Returns:
        List of open positions with entry price, mark price, PnL, and margin info
    """
    try:
        logger.info("Fetching positions", symbol=symbol)
        positions_data = await extended_client.get_positions(symbol)
        
        logger.info("Positions fetched successfully", symbol=symbol, 
                   count=len(positions_data))
        return SuccessResponse(data=positions_data)
        
    except Exception as e:
        logger.error("Failed to fetch positions", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch positions")


@router.get("/positions/history", response_model=SuccessResponse, summary="Get position history")
async def get_position_history(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    cursor: Optional[int] = Query(default=None, description="Pagination cursor")
):
    """
    Get historical positions (closed positions).
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
        limit: Number of records to return (1-1000)
        cursor: Pagination cursor for fetching older records
    
    Returns:
        List of closed positions with entry/exit prices, realized PnL, and duration
    """
    try:
        logger.info("Fetching position history", symbol=symbol, limit=limit, cursor=cursor)
        history_data = await extended_client.get_position_history(symbol, limit, cursor)
        
        logger.info("Position history fetched successfully", symbol=symbol,
                   count=len(history_data.get('data', [])))
        return SuccessResponse(
            data=history_data.get('data', []),
            pagination=history_data.get('pagination')
        )
        
    except Exception as e:
        logger.error("Failed to fetch position history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch position history")


@router.get("/leverage", response_model=SuccessResponse, summary="Get leverage settings")
async def get_leverage(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol")
):
    """
    Get current leverage settings for all symbols or a specific symbol.
    
    Args:
        symbol: Optional symbol filter (e.g., BTC-USD)
    
    Returns:
        Leverage information including current leverage, max leverage, and position size
    """
    try:
        logger.info("Fetching leverage settings", symbol=symbol)
        leverage_data = await extended_client.get_leverage(symbol)
        
        logger.info("Leverage settings fetched successfully", symbol=symbol)
        return SuccessResponse(data=leverage_data)
        
    except Exception as e:
        logger.error("Failed to fetch leverage settings", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch leverage settings")


@router.patch("/leverage", response_model=SuccessResponse, summary="Update leverage")
async def set_leverage(leverage_request: LeverageRequest):
    """
    Update leverage for a specific symbol.
    
    Args:
        leverage_request: Leverage update request with symbol and new leverage value
    
    Returns:
        Updated leverage information
    
    Note:
        - Leverage must be between 1 and the maximum allowed for the symbol
        - Changes may affect margin requirements for existing positions
    """
    try:
        logger.info("Updating leverage", symbol=leverage_request.symbol, 
                   leverage=leverage_request.leverage)
        
        result = await extended_client.set_leverage(
            leverage_request.symbol, 
            leverage_request.leverage
        )
        
        logger.info("Leverage updated successfully", symbol=leverage_request.symbol,
                   new_leverage=leverage_request.leverage)
        return SuccessResponse(data=result)
        
    except Exception as e:
        logger.error("Failed to update leverage", symbol=leverage_request.symbol, 
                    leverage=leverage_request.leverage, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update leverage")


@router.get("/fees", response_model=SuccessResponse, summary="Get fee structure")
async def get_fees():
    """
    Get current fee structure and trading tier information.
    
    Returns:
        Fee structure including:
        - Current maker and taker fees
        - 30-day trading volume
        - Current tier level
        - Next tier requirements (if applicable)
    """
    try:
        logger.info("Fetching fee structure")
        fees_data = await extended_client.get_fees()
        
        logger.info("Fee structure fetched successfully")
        return SuccessResponse(data=fees_data)
        
    except Exception as e:
        logger.error("Failed to fetch fee structure", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch fee structure")


@router.get("/summary", response_model=SuccessResponse, summary="Get account summary")
async def get_account_summary():
    """
    Get comprehensive account summary.
    
    Returns:
        Account summary including:
        - Total equity and available balance
        - Margin usage and ratios
        - Unrealized PnL
        - Number of open positions and orders
    """
    try:
        logger.info("Fetching account summary")
        
        # Fetch balance and positions in parallel
        balance_data = await extended_client.get_account_balance()
        positions_data = await extended_client.get_positions()
        
        # Calculate summary metrics
        total_equity = balance_data.get('total_equity', 0)
        available_balance = balance_data.get('available_balance', 0)
        used_margin = balance_data.get('used_margin', 0)
        unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions_data)
        
        summary = {
            'total_equity': total_equity,
            'available_balance': available_balance,
            'used_margin': used_margin,
            'free_margin': available_balance - used_margin,
            'margin_ratio': (used_margin / total_equity * 100) if total_equity > 0 else 0,
            'unrealized_pnl': unrealized_pnl,
            'total_positions': len(positions_data),
            'open_orders': 0  # Will be updated when orders endpoint is called
        }
        
        logger.info("Account summary calculated successfully", 
                   total_equity=total_equity, positions_count=len(positions_data))
        return SuccessResponse(data=summary)
        
    except Exception as e:
        logger.error("Failed to fetch account summary", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch account summary") 