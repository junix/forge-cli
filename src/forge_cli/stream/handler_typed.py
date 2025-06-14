"""Stream handler with typed API support."""

import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

from ..display.v3.base import Display
# Note: Registry system removed - all processing now done in v3 renderers
from ..response._types import Response

# Removed MigrationHelper - using typed Response directly

# Tool status type alias
ToolStatusType = Literal["idle", "searching", "in_progress", "completed", "failed"]


@dataclass
class ToolState:
    """State for a specific tool execution."""

    tool_type: str = ""
    query: str = ""
    queries: list[str] = field(default_factory=list)
    results_count: int | None = None
    status: ToolStatusType = "idle"
    query_time: float | None = None
    retrieval_time: float | None = None

    def to_display_info(self) -> dict[str, str | int | float]:
        """Convert to display information dictionary."""
        info: dict[str, str | int | float] = {"tool_type": self.tool_type}

        if self.query:
            info["query"] = self.query
            if self.query_time:
                info["query_time"] = self.query_time

        if self.status == "completed":
            info["results_count"] = self.results_count or 0
            if self.retrieval_time:
                info["retrieval_time"] = self.retrieval_time

        return info


@dataclass
class StreamState:
    """Manages complete state during streaming, compatible with both APIs."""

    # Current output items from latest snapshot
    output_items: list[Any] = field(default_factory=list)

    # Tool states by tool type
    tool_states: dict[str, ToolState] = field(default_factory=dict)

    # File ID to filename mapping
    file_id_to_name: dict[str, str] = field(default_factory=dict)

    # Extracted citations
    citations: list[dict[str, Any]] = field(default_factory=list)

    # Current reasoning text
    current_reasoning: str = ""

    # Usage statistics
    usage: dict[str, int] = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})

    # Event counters
    event_count: int = 0
    response_event_count: int = 0

    # Response metadata
    response_id: str | None = None
    model: str | None = None

    def update_from_snapshot(self, snapshot: Response) -> None:
        """Update state from typed Response snapshot."""
        if isinstance(snapshot, Response):
            # Typed Response only
            self.output_items = list(snapshot.output)
            self._extract_file_mappings_typed(snapshot)
            self._extract_reasoning_typed(snapshot)

            if snapshot.usage:
                self.usage = {
                    "input_tokens": snapshot.usage.input_tokens,
                    "output_tokens": snapshot.usage.output_tokens,
                    "total_tokens": snapshot.usage.total_tokens,
                }

            self.response_id = snapshot.id
            self.model = snapshot.model

    def _extract_file_mappings_typed(self, response: Response) -> None:
        """Extract file mappings from typed Response."""
        for item in response.output:
            if hasattr(item, "type") and "search_call" in item.type:
                if hasattr(item, "results") and item.results:
                    for result in item.results:
                        if hasattr(result, "file_id") and hasattr(result, "filename"):
                            self.file_id_to_name[result.file_id] = result.filename

    def _extract_reasoning_typed(self, response: Response) -> None:
        """Extract reasoning from typed Response."""
        for item in response.output:
            if hasattr(item, "type") and item.type == "reasoning":
                if hasattr(item, "summary"):
                    # Extract text from summary items
                    texts = []
                    for summary_item in item.summary:
                        if hasattr(summary_item, "text"):
                            texts.append(summary_item.text)
                    self.current_reasoning = " ".join(texts)


class TypedStreamHandler:
    """Stream handler that works with typed Response streams only."""

    def __init__(self, display: Display, debug: bool = False):
        """Initialize with display and debug settings."""
        self.display = display
        self.debug = debug
        # Note: Registry system removed - processing now handled directly by v3 renderers

    async def handle_stream(
        self, stream: AsyncIterator[tuple[str, Response | None]], initial_request: str
    ) -> StreamState:
        """
        Handle streaming events from typed API.

        Args:
            stream: Iterator yielding (event_type, Response) tuples
            initial_request: The initial query/request text

        Returns:
            Final StreamState after processing all events
        """
        state = StreamState()

        # Track timing
        start_time = time.time()
        last_event_time = start_time

        # Process events
        async for event_type, event_data in stream:
            current_time = time.time()
            state.event_count += 1

            if self.debug:
                if event_data is not None and isinstance(event_data, Response):
                    # Show the FULL model dump for Response objects
                    print(f"[{state.event_count}] {event_type}: Response data:")
                    try:
                        # Use model_dump() to get the full dictionary representation
                        import json
                        full_dump = event_data.model_dump()
                        # Pretty print the entire response with indentation
                        print(json.dumps(full_dump, indent=2, ensure_ascii=False))
                    except Exception as e:
                        # Fallback if model_dump fails
                        print(f"  Error dumping model: {e}")
                        print(f"  Response repr: {repr(event_data)}")
                else:
                    print(f"[{state.event_count}] {event_type}: {type(event_data)}")

            # Handle snapshot events (events with Response objects)
            if event_data is not None and isinstance(event_data, Response):
                # Update state from Response
                state.update_from_snapshot(event_data)

                # Render the complete Response snapshot using v3 display
                self.display.handle_response(event_data)

            # Handle lifecycle events
            elif event_type == "done":
                # Stream completed
                self.display.complete()
                break

            elif event_type == "error":
                # Stream error
                error_msg = "Stream error occurred"
                if event_data and hasattr(event_data, "message"):
                    error_msg = event_data.message
                self.display.show_error(error_msg)
                break

            # Debug logging for non-snapshot events
            if self.debug and event_data is None:
                print(f"  └─ Event {event_type} (no data)")

            last_event_time = current_time

        return state

    # Note: Most processing logic has been moved to v3 renderers
    # The TypedStreamHandler now focuses purely on routing Response objects to displays
