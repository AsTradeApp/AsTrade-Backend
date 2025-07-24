from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Header, HTTPException, Depends
from app.config.settings import settings
from app.models.database import Base, User
import os

# Create engine (SQLite for local development)
engine = create_engine(
    "sqlite:///./astrade.db",
    connect_args={"check_same_thread": False}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(x_user_id: str = Header(None, alias="X-User-ID")) -> str:
    """
    Extract and validate user ID from X-User-ID header.
    
    Args:
        x_user_id: User ID from X-User-ID header
        
    Returns:
        Validated user ID
        
    Raises:
        HTTPException: If header is missing or invalid
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-ID header is required"
        )
    
    return x_user_id


def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from database using X-User-ID header.
    
    Args:
        user_id: User ID from header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine) 