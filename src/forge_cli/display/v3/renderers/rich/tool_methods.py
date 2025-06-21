"""Tool method dispatchers for the Rich display system."""

from typing import Any
from ...style import ICONS
from ...builder import TextBuilder
from forge_cli.response.type_guards import (
    is_code_interpreter_call,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_list_documents_call,
    is_page_reader_call,
    is_web_search_call,
)
from .tools import (
    FileSearchToolRender,
    WebSearchToolRender,
    ListDocumentsToolRender,
    FileReaderToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
)


def get_tool_result_summary(tool_item: Any) -> str:
    """Create a concise, beautiful summary of tool results."""
    if is_file_search_call(tool_item):
        # Use the specialized FileSearchToolRender class
        return FileSearchToolRender.from_tool_item(tool_item).render()

    elif is_web_search_call(tool_item):
        # Use the specialized WebSearchToolRender class
        return WebSearchToolRender.from_tool_item(tool_item).render()

    elif is_list_documents_call(tool_item):
        # Use the specialized ListDocumentsToolRender class
        return ListDocumentsToolRender.from_tool_item(tool_item).render()

    elif is_file_reader_call(tool_item):
        # Use the specialized FileReaderToolRender class
        return FileReaderToolRender.from_tool_item(tool_item).render()

    elif is_page_reader_call(tool_item):
        # Use the specialized PageReaderToolRender class
        return PageReaderToolRender.from_tool_item(tool_item).render()

    elif is_code_interpreter_call(tool_item):
        # Use the specialized CodeInterpreterToolRender class
        return CodeInterpreterToolRender.from_tool_item(tool_item).render()

    elif is_function_call(tool_item):
        # Use the specialized FunctionCallToolRender class
        return FunctionCallToolRender.from_tool_item(tool_item).render()

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


def render_file_search_tool_call(tool_item) -> str:
    """Render a file search tool call."""
    return FileSearchToolRender.from_tool_item(tool_item).render()


def render_web_search_tool_call(tool_item) -> str:
    """Render a web search tool call."""
    return WebSearchToolRender.from_tool_item(tool_item).render()


def render_list_documents_tool_call(tool_item) -> str:
    """Render a list documents tool call."""
    return ListDocumentsToolRender.from_tool_item(tool_item).render()


def render_file_reader_tool_call(tool_item) -> str:
    """Render a file reader tool call."""
    return FileReaderToolRender.from_tool_item(tool_item).render()


def render_page_reader_tool_call(tool_item) -> str:
    """Render a page reader tool call."""
    return PageReaderToolRender.from_tool_item(tool_item).render()


def render_code_interpreter_tool_call(tool_item) -> str:
    """Render a code interpreter tool call."""
    return CodeInterpreterToolRender.from_tool_item(tool_item).render()


def render_function_tool_call(tool_item) -> str:
    """Render a function tool call."""
    return FunctionCallToolRender.from_tool_item(tool_item).render() 