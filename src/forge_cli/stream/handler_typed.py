"""Stream handler with typed API support."""

import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass

from ..display.v3.base import Display

# Note: Registry system removed - all processing now done in v3 renderers
from ..response._types import Response

# Additional imports for proper typing

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
    """Lightweight streaming state container - most data comes from response object."""

    # Event counters (needed for streaming metrics)
    event_count: int = 0

    # Vector store IDs used in this session (from configuration, not in response)
    vector_store_ids: set[str] = field(default_factory=set)

    # Last completed Response object - the source of truth for all response data
    response: Response | None = None

    def initialize_vector_store_ids(self, vector_store_ids: list[str]) -> None:
        """Initialize vector store IDs from user configuration.

        Args:
            vector_store_ids: List of vector store IDs from user configuration
        """
        if vector_store_ids:
            self.vector_store_ids.update(vector_store_ids)

    def get_vector_store_ids(self) -> list[str]:
        """Get the list of vector store IDs used in this session.

        Returns:
            Sorted list of unique vector store IDs
        """
        return sorted(self.vector_store_ids)


class TypedStreamHandler:
    """Stream handler that works with typed Response streams only."""

    def __init__(self, display: Display, debug: bool = False):
        """Initialize with display and debug settings."""
        self.display = display
        self.debug = debug
        # Note: Registry system removed - processing now handled directly by v3 renderers

    async def handle_stream(
        self,
        stream: AsyncIterator[tuple[str, Response | None]],
        initial_request: str,
        vector_store_ids: list[str] | None = None,
    ) -> StreamState:
        """
        Handle streaming events from typed API.

        Args:
            stream: Iterator yielding (event_type, Response) tuples
            initial_request: The initial query/request text
            vector_store_ids: Optional list of vector store IDs from user configuration

        Returns:
            Final StreamState after processing all events
        """
        state = StreamState()

        # Initialize vector store IDs from user configuration if provided
        if vector_store_ids:
            state.initialize_vector_store_ids(vector_store_ids)

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
                # Store the Response snapshot directly
                state.response = event_data
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
                if event_data:
                    # Use type guard to safely extract error message
                    from ..response.type_guards import get_error_message

                    extracted_msg = get_error_message(event_data)
                    if extracted_msg:
                        error_msg = extracted_msg
                self.display.show_error(error_msg)
                break

            # Debug logging for non-snapshot events
            if self.debug and event_data is None:
                print(f"  └─ Event {event_type} (no data)")

            last_event_time = current_time

        return state

    # Note: Most processing logic has been moved to v3 renderers
    # The TypedStreamHandler now focuses purely on routing Response objects to displays
