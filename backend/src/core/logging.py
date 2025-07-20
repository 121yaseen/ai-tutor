"""
Structured logging system with proper levels, formatting, and context tracking.

This module provides a centralized logging setup that supports both JSON and text
formats, request tracing, and performance monitoring for scalable applications.
"""

import logging
import logging.config
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Union
from contextvars import ContextVar
from functools import wraps

from .config import settings


# Context variables for request tracking
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_email_context: ContextVar[Optional[str]] = ContextVar('user_email', default=None)
session_id_context: ContextVar[Optional[str]] = ContextVar('session_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context information if available
        if request_id := request_id_context.get():
            log_data["request_id"] = request_id
        if user_email := user_email_context.get():
            log_data["user_email"] = user_email
        if session_id := session_id_context.get():
            log_data["session_id"] = session_id
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add performance metrics if present
        if hasattr(record, 'duration'):
            log_data["duration_ms"] = record.duration
        if hasattr(record, 'status_code'):
            log_data["status_code"] = record.status_code
        
        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Enhanced text formatter with context information."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as enhanced text."""
        # Build context string
        context_parts = []
        if request_id := request_id_context.get():
            context_parts.append(f"req_id={request_id[:8]}")
        if user_email := user_email_context.get():
            context_parts.append(f"user={user_email}")
        if session_id := session_id_context.get():
            context_parts.append(f"session={session_id[:8]}")
        
        context_str = f"[{', '.join(context_parts)}]" if context_parts else ""
        
        # Format the message
        base_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d"
        if context_str:
            base_format += f" {context_str}"
        base_format += " - %(message)s"
        
        formatter = logging.Formatter(base_format)
        return formatter.format(record)


class PerformanceLogger:
    """Logger for performance monitoring and metrics."""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_execution_time(self, operation: str, duration_ms: float, 
                          success: bool = True, **kwargs):
        """Log execution time for an operation."""
        extra_fields = {
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            **kwargs
        }
        
        level = logging.INFO if success else logging.WARNING
        message = f"Operation '{operation}' completed in {duration_ms:.2f}ms"
        
        # Create log record with extra fields
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        record.extra_fields = extra_fields
        record.duration = duration_ms
        
        self.logger.handle(record)
    
    def log_database_operation(self, query_type: str, table: str, 
                              duration_ms: float, rows_affected: int = 0):
        """Log database operation metrics."""
        self.log_execution_time(
            operation=f"db_{query_type}",
            duration_ms=duration_ms,
            table=table,
            rows_affected=rows_affected
        )
    
    def log_api_call(self, service: str, endpoint: str, duration_ms: float, 
                     status_code: int, success: bool = True):
        """Log external API call metrics."""
        extra_fields = {
            "service": service,
            "endpoint": endpoint,
            "status_code": status_code
        }
        
        self.log_execution_time(
            operation=f"api_call_{service}",
            duration_ms=duration_ms,
            success=success,
            **extra_fields
        )


def setup_logging():
    """Setup logging configuration based on settings."""
    
    # Determine formatter based on configuration
    if settings.app.log_format.lower() == "json":
        formatter_class = JSONFormatter
        formatter_args = {}
    else:
        formatter_class = TextFormatter
        formatter_args = {"format": "%(message)s"}  # TextFormatter handles its own format
    
    # Logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                **formatter_args
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "src": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "websockets": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "livekit": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "livekit.agents": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "google_genai": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "asyncio": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "performance": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": settings.app.log_level,
            "handlers": ["console"]
        }
    }
    
    logging.config.dictConfig(config)
    
    # Log initialization
    logger = logging.getLogger("src.core.logging")
    logger.info(
        "Logging system initialized",
        extra={"extra_fields": {
            "log_level": settings.app.log_level,
            "log_format": settings.app.log_format,
            "environment": settings.app.environment
        }}
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    # Ensure name starts with 'src' for proper configuration
    if not name.startswith("src"):
        name = f"src.{name}"
    return logging.getLogger(name)


def set_request_context(request_id: Optional[str] = None, 
                       user_email: Optional[str] = None,
                       session_id: Optional[str] = None):
    """Set request context for logging."""
    if request_id:
        request_id_context.set(request_id)
    if user_email:
        user_email_context.set(user_email)
    if session_id:
        session_id_context.set(session_id)


def clear_request_context():
    """Clear request context."""
    request_id_context.set(None)
    user_email_context.set(None)
    session_id_context.set(None)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def log_performance(operation: str, logger: Optional[logging.Logger] = None):
    """Decorator to log performance metrics for functions."""
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                # Use provided logger or get performance logger
                perf_logger = logger or PerformanceLogger()
                
                if hasattr(perf_logger, 'log_execution_time'):
                    perf_logger.log_execution_time(
                        operation=operation,
                        duration_ms=duration_ms,
                        success=success,
                        error=error if error else None
                    )
                else:
                    # Fallback for regular loggers
                    level = logging.INFO if success else logging.ERROR
                    perf_logger.log(
                        level,
                        f"Operation '{operation}' completed in {duration_ms:.2f}ms - Success: {success}"
                    )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                # Use provided logger or get performance logger
                perf_logger = logger or PerformanceLogger()
                
                if hasattr(perf_logger, 'log_execution_time'):
                    perf_logger.log_execution_time(
                        operation=operation,
                        duration_ms=duration_ms,
                        success=success,
                        error=error if error else None
                    )
                else:
                    # Fallback for regular loggers
                    level = logging.INFO if success else logging.ERROR
                    perf_logger.log(
                        level,
                        f"Operation '{operation}' completed in {duration_ms:.2f}ms - Success: {success}"
                    )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Create global performance logger instance
performance_logger = PerformanceLogger()

# Initialize logging when module is imported
if not logging.getLogger().handlers:  # Only setup if not already configured
    setup_logging() 