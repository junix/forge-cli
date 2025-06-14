"""Configure handlers and formats for application loggers."""

import logging
import sys
from pprint import pformat
from typing import Any

# if you dont like imports of private modules
# you can move it to typing.py module
from loguru import logger
from loguru._defaults import LOGURU_FORMAT


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    # Simplified format: timestamp and message only
    # format_string = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {message}"

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(record["extra"]["payload"], indent=4, compact=True, width=88)
        format_string += "\n<level>{extra[payload]}</level>"

    # Display all other bound variables in extras
    if record["extra"] and len(record["extra"]) > 0:
        extras = {k: v for k, v in record["extra"].items() if k != "payload"}
        if extras:
            record["extra"]["_all_extras"] = pformat(extras, indent=4, compact=True, width=88)
            format_string += "\n<level>{extra[_all_extras]}</level>"

    format_string += "{exception}\n"
    return format_string


def init_logging(level: str = "DEBUG", enable_colors: bool = True, structured: bool = True):
    """
    Initialize enhanced logging with improved formatting and features.

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_colors: Whether to use colored output
        structured: Whether to use structured formatting

    Features:
        - Rich formatting with icons and colors
        - Structured payload display
        - Enhanced exception handling
        - Performance optimizations
        - Configurable output levels
    """

    # Remove default logger
    logger.remove()

    # Configure uvicorn loggers
    uvicorn_loggers = [
        logging.getLogger(name) for name in logging.root.manager.loggerDict if name.startswith(("uvicorn", "fastapi"))
    ]

    for uvicorn_logger in uvicorn_loggers:
        uvicorn_logger.handlers = []

    # Set up intercept handler for standard logging
    intercept_handler = InterceptHandler()
    logging.getLogger().handlers = [intercept_handler]
    logging.getLogger().setLevel(getattr(logging, level))

    # Configure main logger with enhanced formatting
    format_func = format_record if structured else LOGURU_FORMAT

    handlers = [
        {
            "sink": sys.stdout,
            "level": level,
            "format": format_func,
            "colorize": enable_colors,
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,  # Thread-safe logging
        }
    ]

    # Add file handler for errors (only if logs directory exists)
    try:
        import os

        if not os.path.exists("logs"):
            os.makedirs("logs")
        handlers.append(
            {
                "sink": "logs/error.log",
                "level": "ERROR",
                "format": format_func,
                "rotation": "10 MB",
                "retention": "1 week",
                "compression": "zip",
                "serialize": False,
            }
        )
    except Exception:
        pass  # Skip file logging if not possible

    logger.configure(handlers=handlers)

    # Log initialization
    logger.success(f"Enhanced logging initialized - Level: {level}, Colors: {enable_colors}, Structured: {structured}")


# Convenience functions for structured logging
def log_request(method: str, url: str, status_code: int = None, duration: float = None, **extras):
    """Log HTTP request with structured data."""
    logger.bind(
        request_method=method,
        request_url=url,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2) if duration else None,
        **extras,
    ).info(f"{method} {url}" + (f" - {status_code}" if status_code else ""))


def log_performance(operation: str, duration: float, **extras):
    """Log performance metrics."""
    level = "WARNING" if duration > 1.0 else "INFO"
    logger.bind(operation=operation, duration_ms=round(duration * 1000, 2), **extras).log(
        level, f"Performance: {operation} took {duration:.3f}s"
    )


def log_error_with_context(error: Exception, context: dict[str, Any] = None):
    """Log error with additional context."""
    logger.bind(error_type=type(error).__name__, error_message=str(error), context=context or {}).error(
        f"Error occurred: {error}"
    )


# Initialize with enhanced settings
init_logging(level="DEBUG", enable_colors=True, structured=True)
