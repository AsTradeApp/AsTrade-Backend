from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import structlog
import secrets
import uuid

from app.services.database import get_db
from app.models.responses import SuccessResponse
from app.models.users import UserCreateRequest, UserCreateResponse
from app.models.database import User, UserApiCredentials

logger = structlog.get_logger()
router = APIRouter(prefix="/users")


@router.post("/", response_model=SuccessResponse, summary="Create a new user")
async def create_user(
    user_request: UserCreateRequest,
    db = Depends(get_db)
):
    """
    Create a new user and generate StarkEx private key.
    
    Args:
        user_request: User creation request with optional email and username
        db: Database session
    
    Returns:
        User creation response with user_id and generated stark_private_key
    """
    try:
        logger.info("Creating new user", email=user_request.email)
        
        # Generate StarkEx private key (temporary implementation)
        # TODO: Replace with proper starkbank.ecdsa.PrivateKey implementation
        stark_private_key_str = f"0x{secrets.token_hex(32)}"
        
        logger.info("Generated StarkEx private key")
        
        # Create user in database
        db_user = User(
            email=user_request.email
        )
        
        db.add(db_user)
        db.flush()  # Flush to get the user ID
        
        # Create user API credentials
        db_credentials = UserApiCredentials(
            user_id=db_user.id,
            extended_stark_private_key=stark_private_key_str,
            environment="testnet",
            is_mock_enabled=True
        )
        
        db.add(db_credentials)
        db.commit()
        
        logger.info("User created successfully", user_id=str(db_user.id))
        
        # Prepare response (without exposing private key)
        response_data = UserCreateResponse(
            user_id=db_user.id,
            message="User created successfully"
        )
        
        return SuccessResponse(data=response_data.dict())
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/{user_id}", response_model=SuccessResponse, summary="Get user by ID")
async def get_user(user_id: str, db = Depends(get_db)):
    """
    Get user information by user ID.
    
    Args:
        user_id: UUID of the user
        db: Database session
    
    Returns:
        User information without sensitive data
    """
    try:
        # Query user from database
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare response (without sensitive data)
        response_data = {
            "user_id": str(db_user.id),
            "email": db_user.email,
            "created_at": db_user.created_at.isoformat(),
            "has_api_credentials": db_user.api_credentials is not None
        }
        
        return SuccessResponse(data=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user") 