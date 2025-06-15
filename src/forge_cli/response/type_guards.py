"""Type guards and utilities for Response types to enable proper type narrowing."""

from typing import Any, TypeGuard

from ._types.annotations import AnnotationFileCitation, AnnotationFilePath, AnnotationURLCitation
from ._types.response_computer_tool_call import ResponseComputerToolCall
from ._types.response_document_finder_tool_call import ResponseDocumentFinderToolCall
from ._types.response_file_search_tool_call import ResponseFileSearchToolCall
from ._types.response_function_file_reader import ResponseFunctionFileReader
from ._types.response_function_tool_call import ResponseFunctionToolCall
from ._types.response_function_web_search import ResponseFunctionWebSearch
from ._types.response_output_item import ResponseOutputItem
from ._types.response_output_message import ResponseOutputMessage
from ._types.response_reasoning_item import ResponseReasoningItem


def is_message_item(item: ResponseOutputItem) -> TypeGuard[ResponseOutputMessage]:
    """Check if output item is a message."""
    return item.type == "message"


def is_reasoning_item(item: ResponseOutputItem) -> TypeGuard[ResponseReasoningItem]:
    """Check if output item is reasoning."""
    return item.type == "reasoning"


def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if output item is a file search tool call."""
    return item.type == "file_search_call"


def is_web_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionWebSearch]:
    """Check if output item is a web search tool call."""
    return item.type == "web_search_call"


def is_document_finder_call(item: ResponseOutputItem) -> TypeGuard[ResponseDocumentFinderToolCall]:
    """Check if output item is a document finder tool call."""
    return item.type == "document_finder_call"


def is_file_reader_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionFileReader]:
    """Check if output item is a file reader tool call."""
    return item.type == "file_reader_call"


def is_computer_tool_call(item: ResponseOutputItem) -> TypeGuard[ResponseComputerToolCall]:
    """Check if output item is a computer tool call."""
    return item.type == "computer_tool_call"


def is_function_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionToolCall]:
    """Check if output item is a function call."""
    return item.type == "function_call"


def is_file_citation(annotation: Any) -> TypeGuard[AnnotationFileCitation]:
    """Check if annotation is a file citation."""
    return hasattr(annotation, "type") and annotation.type == "file_citation"


def is_url_citation(annotation: Any) -> TypeGuard[AnnotationURLCitation]:
    """Check if annotation is a URL citation."""
    return hasattr(annotation, "type") and annotation.type == "url_citation"


def is_file_path(annotation: Any) -> TypeGuard[AnnotationFilePath]:
    """Check if annotation is a file path."""
    return hasattr(annotation, "type") and annotation.type == "file_path"


def get_tool_queries(tool_item: ResponseOutputItem) -> list[str]:
    """Get queries from a tool item, handling both single query and multiple queries."""
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
    else:
        return []


def get_tool_results(tool_item: ResponseOutputItem) -> list[Any]:
    """Get results from a tool item."""
    if is_file_search_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_web_search_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_document_finder_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_file_reader_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_computer_tool_call(tool_item):
        return []  # Computer tool doesn't have results in the same format
    elif is_function_call(tool_item):
        return []  # Function call doesn't have results in the same format
    else:
        return []


def get_tool_content(tool_item: ResponseOutputItem) -> str | None:
    """Get content from a tool item."""
    if is_file_reader_call(tool_item):
        return tool_item.content
    elif is_computer_tool_call(tool_item):
        return tool_item.code if tool_item.code else None
    elif is_function_call(tool_item):
        return None  # Function calls don't have content
    else:
        return None


def get_tool_output(tool_item: ResponseOutputItem) -> str | None:
    """Get output from a tool item."""
    if is_computer_tool_call(tool_item):
        return tool_item.output
    elif is_function_call(tool_item):
        return tool_item.output
    else:
        return None


def get_tool_function_name(tool_item: ResponseOutputItem) -> str | None:
    """Get function name from a function call tool item."""
    if is_function_call(tool_item):
        return tool_item.function
    else:
        return None


def get_tool_arguments(tool_item: ResponseOutputItem) -> str | None:
    """Get arguments from a function call tool item."""
    if is_function_call(tool_item):
        return tool_item.arguments
    else:
        return None


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get attribute from object, returning default if not present."""
    return getattr(obj, attr, default)
