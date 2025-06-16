"""Utility functions and complex type guards."""

from typing import Any

from .._types.response_output_item import ResponseOutputItem
from .input_content import is_input_text
from .output_items import (
    is_code_interpreter_call,
    is_computer_tool_call,
    is_document_finder_call,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_web_search_call,
)
from .status import is_response_error


def get_tool_queries(tool_item: ResponseOutputItem) -> list[str]:
    """Extracts search queries from a ResponseOutputItem if it's a tool call that supports queries.

    Handles tool calls like file search, web search, and document finder.
    Returns an empty list if the tool item doesn't have queries (e.g., file reader, computer tool).

    Args:
        tool_item: The ResponseOutputItem to extract queries from.

    Returns:
        A list of query strings, or an empty list if no queries are applicable.
    """
    if is_file_search_call(tool_item):
        return tool_item.queries
    elif is_web_search_call(tool_item):
        return tool_item.queries if tool_item.queries else []
    elif is_document_finder_call(tool_item):
        return tool_item.queries if tool_item.queries else []
    elif is_file_reader_call(tool_item):
        # File reader doesn't have queries, return empty list
        return []
    elif is_computer_tool_call(tool_item):
        # Computer tool doesn't have queries, return empty list
        return []
    elif is_function_call(tool_item):
        # Function call doesn't have queries, return empty list
        return []
    elif is_code_interpreter_call(tool_item):
        # Code interpreter doesn't have queries, return empty list
        return []
    else:
        return []


def get_tool_results(tool_item: ResponseOutputItem) -> list[Any]:
    """Extracts results from a ResponseOutputItem if it's a tool call that produces results.

    Handles tool calls like file search, web search, document finder, file reader, and code interpreter.
    Returns an empty list for tool calls that don't have results in this format (e.g., computer tool, function call).

    Args:
        tool_item: The ResponseOutputItem to extract results from.

    Returns:
        A list of results, or an empty list if no results are applicable or available.
    """
    if is_file_search_call(tool_item):
        return []  # File search results are not directly accessible from tool call
    elif is_web_search_call(tool_item):
        return []  # Web search results are not directly accessible from tool call
    elif is_document_finder_call(tool_item):
        return []  # Document finder results are not directly accessible from tool call
    elif is_file_reader_call(tool_item):
        return []  # File reader results are not directly accessible from tool call
    elif is_computer_tool_call(tool_item):
        return []  # Computer tool doesn't have results in the same format
    elif is_function_call(tool_item):
        return []  # Function call doesn't have results in the same format
    elif is_code_interpreter_call(tool_item):
        return tool_item.results if tool_item.results else []
    else:
        return []


def get_tool_content(tool_item: ResponseOutputItem) -> str | None:
    """Extracts content (e.g., file content, code) from a ResponseOutputItem.

    Applicable to tool calls like file reader (content) and code interpreter (code).
    Returns None for tool calls that don't have a direct 'content' or 'code' field (e.g., computer tool, function call).

    Args:
        tool_item: The ResponseOutputItem to extract content from.

    Returns:
        The content string if available, otherwise None.
    """
    if is_file_reader_call(tool_item):
        return tool_item.content
    elif is_computer_tool_call(tool_item):
        # Computer tool calls don't have a code field, they have action
        return None
    elif is_code_interpreter_call(tool_item):
        return tool_item.code if tool_item.code else None
    elif is_function_call(tool_item):
        return None  # Function calls don't have content
    else:
        return None


def get_tool_output(tool_item: ResponseOutputItem) -> str | None:
    """Extracts the output from a ResponseOutputItem, typically from a function call.

    Primarily used for `ResponseFunctionToolCall` to get its `output` attribute.
    Returns None for other tool types or if the output attribute is not present.

    Args:
        tool_item: The ResponseOutputItem to extract output from.

    Returns:
        The output string if available (for function calls), otherwise None.
    """
    if is_computer_tool_call(tool_item):
        # Computer tool calls don't have output field in the same way
        return None
    elif is_function_call(tool_item):
        return getattr(tool_item, "output", None)
    else:
        return None


def get_tool_function_name(tool_item: ResponseOutputItem) -> str | None:
    """Extracts the function name from a ResponseOutputItem if it's a ResponseFunctionToolCall.

    Args:
        tool_item: The ResponseOutputItem to check.

    Returns:
        The function name string if the item is a function call, otherwise None.
    """
    if is_function_call(tool_item):
        return tool_item.name
    else:
        return None


