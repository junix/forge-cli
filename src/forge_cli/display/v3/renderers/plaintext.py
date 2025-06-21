"""Legacy plaintext renderer module - now redirects to modular implementation.

This module provides backward compatibility for the original monolithic
PlaintextRenderer while internally using the new modular architecture.

The original 741-line monolithic PlaintextRenderer has been refactored into
a modular architecture with the following components:

- PlaintextRenderer: Main renderer using modular components
- PlaintextDisplayConfig: Configuration management
- PlaintextStyles: Centralized style management
- PlaintextMessageContentRenderer: Message content rendering
- PlaintextCitationsRenderer: Citations rendering  
- PlaintextUsageRenderer: Usage statistics rendering
- PlaintextReasoningRenderer: Reasoning content rendering
- PlaintextWelcomeRenderer: Welcome screen rendering
- Tool renderers: Specialized renderers for each tool type

This provides:
- Better maintainability (50-100 lines per component vs 741 lines)
- Improved testability (isolated components)
- Enhanced extensibility (easy to add new renderers)
- Consistency with Rich renderer architecture
- Complete backward compatibility
"""

# Import the new modular implementation
from .plaintext.render import PlaintextRenderer
from .plaintext.config import PlaintextDisplayConfig

# Re-export for backward compatibility
__all__ = ["PlaintextRenderer", "PlaintextDisplayConfig"]
