"""Main stream handler for processing API responses."""

import time
from collections.abc import AsyncIterator
from typing import Any, Literal
from dataclasses import dataclass, field

from ..display.v3.base import Display
from ..response._types import ResponseStatus
from ..processors.registry import default_registry

# Removed ResponseStreamEvent import to avoid isinstance issues with generics

# Tool status type alias using response types
ToolStatusType = Literal["idle", "searching", "in_progress", "completed", "failed"]


@dataclass
class ToolState:
    """State for a specific tool execution using response types."""

    tool_type: str = ""
    query: str = ""
    queries: list[str] = field(default_factory=list)
    results_count: int | None = None
    status: ToolStatusType = "idle"
    query_time: float | None = None
    retrieval_time: float | None = None

    def to_display_info(self) -> dict[str, str | int | float]:
        """Convert to display information dictionary."""
        info = {"tool_type": self.tool_type}

        if self.query:
            info["query"] = self.query
            if self.query_time:
                info["query_time"] = self.query_time

        if self.status == "completed":
            info["results_count"] = self.results_count
            if self.retrieval_time:
                info["retrieval_time"] = self.retrieval_time

        return info


@dataclass
class StreamState:
    """Manages complete state during streaming using response types."""

    # Current output items from latest snapshot
    output_items: list[dict[str, str | int | float | bool | list | dict]] = field(default_factory=list)

    # Tool states by tool type
    tool_states: dict[str, ToolState] = field(default_factory=dict)

    # File ID to filename mapping
    file_id_to_name: dict[str, str] = field(default_factory=dict)

    # Extracted citations
    citations: list[dict[str, str | int]] = field(default_factory=list)

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

    def update_from_snapshot(self, snapshot: dict[str, str | int | float | list | dict]) -> None:
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

    def get_completed_tools(self) -> list[dict[str, str | int | float]]:
        """Get display info for all completed tools."""
        completed: list[dict[str, str | int | float]] = []

        for tool_state in self.tool_states.values():
            if tool_state.status == "completed":
                completed.append(tool_state.to_display_info())

        return completed


