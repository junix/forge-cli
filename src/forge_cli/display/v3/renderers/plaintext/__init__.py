"""Modular plaintext renderer package for v3 display system.

This package provides clean, colorful plaintext output using Rich's Text and Live components.
It is organized into modular components for maintainability, following the same patterns as the Rich renderer.

Components:
- render.py: Main PlaintextRenderer class
- config.py: Configuration management
- styles.py: Centralized style management
- message_content.py: Message content rendering
- citations.py: Citations rendering
- usage.py: Usage statistics rendering
- reasoning.py: Reasoning content rendering
- welcome.py: Welcome screen rendering
- tools/: Tool-specific renderers
"""

from .render import PlaintextRenderer
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles
from .message_content import PlaintextMessageContentRenderer
from .citations import PlaintextCitationsRenderer
from .usage import PlaintextUsageRenderer
from .reasoning import PlaintextReasoningRenderer
from .welcome import PlaintextWelcomeRenderer

# Import tool renderers
from .tools import (
    PlaintextFileReaderToolRender,
    PlaintextWebSearchToolRender,
    PlaintextFileSearchToolRender,
    PlaintextPageReaderToolRender,
    PlaintextCodeInterpreterToolRender,
    PlaintextFunctionCallToolRender,
    PlaintextListDocumentsToolRender,
)

__all__ = [
    "PlaintextRenderer",
    "PlaintextDisplayConfig",
    "PlaintextStyles",
    "PlaintextMessageContentRenderer",
    "PlaintextCitationsRenderer",
    "PlaintextUsageRenderer",
    "PlaintextReasoningRenderer",
    "PlaintextWelcomeRenderer",
    "PlaintextFileReaderToolRender",
    "PlaintextWebSearchToolRender",
    "PlaintextFileSearchToolRender",
    "PlaintextPageReaderToolRender",
    "PlaintextCodeInterpreterToolRender",
    "PlaintextFunctionCallToolRender",
    "PlaintextListDocumentsToolRender",
] 