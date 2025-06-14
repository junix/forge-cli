"""State management models for streaming responses."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional


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
    queries: List[str] = field(default_factory=list)
    results_count: Optional[int] = None
    status: ToolStatus = ToolStatus.IDLE
    query_time: Optional[float] = None
    retrieval_time: Optional[float] = None

    def to_display_info(self) -> Dict[str, Any]:
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

    # Current output items from latest snapshot
    output_items: List[Dict[str, Any]] = field(default_factory=list)

    # Tool states by tool type
    tool_states: Dict[str, ToolState] = field(default_factory=dict)

    # File ID to filename mapping
    file_id_to_name: Dict[str, str] = field(default_factory=dict)

    # Extracted citations
    citations: List[Dict[str, Any]] = field(default_factory=list)

    # Current reasoning text
    current_reasoning: str = ""

    # Usage statistics
    usage: Dict[str, int] = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})

    # Event counters
    event_count: int = 0
    response_event_count: int = 0

    # Response metadata
    response_id: Optional[str] = None
    model: Optional[str] = None

    def update_from_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Update state from response snapshot."""
        if "output" in snapshot:
            self.output_items = snapshot["output"]
            self._extract_file_mappings()
            self._extract_reasoning()

        if "usage" in snapshot:
            self.usage.update(snapshot["usage"])

        if "id" in snapshot:
            self.response_id = snapshot["id"]

        if "model" in snapshot:
            self.model = snapshot["model"]

    def _extract_file_mappings(self) -> None:
        """Extract file ID to name mappings from output items."""
        for item in self.output_items:
            item_type = item.get("type", "")

            # Extract from file search results
            if item_type == "file_search_call" and item.get("results"):
                for result in item["results"]:
                    if isinstance(result, dict):
                        file_id = result.get("file_id", "")
                        filename = result.get("filename", "")
                        if file_id and filename:
                            self.file_id_to_name[file_id] = filename

            # Extract from document finder results
            elif item_type == "document_finder_call" and item.get("results"):
                for result in item["results"]:
                    if isinstance(result, dict):
                        doc_id = result.get("doc_id", "")
                        title = result.get("title", "")
                        if doc_id and title:
                            self.file_id_to_name[doc_id] = title

    def _extract_reasoning(self) -> None:
        """Extract reasoning text from output items."""
        reasoning_texts = []

        for item in self.output_items:
            if item.get("type") == "reasoning":
                for summary in item.get("summary", []):
                    if summary.get("type") == "summary_text":
                        text = summary.get("text", "")
                        if text:
                            reasoning_texts.append(text)

        self.current_reasoning = "\n\n".join(reasoning_texts)

    def get_tool_state(self, tool_type: str) -> ToolState:
        """Get or create tool state for a specific tool type."""
        # Normalize tool type
        base_tool_type = tool_type
        for pattern in ["response.", "_call", ".searching", ".completed", ".in_progress"]:
            base_tool_type = base_tool_type.replace(pattern, "")

        if base_tool_type not in self.tool_states:
            self.tool_states[base_tool_type] = ToolState(tool_type=base_tool_type)

        return self.tool_states[base_tool_type]

    def get_completed_tools(self) -> List[Dict[str, Any]]:
        """Get display info for all completed tools."""
        completed = []

        for tool_state in self.tool_states.values():
            if tool_state.status == ToolStatus.COMPLETED:
                completed.append(tool_state.to_display_info())

        return completed
