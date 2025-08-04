# Common Module - Shared Utilities and Infrastructure

## Overview

The common module provides shared utilities and infrastructure components used throughout the Forge CLI application. It contains foundational functionality that supports logging, error handling, and other cross-cutting concerns that are needed by multiple modules.

## Directory Structure

```
common/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Module exports
└── logger.py                    # Logging configuration and utilities
```

## Architecture & Design

### Design Principles

1. **Centralized Infrastructure**: Common functionality in one place
2. **Consistent Logging**: Standardized logging across all modules
3. **Reusable Components**: Utilities that can be used by any module
4. **Type Safety**: Comprehensive type annotations throughout
5. **Performance**: Efficient implementations for frequently used utilities

### Core Components

#### logger.py - Logging Infrastructure

Provides centralized logging configuration using Loguru for structured, high-performance logging:

**Key Features:**

- **Structured Logging**: JSON-formatted logs with contextual information
- **Multiple Output Formats**: Console and file logging with different formats
- **Log Level Management**: Dynamic log level configuration
- **Performance Optimization**: Efficient logging for high-throughput scenarios
- **Debug Support**: Enhanced debugging information in debug mode

**Configuration Options:**

- **Console Logging**: Rich terminal output with colors and formatting
- **File Logging**: Structured JSON logs for analysis and monitoring
- **Debug Mode**: Verbose logging with detailed context information
- **Production Mode**: Optimized logging for production environments

## Implementation Details

### Logging Configuration

```python
from loguru import logger
import sys
from typing import Optional

def configure_logging(
    debug: bool = False,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console logging configuration
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if debug:
        logger.add(
            sys.stderr,
            format=console_format,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        logger.add(
            sys.stderr,
            format=console_format,
            level="INFO",
            colorize=True
        )
    
    # File logging if specified
    if log_file:
        if json_format:
            logger.add(
                log_file,
                format="{time} | {level} | {name}:{function}:{line} | {message}",
                level="DEBUG" if debug else "INFO",
                rotation="10 MB",
                retention="7 days",
                serialize=True  # JSON format
            )
        else:
            logger.add(
                log_file,
                format=console_format,
                level="DEBUG" if debug else "INFO",
                rotation="10 MB",
                retention="7 days"
            )
```

### Contextual Logging

```python
from contextvars import ContextVar
from typing import Dict, Any

# Context variables for request tracking
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_context: ContextVar[Dict[str, Any]] = ContextVar('user_context', default={})

def log_with_context(level: str, message: str, **kwargs) -> None:
    """Log message with contextual information."""
    context = {
        'request_id': request_id.get(),
        'user_context': user_context.get(),
        **kwargs
    }
    
    # Filter out None values
    context = {k: v for k, v in context.items() if v is not None}
    
    logger.bind(**context).log(level, message)

def set_request_context(req_id: str, user_info: Dict[str, Any]) -> None:
    """Set context for current request."""
    request_id.set(req_id)
    user_context.set(user_info)
```

### Performance Logging

```python
import time
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def log_performance(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(
                "Function executed successfully",
                function=function_name,
                execution_time=execution_time,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                "Function execution failed",
                function=function_name,
                execution_time=execution_time,
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise
    
    return wrapper

async def log_async_performance(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log async function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(
                "Async function executed successfully",
                function=function_name,
                execution_time=execution_time,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                "Async function execution failed",
                function=function_name,
                execution_time=execution_time,
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise
    
    return wrapper
```

## Usage Patterns

### Basic Logging

```python
from forge_cli.common.logger import logger

# Basic logging
logger.info("Application started")
logger.debug("Debug information", extra_data="value")
logger.error("Error occurred", error_code=500)

# Structured logging with context
logger.bind(user_id="123", action="file_upload").info("File uploaded successfully")
```

### Performance Monitoring

```python
from forge_cli.common.logger import log_performance, log_async_performance

@log_performance
def process_document(document_path: str) -> dict:
    """Process document with performance logging."""
    # Implementation here
    return {"status": "processed"}

@log_async_performance
async def upload_file(file_path: str) -> dict:
    """Upload file with async performance logging."""
    # Implementation here
    return {"file_id": "file_123"}
```

### Error Handling with Context

```python
from forge_cli.common.logger import logger, set_request_context

def handle_api_request(request_id: str, user_info: dict):
    """Handle API request with contextual logging."""
    set_request_context(request_id, user_info)
    
    try:
        # Process request
        logger.info("Processing API request")
        result = process_request()
        logger.info("API request completed successfully")
        return result
        
    except Exception as e:
        logger.error(
            "API request failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

## Configuration Integration

### Environment-Based Configuration

```python
import os
from typing import Optional

def get_logging_config() -> dict:
    """Get logging configuration from environment."""
    return {
        'debug': os.getenv('FORGE_CLI_DEBUG', 'false').lower() == 'true',
        'log_file': os.getenv('FORGE_CLI_LOG_FILE'),
        'json_format': os.getenv('FORGE_CLI_LOG_JSON', 'false').lower() == 'true',
        'log_level': os.getenv('FORGE_CLI_LOG_LEVEL', 'INFO').upper()
    }

def initialize_logging() -> None:
    """Initialize logging with environment configuration."""
    config = get_logging_config()
    configure_logging(**config)
```

### Application Integration

```python
# In main.py or application startup
from forge_cli.common.logger import initialize_logging, logger

def main():
    """Main application entry point."""
    # Initialize logging first
    initialize_logging()
    
    logger.info("Forge CLI application starting")
    
    try:
        # Application logic
        run_application()
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error("Application failed", error=str(e))
        raise
```

## Related Components

- **Configuration** (`../config.py`) - Uses common logging for configuration events
- **SDK** (`../sdk/`) - Uses common logging for API interactions
- **Display** (`../display/`) - Uses common logging for rendering events
- **Chat** (`../chat/`) - Uses common logging for chat session events

## Best Practices

### Logging Guidelines

1. **Structured Data**: Use key-value pairs for contextual information
2. **Appropriate Levels**: Use correct log levels (DEBUG, INFO, WARNING, ERROR)
3. **Performance Awareness**: Avoid expensive operations in log statements
4. **Security**: Don't log sensitive information like API keys or passwords
5. **Context**: Include relevant context for debugging and monitoring

### Implementation Standards

1. **Type Safety**: Use proper type annotations for all functions
2. **Error Handling**: Handle logging errors gracefully
3. **Performance**: Optimize for high-throughput scenarios
4. **Configuration**: Support environment-based configuration
5. **Testing**: Include tests for logging functionality

The common module provides essential infrastructure that ensures consistent, high-quality logging and shared utilities across the entire Forge CLI application.
