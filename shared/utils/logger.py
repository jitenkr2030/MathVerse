"""
Logging Utilities Module

This module provides structured logging utilities for the MathVerse
platform. It implements JSON logging, context management, and
performance tracking.
"""

import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional
import json
import traceback

import structlog


# Global log level configuration
LOG_LEVEL = logging.INFO


def setup_logging(
    level: int = LOG_LEVEL,
    format_type: str = "json",
    service_name: str = "mathverse"
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level
        format_type: Output format ("json" or "plain")
        service_name: Name of the service for log context
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if format_type == "json"
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s" if format_type == "plain" else "%(message)s",
        level=level,
        stream=sys.stdout
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding temporary context to logs.
    
    Usage:
        with LogContext(user_id="user123", action="login"):
            logger.info("User action")
    """
    
    def __init__(self, **context: Any):
        """Initialize context with key-value pairs."""
        self.context = context
        self.token = None
    
    def __enter__(self) -> None:
        """Enter context and bind variables."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and unbind variables."""
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_function(
    logger: Optional[structlog.stdlib.BoundLogger] = None,
    log_args: bool = False,
    log_result: bool = False,
    log_duration: bool = True
) -> Callable:
    """
    Decorator for logging function calls.
    
    Args:
        logger: Logger instance to use
        log_args: Whether to log function arguments
        log_result: Whether to log return value
        log_duration: Whether to log execution duration
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            
            # Start timing
            start_time = time.time()
            
            # Log function call
            call_info = {"function": func.__name__}
            if log_args:
                call_info["args"] = str(args)[:200]
                call_info["kwargs"] = str(kwargs)[:200]
            
            _logger.info("Function called", **call_info)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log success
                success_info = {
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2),
                    "status": "success"
                }
                
                if log_result:
                    success_info["result"] = str(result)[:200]
                
                _logger.info("Function completed", **success_info)
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error
                _logger.error(
                    "Function failed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                    traceback=traceback.format_exc()
                )
                
                raise
        
        return wrapper
    return decorator


class LoggerMixin:
    """
    Mixin class providing logging capabilities.
    
    Usage:
        class MyService(LoggerMixin):
            def __init__(self):
                self.logger = self.get_logger()
            
            def do_something(self):
                self.logger.info("Doing something")
    """
    
    _logger: Optional[structlog.stdlib.BoundLogger] = None
    
    @classmethod
    def get_logger(cls) -> structlog.stdlib.BoundLogger:
        """Get logger for the class."""
        if cls._logger is None:
            cls._logger = get_logger(cls.__name__)
        return cls._logger


class PerformanceLogger:
    """
    Context manager for logging performance metrics.
    
    Usage:
        with PerformanceLogger(logger, "database_query"):
            # Perform operation
            results = db.query()
    """
    
    def __init__(
        self,
        logger: structlog.stdlib.BoundLogger,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize with logger and operation details."""
        self.logger = logger
        self.operation = operation
        self.context = context or {}
        self.start_time: float = 0
        self.end_time: float = 0
    
    def __enter__(self) -> "PerformanceLogger":
        """Start timing."""
        self.start_time = time.time()
        self.logger.info(
            "Performance: operation started",
            operation=self.operation,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Log completion with duration."""
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                "Performance: operation completed",
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                **self.context
            )
        else:
            self.logger.error(
                "Performance: operation failed",
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                error=str(exc_val),
                **self.context
            )


def log_performance(operation: str, logger: Optional[structlog.stdlib.BoundLogger] = None):
    """
    Decorator for logging function performance.
    
    Args:
        operation: Name of the operation for logging
        logger: Logger instance to use
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            
            start_time = time.time()
            _logger.info("Performance: starting", operation=operation)
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = (time.time() - start_time) * 1000
                _logger.info(
                    "Performance: completed",
                    operation=operation,
                    duration_ms=round(duration_ms, 2)
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                _logger.error(
                    "Performance: failed",
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator


class RequestLogger:
    """
    Middleware for logging HTTP requests.
    
    Usage:
        logger = RequestLogger(get_logger("http"))
        logger.log_request(request, response, duration_ms)
    """
    
    def __init__(self, logger: structlog.stdlib.BoundLogger):
        """Initialize with logger."""
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        """
        Log an HTTP request.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: Optional user identifier
            request_id: Optional request correlation ID
        """
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2)
        }
        
        if user_id:
            log_data["user_id"] = user_id
        if request_id:
            log_data["request_id"] = request_id
        
        if status_code < 400:
            self.logger.info("HTTP request", **log_data)
        elif status_code < 500:
            self.logger.warning("HTTP request client error", **log_data)
        else:
            self.logger.error("HTTP request server error", **log_data)
