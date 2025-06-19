from __future__ import annotations

"""Type guards for input content types."""

from typing import Any, TypeGuard

from .._types.response_input_file import ResponseInputFile
from .._types.response_input_image import ResponseInputImage
from .._types.response_input_text import ResponseInputText


def is_input_text(content: Any) -> TypeGuard[ResponseInputText]:
    """Check if the given input content object is a ResponseInputText.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputText, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_text"


def is_input_image(content: Any) -> TypeGuard[ResponseInputImage]:
    """Check if the given input content object is a ResponseInputImage.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputImage, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_image"


def is_input_file(content: Any) -> TypeGuard[ResponseInputFile]:
    """Check if the given input content object is a ResponseInputFile.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputFile, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_file"
