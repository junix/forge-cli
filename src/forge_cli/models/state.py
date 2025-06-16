"""State management models for streaming responses."""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..response._types.annotations import Annotation

# Import proper types from response system
from ..response._types.response_output_item import ResponseOutputItem
from ..response._types.response_usage import ResponseUsage
from ..response.type_guards import (
    is_message_item,
    is_reasoning_item,
    is_file_search_call,
    is_document_finder_call,
    is_file_citation,
    is_url_citation,
    is_file_path,
    is_output_text,
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

    def update_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Update state from response snapshot.
        
        Expects snapshot to contain typed Response objects or compatible data.
        """
        if "output" in snapshot:
            output_data = snapshot["output"]
            if output_data:
                # Expect typed objects; if dicts are provided, attempt conversion
                if isinstance(output_data, list):
                    self.output_items = []
                    for item in output_data:
                        if hasattr(item, "type"):
                            # Already a typed object
                            self.output_items.append(item)
                        elif isinstance(item, dict) and "type" in item:
                            # Try to convert dict to typed object
                            typed_item = self._convert_single_output_item(item)
                            if typed_item:
                                self.output_items.append(typed_item)
                else:
                    self.output_items = output_data
                    
            self._extract_file_mappings()
            self._extract_reasoning()
            self._extract_citations()

        if "usage" in snapshot:
            usage_data = snapshot["usage"]
            if isinstance(usage_data, ResponseUsage):
                self.usage = usage_data
            elif isinstance(usage_data, dict):
                # Convert dict to ResponseUsage
                from ..response._types.response_usage import InputTokensDetails, OutputTokensDetails

                self.usage = ResponseUsage(
                    input_tokens=usage_data.get("input_tokens", 0),
                    output_tokens=usage_data.get("output_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                    input_tokens_details=InputTokensDetails(
                        cached_tokens=usage_data.get("input_tokens_details", {}).get("cached_tokens", 0)
                    ) if usage_data.get("input_tokens_details") else None,
                    output_tokens_details=OutputTokensDetails(
                        reasoning_tokens=usage_data.get("output_tokens_details", {}).get("reasoning_tokens", 0)
                    ) if usage_data.get("output_tokens_details") else None,
                )

        if "id" in snapshot:
            self.response_id = snapshot["id"]

        if "model" in snapshot:
            self.model = snapshot["model"]

    def _convert_single_output_item(self, item_data: dict[str, Any]) -> ResponseOutputItem | None:
        """Convert a single dict-based output item to typed ResponseOutputItem object.
        
        Returns None if conversion fails or type is unknown.
        """
        item_type = item_data.get("type")
        if not item_type:
            return None
            
        try:
            # Import and validate based on type
            if item_type == "message":
                from ..response._types.response_output_message import ResponseOutputMessage
                return ResponseOutputMessage.model_validate(item_data)
                
            elif item_type == "reasoning":
                from ..response._types.response_reasoning_item import ResponseReasoningItem
                return ResponseReasoningItem.model_validate(item_data)
                
            elif item_type == "file_search_call":
                from ..response._types.response_file_search_tool_call import ResponseFileSearchToolCall
                return ResponseFileSearchToolCall.model_validate(item_data)
                
            elif item_type == "document_finder_call":
                from ..response._types.response_document_finder_tool_call import ResponseDocumentFinderToolCall
                return ResponseDocumentFinderToolCall.model_validate(item_data)
                
            elif item_type == "function_call":
                from ..response._types.response_function_tool_call import ResponseFunctionToolCall
                return ResponseFunctionToolCall.model_validate(item_data)
                
            elif item_type == "web_search_call":
                from ..response._types.response_function_web_search import ResponseFunctionWebSearch
                return ResponseFunctionWebSearch.model_validate(item_data)
                
            elif item_type == "file_reader_call":
                from ..response._types.response_function_file_reader import ResponseFunctionFileReader
                return ResponseFunctionFileReader.model_validate(item_data)
                
            elif item_type == "computer_tool_call":
                from ..response._types.response_computer_tool_call import ResponseComputerToolCall
                return ResponseComputerToolCall.model_validate(item_data)
                
            elif item_type == "code_interpreter_call":
                from ..response._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
                return ResponseCodeInterpreterToolCall.model_validate(item_data)
                
            else:
                # Unknown type
                return None
                
        except Exception:
            # Validation failed
            return None

    def _extract_file_mappings(self) -> None:
        """Extract file ID to name mappings from output items."""
        for item in self.output_items:
            # Extract from file search results
            if is_file_search_call(item):
                # File search results are not directly accessible from tool call
                pass

            # Extract from document finder results
            elif is_document_finder_call(item):
                # Document finder results are not directly accessible from tool call
                pass

    def _extract_reasoning(self) -> None:
        """Extract reasoning text from output items."""
        reasoning_texts = []

        for item in self.output_items:
            if is_reasoning_item(item):
                if item.summary:
                    for summary in item.summary:
                        # Check for both "summary_text" and "text" types (API variation)
                        if hasattr(summary, "type") and summary.type in ["summary_text", "text"]:
                            if summary.text:
                                reasoning_texts.append(summary.text)

        self.current_reasoning = "\n\n".join(reasoning_texts)

    def _extract_citations(self) -> None:
        """Extract citations from message content annotations."""
        citations = []

        for item in self.output_items:
            if is_message_item(item):
                if item.content:
                    for content in item.content:
                        if is_output_text(content) and content.annotations:
                            for annotation in content.annotations:
                                # Type guards ensure these are properly typed
                                if is_file_citation(annotation) or is_url_citation(annotation) or is_file_path(annotation):
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
