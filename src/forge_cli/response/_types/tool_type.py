"""Type definitions for tools that can be used with the model."""

from enum import Enum


class ToolType(str, Enum):
    """Types of tools that can be used with the model."""

    WEB_SEARCH = "web_search"
    FILE_SEARCH = "file_search"
    FUNCTION = "function"
