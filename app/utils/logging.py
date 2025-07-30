"""Standardized logging utilities"""
import structlog
from typing import Any, Dict, Optional


class APILogger:
    """Centralized logging utility for consistent log formatting"""
    
    def __init__(self, name: Optional[str] = None):
        """Initialize logger with optional name"""
        self.logger = structlog.get_logger(name) if name else structlog.get_logger()
    
    def error_with_context(self, message: str, error: Exception, **context: Any) -> None:
        """
        Log error with consistent formatting and context.
        
        Args:
            message: Error message
            error: Exception object
            **context: Additional context (user_id, operation, etc.)
        """
        self.logger.error(message, error=str(error), **context)
    
    def operation_failed(self, operation: str, error: Exception, **context: Any) -> None:
        """
        Log failed operation with standardized format.
        
        Args:
            operation: Description of the failed operation
            error: Exception object
            **context: Additional context
        """
        self.error_with_context(f"Failed to {operation}", error, **context)
    
    def operation_success(self, operation: str, **context: Any) -> None:
        """
        Log successful operation.
        
        Args:
            operation: Description of the successful operation
            **context: Additional context
        """
        self.logger.info(f"Successfully {operation}", **context)
    
    def operation_started(self, operation: str, **context: Any) -> None:
        """
        Log operation start.
        
        Args:
            operation: Description of the operation
            **context: Additional context
        """
        self.logger.info(f"Starting {operation}", **context)
    
    def validation_error(self, field: str, value: Any, reason: str, **context: Any) -> None:
        """
        Log validation errors with consistent format.
        
        Args:
            field: Field that failed validation
            value: Invalid value
            reason: Reason for validation failure
            **context: Additional context
        """
        self.logger.warning(
            "Validation failed",
            field=field,
            value=str(value),
            reason=reason,
            **context
        )
    
    def external_api_error(self, service: str, endpoint: str, error: Exception, **context: Any) -> None:
        """
        Log external API errors with consistent format.
        
        Args:
            service: External service name (e.g., "Extended Exchange")
            endpoint: API endpoint that failed
            error: Exception object
            **context: Additional context
        """
        self.logger.error(
            "External API error",
            service=service,
            endpoint=endpoint,
            error=str(error),
            **context
        )
    
    def user_action(self, user_id: str, action: str, success: bool, **context: Any) -> None:
        """
        Log user actions for audit purposes.
        
        Args:
            user_id: User identifier
            action: Action performed
            success: Whether the action was successful
            **context: Additional context
        """
        log_method = self.logger.info if success else self.logger.warning
        log_method(
            "User action",
            user_id=user_id,
            action=action,
            success=success,
            **context
        )
    
    def performance_warning(self, operation: str, duration_ms: float, threshold_ms: float = 1000, **context: Any) -> None:
        """
        Log performance warnings for slow operations.
        
        Args:
            operation: Operation that was slow
            duration_ms: Duration in milliseconds
            threshold_ms: Threshold for considering operation slow
            **context: Additional context
        """
        if duration_ms > threshold_ms:
            self.logger.warning(
                "Slow operation detected",
                operation=operation,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                **context
            )
    
    def database_operation(self, operation: str, table: str, success: bool, **context: Any) -> None:
        """
        Log database operations.
        
        Args:
            operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
            table: Table name
            success: Whether the operation was successful
            **context: Additional context
        """
        log_method = self.logger.info if success else self.logger.error
        log_method(
            "Database operation",
            operation=operation,
            table=table,
            success=success,
            **context
        )


# Global logger instances for common use cases
api_logger = APILogger("api")
service_logger = APILogger("service")
db_logger = APILogger("database")


def get_logger(name: str) -> APILogger:
    """
    Get a named logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        APILogger instance
    """
    return APILogger(name) 