"""State management models for streaming responses."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Import proper types from response system
from ..response._types.response_output_item import ResponseOutputItem
from ..response._types.response_usage import ResponseUsage


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

    # Extracted citations
    citations: list[dict[str, str | int]] = field(default_factory=list)

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
        """Update state from response snapshot."""
        if "output" in snapshot:
            # Convert dict-based output items to typed objects if needed
            output_data = snapshot["output"]
            if output_data:
                self.output_items = self._convert_output_items(output_data)
            self._extract_file_mappings()
            self._extract_reasoning()

        if "usage" in snapshot:
            usage_data = snapshot["usage"]
            if isinstance(usage_data, dict):
                # Convert dict to ResponseUsage
                from ..response._types.response_usage import InputTokensDetails, OutputTokensDetails
                self.usage = ResponseUsage(
                    input_tokens=usage_data.get("input_tokens", 0),
                    output_tokens=usage_data.get("output_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                    input_tokens_details=InputTokensDetails(
                        cached_tokens=usage_data.get("input_tokens_details", {}).get("cached_tokens", 0)
                    ),
                    output_tokens_details=OutputTokensDetails(
                        reasoning_tokens=usage_data.get("output_tokens_details", {}).get("reasoning_tokens", 0)
                    ),
                )
            elif hasattr(usage_data, 'model_validate'):
                self.usage = ResponseUsage.model_validate(usage_data)
            else:
                self.usage = usage_data

        if "id" in snapshot:
            self.response_id = snapshot["id"]

        if "model" in snapshot:
            self.model = snapshot["model"]

    def _convert_output_items(self, output_data: list[Any]) -> list[ResponseOutputItem]:
        """Convert dict-based output items to typed ResponseOutputItem objects."""
        typed_items = []
        
        for item_data in output_data:
            if isinstance(item_data, dict):
                # Convert dict to proper typed object based on type
                item_type = item_data.get("type")
                if item_type:
                    try:
                        # Import specific types as needed
                        if item_type == "message":
                            from ..response._types.response_output_message import ResponseOutputMessage
                            typed_items.append(ResponseOutputMessage.model_validate(item_data))
                        elif item_type == "reasoning":
                            from ..response._types.response_reasoning_item import ResponseReasoningItem
                            typed_items.append(ResponseReasoningItem.model_validate(item_data))
                        elif item_type == "file_search_call":
                            from ..response._types.response_file_search_tool_call import ResponseFileSearchToolCall
                            typed_items.append(ResponseFileSearchToolCall.model_validate(item_data))
                        elif item_type == "document_finder_call":
                            from ..response._types.response_document_finder_tool_call import ResponseDocumentFinderToolCall
                            typed_items.append(ResponseDocumentFinderToolCall.model_validate(item_data))
                        elif item_type == "function_call":
                            from ..response._types.response_function_tool_call import ResponseFunctionToolCall
                            typed_items.append(ResponseFunctionToolCall.model_validate(item_data))
                        elif item_type == "web_search":
                            from ..response._types.response_function_web_search import ResponseFunctionWebSearch
                            typed_items.append(ResponseFunctionWebSearch.model_validate(item_data))
                        elif item_type == "file_reader":
                            from ..response._types.response_function_file_reader import ResponseFunctionFileReader
                            typed_items.append(ResponseFunctionFileReader.model_validate(item_data))
                        elif item_type == "computer_tool_call":
                            from ..response._types.response_computer_tool_call import ResponseComputerToolCall
                            typed_items.append(ResponseComputerToolCall.model_validate(item_data))
                        else:
                            # Skip unknown types for now
                            continue
                    except Exception as e:
                        # If validation fails, skip the item (but could log for debugging)
                        # print(f"Failed to validate {item_type}: {e}")
                        continue
            else:
                # Already a typed object, keep as is
                typed_items.append(item_data)
        
        return typed_items

    def _extract_file_mappings(self) -> None:
        """Extract file ID to name mappings from output items."""
        for item in self.output_items:
            # Handle typed objects
            if hasattr(item, 'type'):
                item_type = item.type
            else:
                # Fallback for dict format
                item_type = item.get("type", "") if isinstance(item, dict) else ""

            # Extract from file search results
            if item_type == "file_search_call":
                results = getattr(item, 'results', None) if hasattr(item, 'results') else item.get("results") if isinstance(item, dict) else None
                if results:
                    for result in results:
                        # Handle both typed and dict results
                        if hasattr(result, 'file_id') and hasattr(result, 'filename'):
                            file_id = result.file_id
                            filename = result.filename
                        elif isinstance(result, dict):
                            file_id = result.get("file_id", "")
                            filename = result.get("filename", "")
                        else:
                            continue
                        
                        if file_id and filename:
                            self.file_id_to_name[file_id] = filename

            # Extract from document finder results
            elif item_type == "document_finder_call":
                results = getattr(item, 'results', None) if hasattr(item, 'results') else item.get("results") if isinstance(item, dict) else None
                if results:
                    for result in results:
                        # Handle both typed and dict results
                        if hasattr(result, 'doc_id') and hasattr(result, 'title'):
                            doc_id = result.doc_id
                            title = result.title
                        elif isinstance(result, dict):
                            doc_id = result.get("doc_id", "")
                            title = result.get("title", "")
                        else:
                            continue
                        
                        if doc_id and title:
                            self.file_id_to_name[doc_id] = title

    def _extract_reasoning(self) -> None:
        """Extract reasoning text from output items."""
        reasoning_texts = []

        for item in self.output_items:
            # Handle typed objects
            if hasattr(item, 'type'):
                item_type = item.type
            else:
                # Fallback for dict format
                item_type = item.get("type", "") if isinstance(item, dict) else ""
            
            if item_type == "reasoning":
                # Handle typed ResponseReasoningItem
                if hasattr(item, 'summary'):
                    summary_list = item.summary
                else:
                    # Fallback for dict format
                    summary_list = item.get("summary", []) if isinstance(item, dict) else []
                
                for summary in summary_list:
                    # Handle both typed and dict summary items
                    if hasattr(summary, 'type') and summary.type == "summary_text":
                        text = getattr(summary, 'text', '')
                    elif isinstance(summary, dict) and summary.get("type") == "summary_text":
                        text = summary.get("text", "")
                    else:
                        continue
                    
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

    def get_completed_tools(self) -> list[dict[str, str | int | float]]:
        """Get display info for all completed tools."""
        completed: list[dict[str, str | int | float]] = []

        for tool_state in self.tool_states.values():
            if tool_state.status == ToolStatus.COMPLETED:
                completed.append(tool_state.to_display_info())

        return completed
