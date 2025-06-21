"""Helper functions for testing Rich renderer components."""

from rich.markdown import Markdown
from typing import Any


def extract_text_from_markdown(result: Any) -> str:
    """Extract text content from Markdown objects for testing.
    
    Args:
        result: The result from a renderer (could be Markdown, list of Markdown, or other)
        
    Returns:
        String content for assertion testing
    """
    if result is None:
        return ""
    
    if isinstance(result, Markdown):
        # Extract the markup text from Markdown object
        return result.markup
    
    if isinstance(result, list):
        # Handle list of Markdown objects
        text_parts = []
        for item in result:
            if isinstance(item, Markdown):
                text_parts.append(item.markup)
            else:
                text_parts.append(str(item))
        return " ".join(text_parts)
    
    # For other types, convert to string
    return str(result)


def assert_contains(result: Any, expected_text: str, msg: str = None):
    """Assert that the result contains the expected text.
    
    Args:
        result: The result from a renderer 
        expected_text: Text that should be present
        msg: Optional custom assertion message
    """
    actual_text = extract_text_from_markdown(result)
    if msg:
        assert expected_text in actual_text, f"{msg}: '{expected_text}' not found in '{actual_text}'"
    else:
        assert expected_text in actual_text, f"'{expected_text}' not found in '{actual_text}'"


def assert_equals(result: Any, expected_text: str, msg: str = None):
    """Assert that the result equals the expected text.
    
    Args:
        result: The result from a renderer
        expected_text: Text that should match exactly
        msg: Optional custom assertion message  
    """
    actual_text = extract_text_from_markdown(result)
    if msg:
        assert actual_text == expected_text, f"{msg}: Expected '{expected_text}', got '{actual_text}'"
    else:
        assert actual_text == expected_text, f"Expected '{expected_text}', got '{actual_text}'"


def assert_not_empty(result: Any, msg: str = None):
    """Assert that the result is not empty.
    
    Args:
        result: The result from a renderer
        msg: Optional custom assertion message
    """
    if result is None:
        if msg:
            assert False, f"{msg}: Result is None"
        else:
            assert False, "Result is None"
    
    actual_text = extract_text_from_markdown(result).strip()
    if msg:
        assert len(actual_text) > 0, f"{msg}: Result is empty"
    else:
        assert len(actual_text) > 0, "Result is empty" 