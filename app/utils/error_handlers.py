"""Centralized error handling utilities"""
import functools
from typing import Callable, Any
from fastapi import HTTPException
import structlog

logger = structlog.get_logger()


def handle_api_errors(operation_name: str):
    """
    Decorator to handle API errors consistently.
    
    Args:
        operation_name: Description of the operation for error messages
        
    Usage:
        @handle_api_errors("get markets")
        async def get_markets():
            # Your logic here without try/catch
            return data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as they are already handled
                raise
            except Exception as e:
                logger.error(f"Failed to {operation_name}", error=str(e))
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to {operation_name}"
                )
        return wrapper
    return decorator


def handle_service_errors(operation_name: str, include_context: bool = True):
    """
    Decorator for service layer error handling with optional context.
    
    Args:
        operation_name: Description of the operation
        include_context: Whether to include additional context in error
        
    Usage:
        @handle_service_errors("process user data", include_context=True)
        async def process_user(user_id: str):
            # Your logic here
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract context from function arguments if requested
                context = {}
                if include_context and args:
                    # Try to extract common identifiers
                    if len(args) > 0 and hasattr(args[0], '__dict__'):
                        # For class methods, skip 'self'
                        func_args = args[1:] if 'self' in str(args[0]) else args
                    else:
                        func_args = args
                    
                    # Add first few arguments as context
                    for i, arg in enumerate(func_args[:3]):
                        if isinstance(arg, (str, int, float)):
                            context[f"arg_{i}"] = arg
                
                logger.error(
                    f"Service error: {operation_name}", 
                    error=str(e),
                    **context
                )
                raise
        return wrapper
    return decorator


class APIErrorHandler:
    """Centralized error handling class for common error patterns"""
    
    @staticmethod
    def handle_not_found(resource_name: str, identifier: str = None) -> HTTPException:
        """Handle resource not found errors"""
        detail = f"{resource_name} not found"
        if identifier:
            detail += f" (ID: {identifier})"
        return HTTPException(status_code=404, detail=detail)
    
    @staticmethod
    def handle_validation_error(message: str) -> HTTPException:
        """Handle validation errors"""
        return HTTPException(status_code=400, detail=f"Validation error: {message}")
    
    @staticmethod
    def handle_unauthorized(message: str = "Unauthorized") -> HTTPException:
        """Handle unauthorized access"""
        return HTTPException(status_code=401, detail=message)
    
    @staticmethod
    def handle_forbidden(message: str = "Forbidden") -> HTTPException:
        """Handle forbidden access"""
        return HTTPException(status_code=403, detail=message) 