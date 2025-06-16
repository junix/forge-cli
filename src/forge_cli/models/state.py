"""State management models for streaming responses."""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..response._types.annotations import Annotation

# Import proper types from response system
from ..response._types.response import Response
from ..response._types.response_output_item import ResponseOutputItem
from ..response._types.response_usage import ResponseUsage
from ..response.type_guards import (
    get_tool_results,
    is_file_citation,
    is_file_path,
    is_file_search_call,
    is_message_item,
    is_output_text,
    is_reasoning_item,
    is_url_citation,
)


class ToolStatus(Enum):
    """Status of a tool execution."""

    IDLE = "idle"
    SEARCHING = "searching"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class ToolState:
    """State for a specific tool execution."""

    tool_type: str = ""
    query: str = ""
    queries: list[str] = field(default_factory=list)
    results_count: int | None = None
    status: ToolStatus = ToolStatus.IDLE
    query_time: float | None = None
    retrieval_time: float | None = None

    def to_display_info(self) -> dict[str, str | int | float]:
        """Convert to display information dictionary."""
        info = {"tool_type": self.tool_type}

        if self.query:
            info["query"] = self.query
            if self.query_time:
                info["query_time"] = self.query_time

        if self.status == ToolStatus.COMPLETED:
            info["results_count"] = self.results_count
            if self.retrieval_time:
                info["retrieval_time"] = self.retrieval_time

        return info


@dataclass
class StreamState:
    """Manages complete state during streaming."""

    # Current output items from latest snapshot using typed API
    output_items: list[ResponseOutputItem] = field(default_factory=list)

    # Tool states by tool type
    tool_states: dict[str, ToolState] = field(default_factory=dict)

    # File ID to filename mapping
    file_id_to_name: dict[str, str] = field(default_factory=dict)

    # Extracted citations using typed API
    citations: list["Annotation"] = field(default_factory=list)

    # Current reasoning text
    current_reasoning: str = ""

    # Usage statistics using typed API
    usage: ResponseUsage | None = None

    # Event counters
    event_count: int = 0
    response_event_count: int = 0

    # Response metadata
    response_id: str | None = None
    model: str | None = None

    def update_from_snapshot(self, snapshot: Response) -> None:
        """Update state from typed Response snapshot."""
        if isinstance(snapshot, Response):
            # Typed Response only - direct access to properties
            self.output_items = list(snapshot.output)
            self._extract_file_mappings()
            self._extract_reasoning()
            self._extract_citations()

            # Update usage statistics
            if snapshot.usage:
                self.usage = snapshot.usage

            # Update response metadata
            self.response_id = snapshot.id
            self.model = snapshot.model

    def _extract_file_mappings(self) -> None:
        """Extract file ID to name mappings from output items using type guards."""
        for item in self.output_items:
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

    def _extract_reasoning(self) -> None:
        """Extract reasoning text from output items using type guards."""
        reasoning_texts = []

        for item in self.output_items:
            if is_reasoning_item(item):
                # After type guard, we can safely access summary
                if item.summary:
                    for summary_item in item.summary:
                        # Summary items are typed, so we can access text directly
                        if hasattr(summary_item, "text") and summary_item.text:
                            reasoning_texts.append(summary_item.text)

        self.current_reasoning = "\n\n".join(reasoning_texts)

    def _extract_citations(self) -> None:
        """Extract citations from message content annotations using type guards."""
        citations = []

        for item in self.output_items:
            if is_message_item(item):
                # After type guard, we can safely access content
                if item.content:
                    for content in item.content:
                        if is_output_text(content) and content.annotations:
                            for annotation in content.annotations:
                                # Type guards ensure these are properly typed
                                if (
                                    is_file_citation(annotation)
                                    or is_url_citation(annotation)
                                    or is_file_path(annotation)
                                ):
                                    citations.append(annotation)

        self.citations = citations

    def get_tool_state(self, tool_type: str) -> ToolState:
        """Get or create tool state for a specific tool type."""
        # Normalize tool type
        base_tool_type = tool_type
        for pattern in ["response.", "_call", ".searching", ".completed", ".in_progress"]:
            base_tool_type = base_tool_type.replace(pattern, "")

        if base_tool_type not in self.tool_states:
            self.tool_states[base_tool_type] = ToolState(tool_type=base_tool_type)

        return self.tool_states[base_tool_type]

    def get_completed_tools(self) -> list[dict[str, str | int | float]]:
        """Get display info for all completed tools."""
        completed: list[dict[str, str | int | float]] = []

        for tool_state in self.tool_states.values():
            if tool_state.status == ToolStatus.COMPLETED:
                completed.append(tool_state.to_display_info())

        return completed
