"""Stream handler with typed API support."""

import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ..response._types.annotations import Annotation

from ..display.v3.base import Display

# Note: Registry system removed - all processing now done in v3 renderers
from ..response._types import Response
from ..response._types.response_output_item import ResponseOutputItem

# Additional imports for proper typing
from ..response.type_guards import (
    get_tool_results,
    is_file_search_call,
    is_reasoning_item,
)

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
    output_items: list[ResponseOutputItem] = field(default_factory=list)

    # Tool states by tool type
    tool_states: dict[str, ToolState] = field(default_factory=dict)

    # File ID to filename mapping
    file_id_to_name: dict[str, str] = field(default_factory=dict)

    # Extracted citations using type-based API instead of dict[str, Any]
    citations: "list[Annotation]" = field(default_factory=list)  # Using string annotation due to import issues

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

    # Vector store IDs used in this session
    vector_store_ids: set[str] = field(default_factory=set)

    def update_from_snapshot(self, snapshot: Response) -> None:
        """Update state from typed Response snapshot."""
        if isinstance(snapshot, Response):
            # Typed Response only
            self.output_items = list(snapshot.output)
            self._extract_file_mappings_typed(snapshot)
            self._extract_reasoning_typed(snapshot)
            self._extract_citations_typed(snapshot)

            if snapshot.usage:
                self.usage = {
                    "input_tokens": snapshot.usage.input_tokens,
                    "output_tokens": snapshot.usage.output_tokens,
                    "total_tokens": snapshot.usage.total_tokens,
                }

            self.response_id = snapshot.id
            self.model = snapshot.model

    def _extract_file_mappings_typed(self, response: Response) -> None:
        """Extract file mappings from typed Response using type guards."""
        for item in response.output:
            if is_file_search_call(item):
                # After type guard, we know item is ResponseFileSearchToolCall
                results = get_tool_results(item)
                for result in results:
                    # File search results should have file_id and filename
                    # Use getattr with defaults for safer access
                    file_id = getattr(result, "file_id", None)
                    filename = getattr(result, "filename", None)
                    if file_id and filename:
                        self.file_id_to_name[file_id] = filename

    def get_accessed_files(self) -> list[str]:
        """Get list of files accessed during this stream session."""
        return list(self.file_id_to_name.values())

    def _extract_reasoning_typed(self, response: Response) -> None:
        """Extract reasoning from typed Response using type guards."""
        for item in response.output:
            if is_reasoning_item(item):
                # After type guard, we can safely access summary
                texts = []
                for summary_item in item.summary:
                    # Summary items are typed, so we can access text directly
                    texts.append(summary_item.text)
                self.current_reasoning = " ".join(texts)

    def _extract_citations_typed(self, response: Response) -> None:
        """Extract citations from typed Response using type guards."""
        citations = []

        for item in response.output:
            # Use proper type checking instead of hasattr - following codebase patterns
            if hasattr(item, "type") and item.type == "message":
                if hasattr(item, "content") and item.content:
                    for content in item.content:
                        if hasattr(content, "type") and content.type == "output_text":
                            if hasattr(content, "annotations") and content.annotations:
                                for annotation in content.annotations:
                                    # Check for citation types - these are the concrete Citation types
                                    if hasattr(annotation, "type") and annotation.type in [
                                        "file_citation",  # AnnotationFileCitation
                                        "url_citation",  # AnnotationURLCitation
                                        "file_path",  # AnnotationFilePath
                                    ]:
                                        citations.append(annotation)

        self.citations = citations

    def initialize_vector_store_ids(self, vector_store_ids: list[str]) -> None:
        """Initialize vector store IDs from user configuration.

        Args:
            vector_store_ids: List of vector store IDs from user configuration
        """
        if vector_store_ids:
            self.vector_store_ids.update(vector_store_ids)

    def add_vector_store_ids(self, vector_store_ids: list[str]) -> None:
        """Add vector store IDs to the tracked set.

        Args:
            vector_store_ids: List of vector store IDs to add
        """
        self.vector_store_ids.update(vector_store_ids)

    def get_vector_store_ids(self) -> list[str]:
        """Get the list of vector store IDs used in this session.

        Returns:
            Sorted list of unique vector store IDs
        """
        return sorted(list(self.vector_store_ids))


class TypedStreamHandler:
    """Stream handler that works with typed Response streams only."""

    def __init__(self, display: Display, debug: bool = False):
        """Initialize with display and debug settings."""
        self.display = display
        self.debug = debug
        # Note: Registry system removed - processing now handled directly by v3 renderers

    async def handle_stream(
        self, stream: AsyncIterator[tuple[str, Response | None]], initial_request: str, vector_store_ids: list[str] | None = None
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
