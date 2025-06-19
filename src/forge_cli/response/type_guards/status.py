from __future__ import annotations

"""Type guards for status and error types."""

from typing import Any


def is_response_completed_status(status: str) -> bool:
    """Check if a response status string indicates 'completed'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'completed', False otherwise.
    """
    return status == "completed"


def is_response_failed_status(status: str) -> bool:
    """Check if a response status string indicates 'failed'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'failed', False otherwise.
    """
    return status == "failed"


def is_response_in_progress_status(status: str) -> bool:
    """Check if a response status string indicates 'in_progress'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'in_progress', False otherwise.
    """
    return status == "in_progress"


def is_response_incomplete_status(status: str) -> bool:
    """Check if a response status string indicates 'incomplete'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'incomplete', False otherwise.
    """
    return status == "incomplete"


def is_response_error(obj: Any) -> bool:
    """Check if an object represents a response error structure.

    This typically checks for the presence of 'type' and 'error' attributes.

    Args:
        obj: The object to check.

    Returns:
        True if the object appears to be a response error, False otherwise.
    """
    return hasattr(obj, "code") and hasattr(obj, "message")
