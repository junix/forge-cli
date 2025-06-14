"""Plain text renderer - simple output without formatting."""

import sys
from typing import Any, Dict, Optional, TextIO

from ..base import BaseRenderer
from ..events import EventType


class PlainRenderer(BaseRenderer):
    """Simple text output renderer for non-interactive environments."""

    def __init__(self, file: Optional[TextIO] = None):
        """Initialize plain renderer.

        Args:
            file: Output file handle (defaults to stdout)
        """
        super().__init__()
        self._file = file or sys.stdout
        self._content_started = False
        self._in_reasoning = False
        self._active_tools = {}

    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Render a stream event as plain text."""
        self._ensure_not_finalized()

        # Convert to EventType enum if possible
        event_enum = EventType.from_string(event_type)

        if event_enum:
            # Use match statement for known event types
            match event_enum:
                case EventType.STREAM_START:
                    self._handle_stream_start(data)
                case EventType.TEXT_DELTA:
                    self._handle_text_delta(data)
                case EventType.TOOL_START:
                    self._handle_tool_start(data)
                case EventType.TOOL_COMPLETE:
                    self._handle_tool_complete(data)
                case EventType.REASONING_START:
                    self._handle_reasoning_start(data)
                case EventType.REASONING_DELTA:
                    self._handle_reasoning_delta(data)
                case EventType.REASONING_COMPLETE:
                    self._handle_reasoning_complete(data)
                case EventType.CITATION_FOUND:
                    self._handle_citation(data)
                case EventType.STREAM_ERROR:
                    self._handle_error(data)
                case _:
                    # Other known events we don't need to display
                    pass
        else:
            # Unknown event type - ignore in plain renderer
            pass

    def _handle_stream_start(self, data: Dict[str, Any]) -> None:
        """Handle stream start event."""
        query = data.get("query", "")
        if query:
            print(f"Query: {query}", file=self._file)
            print("-" * 40, file=self._file)

    def _handle_text_delta(self, data: Dict[str, Any]) -> None:
        """Handle text delta event."""
        text = data.get("text", "")
        if text:
            if not self._content_started:
                print("\nResponse:", file=self._file)
                self._content_started = True
            print(text, end="", flush=True, file=self._file)

    def _handle_tool_start(self, data: Dict[str, Any]) -> None:
        """Handle tool start event."""
        tool_id = data.get("tool_id", "unknown")
        tool_type = data.get("tool_type", "unknown")

        self._active_tools[tool_id] = tool_type
        print(f"\n[{tool_type.upper()}] Starting...", file=self._file)

    def _handle_tool_complete(self, data: Dict[str, Any]) -> None:
        """Handle tool complete event."""
        tool_id = data.get("tool_id", "unknown")
        tool_type = self._active_tools.get(tool_id, data.get("tool_type", "unknown"))
        results_count = data.get("results_count", 0)

        print(f"[{tool_type.upper()}] Complete ({results_count} results)", file=self._file)

        if tool_id in self._active_tools:
            del self._active_tools[tool_id]

    def _handle_reasoning_start(self, data: Dict[str, Any]) -> None:
        """Handle reasoning start event."""
        if not self._in_reasoning:
            print("\nThinking...", file=self._file)
            self._in_reasoning = True

    def _handle_reasoning_delta(self, data: Dict[str, Any]) -> None:
        """Handle reasoning delta event."""
        # In plain mode, we don't show reasoning content
        pass

    def _handle_reasoning_complete(self, data: Dict[str, Any]) -> None:
        """Handle reasoning complete event."""
        if self._in_reasoning:
            print("Done thinking.\n", file=self._file)
            self._in_reasoning = False

    def _handle_citation(self, data: Dict[str, Any]) -> None:
        """Handle citation found event."""
        citation_num = data.get("citation_num", 0)
        citation_text = data.get("citation_text", "")
        source = data.get("source", "")

        # Format citation based on available information
        if source:
            citation_display = f"[{citation_num}] {source}: {citation_text}"
        else:
            citation_display = f"[{citation_num}] {citation_text}"

        print(f"\n{citation_display}", file=self._file)

    def _handle_error(self, data: Dict[str, Any]) -> None:
        """Handle error event."""
        error = data.get("error", "Unknown error")
        print(f"\nError: {error}", file=self._file, flush=True)

    def finalize(self) -> None:
        """Complete rendering and ensure final newline."""
        if not self._finalized:
            if self._content_started:
                print("\n", file=self._file)  # Ensure final newline
            self._file.flush()
            self._finalized = True
