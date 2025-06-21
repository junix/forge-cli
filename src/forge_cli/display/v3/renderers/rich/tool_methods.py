"""Tool-related methods for the RichRenderer."""

from typing import Any

from forge_cli.response.type_guards import (
    is_code_interpreter_call,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_list_documents_call,
    is_page_reader_call,
    is_web_search_call,
)
from ...builder import TextBuilder

from ...style import ICONS, pack_queries
from .tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)


def get_tool_result_summary(tool_item: Any) -> str:
    """Create a concise, beautiful summary of tool results."""
    if is_file_search_call(tool_item):
        # Use the specialized FileSearchToolRender class
        return FileSearchToolRender.from_tool_item(tool_item)

    elif is_web_search_call(tool_item):
        # Use the specialized WebSearchToolRender class
        return WebSearchToolRender.from_tool_item(tool_item)

    elif is_list_documents_call(tool_item):
        # Use the specialized ListDocumentsToolRender class
        return ListDocumentsToolRender.from_tool_item(tool_item)

    elif is_file_reader_call(tool_item):
        # Use the specialized FileReaderToolRender class
        return FileReaderToolRender.from_tool_item(tool_item)

    elif is_page_reader_call(tool_item):
        # Use the specialized PageReaderToolRender class
        return PageReaderToolRender.from_tool_item(tool_item)

    elif is_code_interpreter_call(tool_item):
        # Use the specialized CodeInterpreterToolRender class
        return CodeInterpreterToolRender.from_tool_item(tool_item)

    elif is_function_call(tool_item):
        # Use the specialized FunctionCallToolRender class
        return FunctionCallToolRender.from_tool_item(tool_item)

    # Default fallback
    return ""


def get_trace_block(tool_item: Any) -> list[str] | None:
    """Extract the last few trace lines from a traceable tool for sliding display.

    Args:
        tool_item: The tool item to extract trace from

    Returns:
        List of formatted trace lines or None if no trace available
    """
    execution_trace = getattr(tool_item, "execution_trace", None)
    if not execution_trace:
        return None

    # Use Builder pattern for clean sliding display processing
    return TextBuilder.from_text(execution_trace).with_slide(max_lines=3, format_type="text").build() 