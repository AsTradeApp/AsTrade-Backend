"""Base service class for common patterns"""
from typing import Any, Callable, Optional, TypeVar, Generic
from fastapi import HTTPException
import structlog
import time
from .logging import APILogger, service_logger

T = TypeVar('T')


class BaseService:
    """Base service class with common patterns and utilities"""
    
    def __init__(self, service_name: str):
        """
        Initialize base service.
        
        Args:
            service_name: Name of the service for logging purposes
        """
        self.service_name = service_name
        self.logger = APILogger(service_name)
    
    async def safe_execute(
        self, 
        operation: str, 
        func: Callable[..., T], 
        *args, 
        **kwargs
    ) -> T:
        """
        Execute a function safely with error handling and logging.
        
        Args:
            operation: Description of the operation
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            HTTPException: On operation failure
        """
        start_time = time.time()
        self.logger.operation_started(operation)
        
        try:
            result = await func(*args, **kwargs) if callable(func) else func
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.operation_success(operation, duration_ms=duration_ms)
            self.logger.performance_warning(operation, duration_ms)
            
            return result
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.operation_failed(operation, e, duration_ms=duration_ms)
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to {operation}"
            )
    
    async def safe_db_operation(
        self,
        operation: str,
        table: str,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute a database operation safely with specific DB logging.
        
        Args:
            operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
            table: Table name
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        try:
            result = await func(*args, **kwargs) if callable(func) else func
            self.logger.database_operation(operation, table, True)
            return result
            
        except Exception as e:
            self.logger.database_operation(operation, table, False, error=str(e))
            raise
    
    def validate_required_params(self, **params: Any) -> None:
        """
        Validate required parameters.
        
        Args:
            **params: Parameters to validate
            
        Raises:
            HTTPException: If validation fails
        """
        for param_name, param_value in params.items():
            if param_value is None or param_value == "":
                self.logger.validation_error(param_name, param_value, "Required parameter is missing")
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameter: {param_name}"
                )
    
    def log_user_action(self, user_id: str, action: str, success: bool = True, **context: Any) -> None:
        """
        Log user action for audit purposes.
        
        Args:
            user_id: User identifier
            action: Action performed
            success: Whether the action was successful
            **context: Additional context
        """
        self.logger.user_action(user_id, action, success, service=self.service_name, **context)
    
    def handle_external_api_error(self, service_name: str, endpoint: str, error: Exception) -> HTTPException:
        """
        Handle external API errors consistently.
        
        Args:
            service_name: External service name
            endpoint: API endpoint
            error: Exception from external API
            
        Returns:
            HTTPException with appropriate error message
        """
        self.logger.external_api_error(service_name, endpoint, error)
        return HTTPException(
            status_code=503,
            detail=f"External service {service_name} is unavailable"
        )


class CachedService(BaseService):
    """Base service with simple caching capabilities"""
    
    def __init__(self, service_name: str, cache_ttl: int = 300):
        """
        Initialize cached service.
        
        Args:
            service_name: Name of the service
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        super().__init__(service_name)
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache:
            return False
        
        cache_entry = self.cache[key]
        return time.time() - cache_entry['timestamp'] < self.cache_ttl
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if valid"""
        if self._is_cache_valid(key):
            self.logger.logger.debug("Cache hit", key=key, service=self.service_name)
            return self.cache[key]['value']
        
        self.logger.logger.debug("Cache miss", key=key, service=self.service_name)
        return None
    
    def set_cache(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self.logger.logger.debug("Cache set", key=key, service=self.service_name)
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries, optionally by pattern"""
        if pattern:
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
            self.logger.logger.info("Partial cache cleared", pattern=pattern, service=self.service_name)
        else:
            self.cache.clear()
            self.logger.logger.info("Cache cleared", service=self.service_name) 