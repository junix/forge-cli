"""Main stream handler for processing API responses."""

from typing import AsyncIterator, Tuple, Dict, Any, Optional
import time

from ..models.state import StreamState, ToolStatus
from ..models.events import EventType
from ..processors.registry import default_registry
from ..display.v2.base import Display


class StreamHandler:
    """Handles streaming responses with clean architecture."""

    def __init__(self, display: Display, debug: bool = False):
        self.display = display
        self.debug = debug
        self.state = StreamState()
        self.processor_registry = default_registry

        # Timing variables
        self.start_time = time.time()
        self.search_start_time: Optional[float] = None
        self.search_completed_time: Optional[float] = None

    async def handle_stream(
        self, event_stream: AsyncIterator[Tuple[str, Dict[str, Any]]], question: str
    ) -> Optional[Dict[str, Any]]:
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

                # Update usage if present
                if isinstance(event_data, dict) and "usage" in event_data:
                    self.state.usage.update(event_data["usage"])

                # Debug logging
                if self.debug:
                    await self._log_debug_info(event_type, event_data)

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
                    return event_data

                elif event_type == "error":
                    error_msg = (
                        event_data.get("message", "Unknown error") if isinstance(event_data, dict) else "Unknown error"
                    )
                    self.display.show_error(error_msg)
                    return None

                elif isinstance(event_data, dict) and "output" in event_data:
                    # Snapshot update - primary rendering path
                    self.state.update_from_snapshot(event_data)
                    await self._render_current_state(question, event_type)

                elif event_type == "final_response":
                    # Handle final_response event - contains the complete response
                    if isinstance(event_data, dict) and "output" in event_data:
                        self.state.update_from_snapshot(event_data)
                        await self._render_current_state(question, event_type)

                elif self._is_tool_event(event_type):
                    # Handle tool-specific events
                    await self._handle_tool_event(event_type, event_data)

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

        # Convert to v2 display event format
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

    async def _handle_tool_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
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
            tool_state.status = ToolStatus.SEARCHING

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
            tool_state.status = ToolStatus.COMPLETED

            # Extract results count if event_data is valid
            if isinstance(event_data, dict):
                results = event_data.get("results")
                if results is not None:
                    tool_state.results_count = len(results) if isinstance(results, list) else 0

            # Calculate timing
            if self.search_start_time and self.search_completed_time:
                tool_state.retrieval_time = (self.search_completed_time - self.search_start_time) * 1000

    def _extract_queries(self, event_data: Dict[str, Any]) -> list:
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

    async def _log_debug_info(self, event_type: str, event_data: Any) -> None:
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
