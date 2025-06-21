"""Rich renderer package for v3 display system.

This package provides beautiful terminal UI rendering capabilities using the Rich library.
It is organized into modular components for maintainability:

- render.py: Main RichRenderer class and configuration
- reason.py: Reasoning content rendering
- message_content.py: Message content rendering (MessageContentRenderer)
- citations.py: Citations rendering (CitationsRenderer)
- welcome.py: Welcome screen rendering (WelcomeRenderer class)
- usage.py: Usage statistics rendering (UsageRenderer class)
- tools/: Tool-specific renderers (file_reader, etc.)
- core_methods.py: Core rendering methods
- tool_methods.py: Tool result summary methods
"""

from .render import RichRenderer, RichDisplayConfig
from .welcome import WelcomeRenderer
from .usage import UsageRenderer
from .message_content import MessageContentRenderer
from .citations import CitationsRenderer
from .tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)

# Maintain backward compatibility and export new classes
__all__ = [
    "RichRenderer", 
    "RichDisplayConfig", 
    "WelcomeRenderer",
    "UsageRenderer",
    "MessageContentRenderer",
    "CitationsRenderer",
    "FileReaderToolRender",
    "WebSearchToolRender",
    "FileSearchToolRender",
    "PageReaderToolRender",
    "CodeInterpreterToolRender",
    "FunctionCallToolRender",
    "ListDocumentsToolRender",
] 