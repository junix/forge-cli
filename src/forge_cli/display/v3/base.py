"""Base display interface for v3 - pure rendering without input handling."""

from abc import ABC, abstractmethod
from typing import Protocol

from forge_cli.response._types.response import Response


class Renderer(Protocol):
    """Pure renderer protocol - only handles output formatting."""

    def render_response(self, response: Response) -> None:
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
    def render_response(self, response: Response) -> None:
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

    def __init__(self, renderer: Renderer, mode: str = "default"):
        """Initialize display with a renderer.

        Args:
            renderer: The renderer implementation to use
            mode: Display mode ("default" or "chat")
        """
        self._renderer = renderer
        self._event_count = 0
        self._finalized = False
        self._mode = mode

        # Set chat mode on renderer if it supports it
        if hasattr(renderer, "_in_chat_mode"):
            renderer._in_chat_mode = mode == "chat"

    def handle_response(self, response: Response) -> None:
        """Route events to renderer.

        Args:
            event_type: Type of event
            data: Event-specific data
        """
        if self._finalized:
            raise RuntimeError("Display already finalized")

        self._event_count += 1
        self._renderer.render_response(response)

    def complete(self) -> None:
        """Finalize display."""
        if not self._finalized:
            self._renderer.finalize()
            self._finalized = True

    def show_error(self, error: str) -> None:
        """Show error if renderer supports it."""
        if hasattr(self._renderer, "render_error"):
            self._renderer.render_error(error)

    def show_welcome(self, config: object) -> None:
        """Show welcome message if renderer supports it."""
        if hasattr(self._renderer, "render_welcome"):
            self._renderer.render_welcome(config)

    def show_request_info(self, info: dict) -> None:
        """Show request information if renderer supports it."""
        if hasattr(self._renderer, "render_request_info"):
            self._renderer.render_request_info(info)
        elif hasattr(self._renderer, "_console"):
            # Fallback for rich renderers
            console = self._renderer._console
            console.print(f"[cyan]Query:[/cyan] {info.get('question', 'N/A')}")
            if info.get("model"):
                console.print(f"[cyan]Model:[/cyan] {info['model']}")
            if info.get("tools"):
                console.print(f"[cyan]Tools:[/cyan] {', '.join(info['tools'])}")

    def show_status(self, message: str) -> None:
        """Show status message if renderer supports it."""
        if hasattr(self._renderer, "render_status"):
            self._renderer.render_status(message)
        elif hasattr(self._renderer, "_console"):
            # Fallback for rich renderers
            self._renderer._console.print(f"[yellow]Status:[/yellow] {message}")

    @property
    def event_count(self) -> int:
        """Get total number of events handled."""
        return self._event_count

    @property
    def is_finalized(self) -> bool:
        """Check if display has been finalized."""
        return self._finalized

    @property
    def mode(self) -> str:
        """Get display mode."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Set display mode."""
        self._mode = value
        # Update renderer if it supports mode changes
        if hasattr(self._renderer, "_in_chat_mode"):
            self._renderer._in_chat_mode = value == "chat"
