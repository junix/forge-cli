"""Stream handler with typed API support."""

import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

from ..display.v3.base import Display
from ..processors.registry_typed import default_typed_registry, initialize_typed_registry
from ..response._types import Response
from ..response.adapters import MigrationHelper

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

    def update_from_snapshot(self, snapshot: dict[str, Any] | Response) -> None:
        """Update state from response snapshot (dict or typed)."""
        if isinstance(snapshot, Response):
            # Typed Response
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

        elif isinstance(snapshot, dict):
            # Dict response
            if "output" in snapshot:
                self.output_items = snapshot["output"]
                self._extract_file_mappings_dict()
                self._extract_reasoning_dict()

            if "usage" in snapshot:
                self.usage.update(snapshot["usage"])

            if "id" in snapshot:
                self.response_id = snapshot["id"]

            if "model" in snapshot:
                self.model = snapshot["model"]

    def _extract_file_mappings_typed(self, response: Response) -> None:
        """Extract file mappings from typed Response."""
        for item in response.output:
            if hasattr(item, "type") and "search_call" in item.type:
                if hasattr(item, "results") and item.results:
                    for result in item.results:
                        if hasattr(result, "file_id") and hasattr(result, "filename"):
                            self.file_id_to_name[result.file_id] = result.filename

    def _extract_file_mappings_dict(self) -> None:
        """Extract file mappings from dict output."""
        for item in self.output_items:
            if isinstance(item, dict):
                item_type = item.get("type", "")
                if "search_call" in item_type and item.get("results"):
                    for result in item["results"]:
                        if isinstance(result, dict):
                            file_id = result.get("file_id")
                            filename = result.get("filename")
                            if file_id and filename:
                                self.file_id_to_name[file_id] = filename

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

    def _extract_reasoning_dict(self) -> None:
        """Extract reasoning from dict output."""
        for item in self.output_items:
            if isinstance(item, dict) and item.get("type") == "reasoning":
                summary = item.get("summary", [])
                if isinstance(summary, list):
                    texts = []
                    for summary_item in summary:
                        if isinstance(summary_item, dict) and summary_item.get("type") == "summary_text":
                            text = summary_item.get("text", "")
                            if text:
                                texts.append(text)
                    self.current_reasoning = " ".join(texts)


