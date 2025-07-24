"""Account endpoints"""
from fastapi import APIRouter, Depends
import structlog

from app.models.responses import SuccessResponse
from app.models.database import User
from app.services.database import get_current_user
from app.api.v1.accounts.service import get_user_balance

logger = structlog.get_logger()
router = APIRouter(prefix="/account")


@router.get("/balance", response_model=SuccessResponse, summary="Get account balance")
async def get_account_balance(current_user: User = Depends(get_current_user)):
    """
    Get current account balance information for the authenticated user.
    
    Headers:
        X-User-ID: UUID of the user (required)
    
    Returns:
        Account balance with total, available, and reserved amounts
        Unrealized PnL from open positions
        User information
    """
    response = await get_user_balance(current_user)
    return SuccessResponse(data=response.dict()) 