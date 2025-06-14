"""Base display interface for v2 - pure rendering without input handling."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class Renderer(Protocol):
    """Pure renderer protocol - only handles output formatting."""

    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Render a single stream event."""
        ...

    def finalize(self) -> None:
        """Complete rendering and cleanup."""
        ...


class BaseRenderer(ABC):
    """Abstract base for renderers with common functionality."""

    def __init__(self):
        self._finalized = False

    @abstractmethod
    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Render a single stream event.

        Args:
            event_type: Type of event (e.g., "text_delta", "tool_start")
            data: Event-specific data
        """
        pass

    @abstractmethod
    def finalize(self) -> None:
        """Complete rendering and cleanup resources."""
        pass

    def _ensure_not_finalized(self):
        """Check that renderer hasn't been finalized."""
        if self._finalized:
            raise RuntimeError("Renderer already finalized")


class Display:
    """Display coordinator - manages render lifecycle."""

    def __init__(self, renderer: Renderer):
        """Initialize display with a renderer.

        Args:
            renderer: The renderer implementation to use
        """
        self._renderer = renderer
        self._event_count = 0
        self._finalized = False

    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Route events to renderer.

        Args:
            event_type: Type of event
            data: Event-specific data
        """
        if self._finalized:
            raise RuntimeError("Display already finalized")

        self._event_count += 1
        self._renderer.render_stream_event(event_type, data)

    def complete(self) -> None:
        """Finalize display."""
        if not self._finalized:
            self._renderer.finalize()
            self._finalized = True

    @property
    def event_count(self) -> int:
        """Get total number of events handled."""
        return self._event_count

    @property
    def is_finalized(self) -> bool:
        """Check if display has been finalized."""
        return self._finalized
