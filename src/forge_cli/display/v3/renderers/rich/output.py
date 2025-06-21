"""Output renderer for Rich display system.

This module provides backward compatibility by re-exporting renderers
from their dedicated files.
"""

# Import from dedicated files
from .message_content import MessageContentRenderer, render_message_content
from .citations import CitationsRenderer, render_citations

# Re-export for backward compatibility
__all__ = [
    "MessageContentRenderer",
    "CitationsRenderer", 
    "render_message_content",
    "render_citations",
] 