def get_tool_arguments(tool_item: ResponseOutputItem) -> str | None:
    """Extracts the arguments string from a ResponseOutputItem if it's a ResponseFunctionToolCall.

    Args:
        tool_item: The ResponseOutputItem to check.

    Returns:
        The arguments string if the item is a function call, otherwise None.
    """
    if is_function_call(tool_item):
        return tool_item.arguments
    else:
        return None


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely retrieve an attribute from an object.

    If the attribute does not exist, returns the provided default value.

    Args:
        obj: The object from which to get the attribute.
        attr: The name of the attribute to retrieve.
        default: The value to return if the attribute is not found. Defaults to None.

    Returns:
        The attribute's value or the default value.
    """
    return getattr(obj, attr, default)


def is_code_interpreter_logs(result: Any) -> bool:
    """Check if a result from a Code Interpreter tool call is of type 'logs'.

    Args:
        result: The result item from `ResponseCodeInterpreterToolCall.results`.

    Returns:
        True if the result type is 'logs', False otherwise.
    """
    return hasattr(result, "type") and result.type == "logs"


def is_code_interpreter_files(result: Any) -> bool:
    """Check if a result from a Code Interpreter tool call is of type 'files'.

    Args:
        result: The result item from `ResponseCodeInterpreterToolCall.results`.

    Returns:
        True if the result type is 'files', False otherwise.
    """
    return hasattr(result, "type") and result.type == "files"


def is_computer_tool_output(item: Any) -> bool:
    """Check if an item is a computer tool call output.

    This typically refers to the structured output from a computer interaction.

    Args:
        item: The item to check.

    Returns:
        True if the item's type is 'computer_call_output', False otherwise.
    """
    return hasattr(item, "type") and item.type == "computer_call_output"


def get_error_message(error: Any) -> str | None:
    """Safely extracts the error message string from an error object.

    Assumes the error object might have a 'message' attribute.

    Args:
        error: The error object.

    Returns:
        The error message string if present, otherwise None.
    """
    if is_response_error(error):
        return error.message
    else:
        return None


def get_error_code(error: Any) -> str | None:
    """Safely extracts the error code from an error object.

    Assumes the error object might have a 'code' attribute.

    Args:
        error: The error object.

    Returns:
        The error code string if present, otherwise None.
    """
    if is_response_error(error):
        return error.code
    else:
        return None


def is_tool_call_completed(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it has completed.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'completed', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "completed"


def is_tool_call_in_progress(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is in progress.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'in_progress', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "in_progress"


def is_tool_call_failed(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it has failed.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'failed', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status in ["failed", "incomplete"]


def is_tool_call_searching(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is currently searching.

    Applicable to search-related tools like file search, web search, document finder.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'searching', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "searching"


def is_tool_call_interpreting(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is interpreting code.

    Specifically for Code Interpreter tool calls.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'interpreting', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "interpreting"


def is_any_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is any known type of tool call.

    This includes file search, web search, document finder, file reader,
    computer tool, function call, and code interpreter calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is one of the recognized tool call types, False otherwise.
    """
    return (
        is_file_search_call(item)
        or is_web_search_call(item)
        or is_document_finder_call(item)
        or is_file_reader_call(item)
        or is_computer_tool_call(item)
        or is_function_call(item)
        or is_code_interpreter_call(item)
    )


def get_tool_call_id(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'id' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call ID string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "id", None)


def get_tool_call_status(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'status' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call status string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "status", None)


def get_tool_call_type(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'type' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call type string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "type", None)


def is_computer_action_click(action: Any) -> bool:
    """Check if a computer tool action is a 'click' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'click', False otherwise.
    """
    return hasattr(action, "type") and action.type == "click"


def is_computer_action_double_click(action: Any) -> bool:
    """Check if a computer tool action is a 'double_click' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'double_click', False otherwise.
    """
    return hasattr(action, "type") and action.type == "double_click"


def is_computer_action_drag(action: Any) -> bool:
    """Check if a computer tool action is a 'drag' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'drag', False otherwise.
    """
    return hasattr(action, "type") and action.type == "drag"


def is_computer_action_keypress(action: Any) -> bool:
    """Check if a computer tool action is a 'keypress' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'keypress', False otherwise.
    """
    return hasattr(action, "type") and action.type == "keypress"


def is_computer_action_move(action: Any) -> bool:
    """Check if a computer tool action is a 'move' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'move', False otherwise.
    """
    return hasattr(action, "type") and action.type == "move"


def is_computer_action_screenshot(action: Any) -> bool:
    """Check if a computer tool action is a 'screenshot' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'screenshot', False otherwise.
    """
    return hasattr(action, "type") and action.type == "screenshot"


def is_computer_action_scroll(action: Any) -> bool:
    """Check if a computer tool action is a 'scroll' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'scroll', False otherwise.
    """
    return hasattr(action, "type") and action.type == "scroll"


def is_computer_action_type(action: Any) -> bool:
    """Check if a computer tool action is a 'type' (text input) action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'type', False otherwise.
    """
    return hasattr(action, "type") and action.type == "type"


def is_computer_action_wait(action: Any) -> bool:
    """Check if a computer tool action is a 'wait' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'wait', False otherwise.
    """
    return hasattr(action, "type") and action.type == "wait"


def is_search_related_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is a search-related tool call.

    This includes file search, web search, and document finder calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a file search, web search, or document finder call, False otherwise.
    """
    return is_file_search_call(item) or is_web_search_call(item) or is_document_finder_call(item)


def is_execution_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is an execution-related tool call.

    This includes computer tool calls and code interpreter calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a computer tool call or code interpreter call, False otherwise.
    """
    return is_computer_tool_call(item) or is_code_interpreter_call(item)


def is_dict_with_type(obj: Any, type_value: str) -> bool:
    """Check if an object is a dictionary and has a 'type' key with a specific value.

    Args:
        obj: The object to check.
        type_value: The expected value for the 'type' key.

    Returns:
        True if obj is a dict and obj.get('type') == type_value, False otherwise.
    """
    return isinstance(obj, dict) and obj.get("type") == type_value


def is_assistant_message_dict(obj: Any) -> bool:
    """Check if an object is a dictionary representing an assistant message.

    This specifically checks if it's a dict with 'role': 'assistant'.

    Args:
        obj: The object to check.

    Returns:
        True if obj is a dict with obj.get('role') == 'assistant', False otherwise.
    """
    return isinstance(obj, dict) and obj.get("type") == "message" and obj.get("role") == "assistant"
