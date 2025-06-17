"""Type guards for Tool objects."""

from typing import TypeGuard

from .._types.computer_tool import ComputerTool
from .._types.file_reader_tool import FileReaderTool
from .._types.file_search_tool import FileSearchTool
from .._types.function_tool import FunctionTool
from .._types.list_documents_tool import ListDocumentsTool
from .._types.page_reader_tool import PageReaderTool
from .._types.tool import Tool
from .._types.web_search_tool import WebSearchTool


def is_file_search_tool(tool: Tool) -> TypeGuard[FileSearchTool]:
    """Check if the given Tool object is a FileSearchTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FileSearchTool, False otherwise.
    """
    return tool.type == "file_search"


def is_web_search_tool(tool: Tool) -> TypeGuard[WebSearchTool]:
    """Check if the given Tool object is a WebSearchTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a WebSearchTool, False otherwise.
    """
    return tool.type in ["web_search", "web_search_preview", "web_search_preview_2025_03_11"]


def is_function_tool(tool: Tool) -> TypeGuard[FunctionTool]:
    """Check if the given Tool object is a FunctionTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FunctionTool, False otherwise.
    """
    return tool.type == "function"


def is_computer_tool(tool: Tool) -> TypeGuard[ComputerTool]:
    """Check if the given Tool object is a ComputerTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a ComputerTool, False otherwise.
    """
    return tool.type == "computer_use_preview"


def is_list_documents_tool(tool: Tool) -> TypeGuard[ListDocumentsTool]:
    """Check if the given Tool object is a ListDocumentsTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a ListDocumentsTool, False otherwise.
    """
    return tool.type == "list_documents"


def is_file_reader_tool(tool: Tool) -> TypeGuard[FileReaderTool]:
    """Check if the given Tool object is a FileReaderTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FileReaderTool, False otherwise.
    """
    return tool.type == "file_reader"


def is_page_reader_tool(tool: Tool) -> TypeGuard[PageReaderTool]:
    """Check if the given Tool object is a PageReaderTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a PageReaderTool, False otherwise.
    """
    return tool.type in ["page_reader", "page_reader_preview"]
