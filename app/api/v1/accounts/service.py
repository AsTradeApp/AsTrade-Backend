"""Account service layer"""
from typing import Dict, Any
import structlog
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.database import User
from app.services.extended_client import extended_client
from app.api.v1.accounts.models import (
    AccountBalance,
    AccountPosition,
    AccountSummary,
    UserInfo,
    AccountBalanceResponse
)

logger = structlog.get_logger()


async def get_user_balance(user: User) -> AccountBalanceResponse:
    """
    Get user balance information.
    
    Args:
        user: User model from database
        
    Returns:
        Combined user info and balance data
        
    Raises:
        HTTPException: If balance fetch fails
    """
    try:
        logger.info("Fetching account balance", user_id=user.id, email=user.email)
        
        # Get balance data from Extended Exchange
        balance_data = await extended_client.get_account_balance()
        
        # Convert to Pydantic model
        balance = AccountBalance(**balance_data)
        
        # Create user info
        user_info = UserInfo(
            user_id=str(user.id),
            email=user.email,
            provider=user.provider,
            wallet_address=user.wallet_address
        )
        
        # Combine into response
        response = AccountBalanceResponse(
            user_info=user_info,
            balance=balance
        )
        
        logger.info("Account balance fetched successfully", user_id=user.id)
        return response
        
    except Exception as e:
        logger.error("Failed to fetch account balance", user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch account balance") 