class TypedStreamHandler:
    """Stream handler that works with both dict and typed Response streams."""

    def __init__(self, display: Display, debug: bool = False):
        """Initialize with display and debug settings."""
        self.display = display
        self.debug = debug
        # Initialize typed registry if not already done
        if not default_typed_registry._processors:
            initialize_typed_registry()
        self.processor_registry = default_typed_registry

    async def handle_stream(
        self, stream: AsyncIterator[tuple[str, dict[str, Any] | Response | None]], initial_request: str
    ) -> StreamState:
        """
        Handle streaming events from either dict or typed API.

        Args:
            stream: Iterator yielding (event_type, data) where data can be dict or Response
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
                print(f"[{state.event_count}] {event_type}")

            # Route events based on type
            if event_type == "response.created":
                self._handle_response_created(event_data, state)

            elif event_type == "response.output_item.added":
                # Update from snapshot for snapshot-based streaming
                if event_data:
                    state.update_from_snapshot(event_data)
                    # In v3, we render the complete Response snapshot
                    if isinstance(event_data, Response):
                        self.display.handle_response(event_data)

            elif event_type == "response.output_text.delta":
                # Update from snapshot and render complete response
                if event_data:
                    state.update_from_snapshot(event_data)
                    # In v3, we render the complete Response snapshot
                    if isinstance(event_data, Response):
                        self.display.handle_response(event_data)

            elif event_type.startswith("response.reasoning_summary_text."):
                # Handle reasoning events - in v3, just render the complete response
                if event_data:
                    state.update_from_snapshot(event_data)
                    if isinstance(event_data, Response):
                        self.display.handle_response(event_data)

            elif "searching" in event_type or "in_progress" in event_type:
                self._handle_tool_search(event_type, event_data, state, current_time - last_event_time)

            elif "completed" in event_type and "call" in event_type:
                self._handle_tool_complete(event_type, event_data, state, current_time - start_time)

            elif event_type == "response.completed":
                if event_data:
                    state.update_from_snapshot(event_data)
                    # Final response snapshot
                    if isinstance(event_data, Response):
                        self.display.handle_response(event_data)

            elif event_type == "done":
                break

            last_event_time = current_time

        # Final processing
        self.display.complete()

        return state

    def _handle_response_created(self, data: dict[str, Any] | Response | None, state: StreamState) -> None:
        """Handle response created event."""
        if isinstance(data, Response):
            state.response_id = data.id
            state.model = data.model
        elif isinstance(data, dict):
            state.response_id = data.get("id")
            state.model = data.get("model")

    def _extract_text(self, data: dict[str, Any] | Response | None) -> str:
        """Extract text from event data (works with both APIs)."""
        return MigrationHelper.safe_get_text(data)

    def _extract_reasoning_text(self, data: dict[str, Any] | Response | None) -> str:
        """Extract reasoning text from event data."""
        if isinstance(data, Response):
            # Extract from typed Response object
            for item in data.output:
                if hasattr(item, "type") and item.type == "reasoning":
                    if hasattr(item, "summary") and item.summary:
                        # Concatenate all summary texts
                        texts = []
                        for summary in item.summary:
                            if hasattr(summary, "text") and summary.text:
                                texts.append(summary.text)
                        return " ".join(texts)
        elif isinstance(data, dict):
            # For reasoning delta events, the text might be directly in the data
            text = data.get("text", "")
            if text:
                return text

            # Or in a reasoning structure
            reasoning = data.get("reasoning", {})
            if isinstance(reasoning, dict):
                # Could be in summary
                summary = reasoning.get("summary", "")
                if summary:
                    return summary
                # Or in summary_text
                summary_text = reasoning.get("summary_text", "")
                if summary_text:
                    return summary_text

            # Or check in output items for reasoning
            output = data.get("output", [])
            for item in output:
                if isinstance(item, dict) and item.get("type") == "reasoning":
                    # Extract from summary items
                    for summary in item.get("summary", []):
                        if isinstance(summary, dict) and summary.get("type") in ["summary_text", "text"]:
                            return summary.get("text", "")
        return ""

    # _process_output_items removed - v3 handles complete Response snapshots

    def _handle_tool_search(
        self, event_type: str, data: dict[str, Any] | Response | None, state: StreamState, query_time: float
    ) -> None:
        """Handle tool search events."""
        # Extract tool type
        tool_type = event_type.split(".")[1].replace("_call", "")

        # Create or update tool state
        if tool_type not in state.tool_states:
            state.tool_states[tool_type] = ToolState(tool_type=tool_type)

        tool_state = state.tool_states[tool_type]
        tool_state.status = "searching"
        tool_state.query_time = query_time

        # Extract queries
        if isinstance(data, Response):
            # Extract from typed Response
            for item in data.output:
                if hasattr(item, "type") and tool_type in item.type:
                    if hasattr(item, "queries"):
                        tool_state.queries = item.queries
                        tool_state.query = ", ".join(item.queries)
        elif isinstance(data, dict):
            # Extract from dict
            queries = data.get("queries", [])
            if queries:
                tool_state.queries = queries
                tool_state.query = ", ".join(queries)

        # In v3, we rely on the response snapshot to show tool status
        # The rich renderer will extract tool information from the response object

    def _handle_tool_complete(
        self, event_type: str, data: dict[str, Any] | Response | None, state: StreamState, retrieval_time: float
    ) -> None:
        """Handle tool completion events."""
        # Extract tool type
        tool_type = event_type.split(".")[1].replace("_call", "")

        if tool_type in state.tool_states:
            tool_state = state.tool_states[tool_type]
            tool_state.status = "completed"
            tool_state.retrieval_time = retrieval_time

            # Extract results count
            if isinstance(data, Response):
                # Count from typed Response
                results_count = 0
                for item in data.output:
                    if hasattr(item, "type") and tool_type in item.type:
                        if hasattr(item, "results") and item.results:
                            results_count = len(item.results)
                tool_state.results_count = results_count
            elif isinstance(data, dict):
                # Count from dict
                output = data.get("output", [])
                for item in output:
                    if isinstance(item, dict) and tool_type in item.get("type", ""):
                        results = item.get("results", [])
                        tool_state.results_count = len(results)

            # In v3, tool status is shown through the complete Response snapshot
            pass


# Export the typed handler as the default
StreamHandler = TypedStreamHandler
