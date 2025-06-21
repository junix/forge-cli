"""Rich renderer package for v3 display system.

This package provides beautiful terminal UI rendering capabilities using the Rich library.
It is organized into modular components for maintainability:

- render.py: Main RichRenderer class and configuration
- reason.py: Reasoning content rendering
- output.py: Message content and citation rendering  
- welcome.py: Welcome screen rendering
- tools/: Tool-specific renderers (file_reader, etc.)
- core_methods.py: Core rendering methods
- tool_methods.py: Tool result summary methods
"""

from .render import RichRenderer, RichDisplayConfig

# Maintain backward compatibility
__all__ = ["RichRenderer", "RichDisplayConfig"] 