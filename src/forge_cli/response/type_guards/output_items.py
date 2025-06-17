"""Type guards for ResponseOutputItem types."""

from typing import TypeGuard

from .._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
from .._types.response_computer_tool_call import ResponseComputerToolCall
from .._types.response_file_search_tool_call import ResponseFileSearchToolCall
from .._types.response_function_file_reader import ResponseFunctionFileReader
from .._types.response_function_page_reader import ResponseFunctionPageReader
from .._types.response_function_tool_call import ResponseFunctionToolCall
from .._types.response_function_web_search import ResponseFunctionWebSearch
from .._types.response_list_documents_tool_call import ResponseListDocumentsToolCall
from .._types.response_output_item import ResponseOutputItem
from .._types.response_output_message import ResponseOutputMessage
from .._types.response_reasoning_item import ResponseReasoningItem


def is_message_item(item: ResponseOutputItem) -> TypeGuard[ResponseOutputMessage]:
    """Check if the given ResponseOutputItem is a ResponseOutputMessage.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseOutputMessage, False otherwise.
    """
    return item.type == "message"


def is_reasoning_item(item: ResponseOutputItem) -> TypeGuard[ResponseReasoningItem]:
    """Check if the given ResponseOutputItem is a ResponseReasoningItem.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseReasoningItem, False otherwise.
    """
    return item.type == "reasoning"


def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if the given ResponseOutputItem is a ResponseFileSearchToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFileSearchToolCall, False otherwise.
    """
    return item.type == "file_search_call"


def is_web_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionWebSearch]:
    """Check if the given ResponseOutputItem is a ResponseFunctionWebSearch.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionWebSearch, False otherwise.
    """
    return item.type == "web_search_call"


def is_list_documents_call(item: ResponseOutputItem) -> TypeGuard[ResponseListDocumentsToolCall]:
    """Check if the given ResponseOutputItem is a ResponseListDocumentsToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseListDocumentsToolCall, False otherwise.
    """
    return item.type == "list_documents_call"


def is_file_reader_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionFileReader]:
    """Check if the given ResponseOutputItem is a ResponseFunctionFileReader.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionFileReader, False otherwise.
    """
    return item.type == "file_reader_call"


def is_page_reader_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionPageReader]:
    """Check if the given ResponseOutputItem is a ResponseFunctionPageReader.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionPageReader, False otherwise.
    """
    return item.type == "page_reader_call"


def is_computer_tool_call(item: ResponseOutputItem) -> TypeGuard[ResponseComputerToolCall]:
    """Check if the given ResponseOutputItem is a ResponseComputerToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseComputerToolCall, False otherwise.
    """
    return item.type == "computer_call"


def is_function_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionToolCall]:
    """Check if the given ResponseOutputItem is a ResponseFunctionToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionToolCall, False otherwise.
    """
    return item.type == "function_call"


def is_code_interpreter_call(item: ResponseOutputItem) -> TypeGuard[ResponseCodeInterpreterToolCall]:
    """Check if the given ResponseOutputItem is a ResponseCodeInterpreterToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseCodeInterpreterToolCall, False otherwise.
    """
    return item.type == "code_interpreter_call"