class StreamHandler:
    """Handles streaming responses with clean architecture."""

    def __init__(self, display: Display, debug: bool = False):
        self.display = display
        self.debug = debug
        self.state = StreamState()
        self.processor_registry = default_registry

        # Timing variables
        self.start_time = time.time()
        self.search_start_time: float | None = None
        self.search_completed_time: float | None = None

    async def handle_stream(
        self,
        event_stream: AsyncIterator[tuple[str, dict[str, Any] | Any | None]],
        question: str,
    ) -> dict[str, str | int | float | bool | list | dict] | None:
        """
        Process event stream and return final response.

        Args:
            event_stream: Async iterator of (event_type, event_data) tuples
            question: The user's question for display

        Returns:
            Final response data or None if error
        """
        try:
            async for event_type, event_data in event_stream:
                self.state.event_count += 1

                # Count response events
                if event_type and event_type.startswith("response"):
                    self.state.response_event_count += 1

                # Handle typed events - check for Pydantic model rather than specific type
                if hasattr(event_data, "model_dump") and callable(getattr(event_data, "model_dump")):
                    # Convert typed event to dict for compatibility
                    event_dict = event_data.model_dump(by_alias=True, exclude_none=True)
                elif isinstance(event_data, dict):
                    event_dict = event_data
                else:
                    event_dict = {}

                # Update usage if present
                if "usage" in event_dict:
                    self.state.usage.update(event_dict["usage"])

                # Debug logging
                if self.debug:
                    await self._log_debug_info(event_type, event_dict)

                # Route event to appropriate handler
                if event_type == "done":
                    # In chat mode, just finalize the renderer to preserve content
                    # but don't complete the display (which would prevent further messages)
                    if hasattr(self.display, "mode") and self.display.mode == "chat":
                        # Call renderer's finalize directly to preserve content
                        if hasattr(self.display, "_renderer") and hasattr(self.display._renderer, "finalize"):
                            self.display._renderer.finalize()
                    else:
                        # Non-chat mode: complete the display normally
                        self.display.complete()
                    return event_dict

                elif event_type == "error":
                    error_msg = event_dict.get("message", "Unknown error")
                    self.display.show_error(error_msg)
                    return None

                elif "output" in event_dict:
                    # Snapshot update - primary rendering path
                    self.state.update_from_snapshot(event_dict)
                    await self._render_current_state(question, event_type)

                elif event_type == "final_response":
                    # Handle final_response event - contains the complete response
                    if "output" in event_dict:
                        self.state.update_from_snapshot(event_dict)
                        await self._render_current_state(question, event_type)

                elif self._is_tool_event(event_type):
                    # Handle tool-specific events
                    await self._handle_tool_event(event_type, event_dict)

                # Track timing for search events
                if "file_search_call.searching" in event_type and self.search_start_time is None:
                    self.search_start_time = time.time()
                elif "file_search_call.completed" in event_type:
                    self.search_completed_time = time.time()

            return None

        except Exception as e:
            self.display.show_error(f"Stream handling error: {str(e)}")
            if self.debug:
                import traceback

                traceback.print_exc()
            return None

    async def _render_current_state(self, question: str, event_type: str) -> None:
        """Render current state based on output items."""
        formatted_content = self._format_output_items()

        metadata = {
            "question": question,
            "event_type": event_type,
            "usage": self.state.usage,
            "event_count": self.state.response_event_count,
        }

        # Convert to v3 display event format
        self.display.handle_event("text_delta", {"text": formatted_content, "metadata": metadata})

    def _format_output_items(self) -> str:
        """Format all output items in native order."""
        formatted_parts = []

        if self.debug:
            print(f"\nDEBUG: Formatting {len(self.state.output_items)} output items")

        for item in self.state.output_items:
            formatted = self.processor_registry.format_item(item)
            if formatted:
                formatted_parts.append(formatted)
                if self.debug:
                    print(f"DEBUG: Formatted {item.get('type', 'unknown')} item with {len(formatted)} chars")

        result = "\n\n".join(formatted_parts)
        if self.debug:
            print(f"DEBUG: Total formatted content: {len(result)} chars")

        return result

    def _is_tool_event(self, event_type: str) -> bool:
        """Check if event is a tool-related event."""
        tool_patterns = ["_call.searching", "_call.in_progress", "_call.completed"]
        return any(pattern in event_type for pattern in tool_patterns)

    async def _handle_tool_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Handle tool-specific events."""
        # Extract tool type from event
        tool_type = event_type
        if "response." in tool_type:
            tool_type = tool_type.replace("response.", "")
        if "_call." in tool_type:
            tool_type = tool_type.split("_call.")[0]

        # Update tool state
        tool_state = self.state.get_tool_state(tool_type)

        if ".searching" in event_type or ".in_progress" in event_type:
            tool_state.status = "searching"

            # Extract queries if present and event_data is valid
            if isinstance(event_data, dict):
                queries = self._extract_queries(event_data)
                if queries:
                    tool_state.queries = queries
                    tool_state.query = ", ".join(queries)

            # Calculate timing
            if self.search_start_time:
                tool_state.query_time = (time.time() - self.start_time) * 1000

        elif ".completed" in event_type:
            tool_state.status = "completed"

            # Extract results count if event_data is valid
            if isinstance(event_data, dict):
                results = event_data.get("results")
                if results is not None:
                    tool_state.results_count = len(results) if isinstance(results, list) else 0

            # Calculate timing
            if self.search_start_time and self.search_completed_time:
                tool_state.retrieval_time = (self.search_completed_time - self.search_start_time) * 1000

    def _extract_queries(self, event_data: dict[str, Any]) -> list[str]:
        """Extract queries from various event data structures."""
        if not isinstance(event_data, dict):
            return []

        # Direct location
        if "queries" in event_data:
            return event_data.get("queries", [])

        # Nested in tool call
        for key, value in event_data.items():
            if "_call" in key and isinstance(value, dict) and "queries" in value:
                return value.get("queries", [])

        return []

    async def _log_debug_info(
        self,
        event_type: str,
        event_data: dict[str, Any],
    ) -> None:
        """Log debug information for events."""
        print(f"\nDEBUG: Event: {event_type}")

        if isinstance(event_data, dict):
            # Special handling for output events
            if "output" in event_data and isinstance(event_data["output"], list):
                print(f"DEBUG: Event contains {len(event_data['output'])} output items")
                for idx, item in enumerate(event_data["output"]):
                    if isinstance(item, dict):
                        item_type = item.get("type", "unknown")
                        print(f"DEBUG:   [{idx}] {item_type}")

            # Log other event data
            else:
                import json

                print(f"DEBUG: {json.dumps(event_data, indent=2, ensure_ascii=False)[:500]}...")
