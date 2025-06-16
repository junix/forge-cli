"""Type guards for content types."""

from typing import Any, TypeGuard

from .._types.response_input_text import ResponseInputText
from .._types.response_output_refusal import ResponseOutputRefusal
from .._types.response_output_text import ResponseOutputText


def is_output_text(content: Any) -> TypeGuard[ResponseOutputText]:
    """Check if the given content object is a ResponseOutputText.

    This is used to narrow down the type of `ResponseOutputMessage.content`.

    Args:
        content: The content object to check.

    Returns:
        True if the content is ResponseOutputText, False otherwise.
    """
    return hasattr(content, "type") and content.type == "output_text"


def is_output_refusal(content: Any) -> TypeGuard[ResponseOutputRefusal]:
    """Check if the given content object is a ResponseOutputRefusal.

    This is used to narrow down the type of `ResponseOutputMessage.content`.

    Args:
        content: The content object to check.

    Returns:
        True if the content is ResponseOutputRefusal, False otherwise.
    """
    return hasattr(content, "type") and content.type == "refusal"


def get_content_text(content: Any) -> str | None:
    """Extracts the text value from a content item if it's a ResponseOutputText.

    Args:
        content: The content item, expected to be of a type with a 'text' attribute
                 if it's an output text item (e.g., ResponseOutputText).

    Returns:
        The text string if the content is ResponseOutputText and has a text value,
        otherwise None.
    """
    if is_output_text(content):
        return content.text
    elif hasattr(content, "type") and content.type == "input_text":
        return content.text
    else:
        return None


def get_content_refusal(content: Any) -> str | None:
    """Extracts the refusal message from a content item if it's a ResponseOutputRefusal.

    Args:
        content: The content item, expected to be ResponseOutputRefusal.

    Returns:
        The refusal message string if the content is ResponseOutputRefusal,
        otherwise None.
    """
    if is_output_refusal(content):
        return content.refusal
    else:
        return None
