"""Adapters for backward compatibility between v1 and v2 display systems."""

import asyncio
import time
from typing import Any, Dict, Optional

from ..v1.base import BaseDisplay  # v1 interface
from .base import Display, Renderer  # v2 interfaces
from .events import EventType


class V1ToV2Adapter(BaseDisplay):
    """Adapter to make v2 Display work with v1 interface.

    This allows new v2 display implementations to be used with existing
    code that expects the v1 BaseDisplay interface.
    """

    def __init__(self, display_v2: Display):
        """Initialize adapter with a v2 display.

        Args:
            display_v2: The v2 Display instance to adapt
        """
        self._display = display_v2
        self._start_time = time.time()

    async def show_request_info(self, info: Dict[str, Any]) -> None:
        """Convert v1 request info to v2 stream start event."""
        # Use the display's show_request_info method if available
        if hasattr(self._display, 'show_request_info'):
            self._display.show_request_info(info)
        else:
            self._display.handle_event(
                EventType.STREAM_START.value,
                {
                    "query": info.get("question", ""),
                    "model": info.get("model", ""),
                    "effort": info.get("effort", ""),
                    "temperature": info.get("temperature", 0.7),
                    "timestamp": time.time(),
                },
            )

    async def update_content(self, content: str, metadata: Dict[str, Any] | None = None) -> None:
        """Convert v1 content update to v2 text delta event."""
        event_data = {"text": content}
        if metadata:
            event_data["metadata"] = metadata

        self._display.handle_event(EventType.TEXT_DELTA.value, event_data)

    async def show_status(self, status: str) -> None:
        """Convert v1 status to appropriate v2 event.

        This method attempts to intelligently map status messages to
        appropriate v2 events based on the status content.
        """
        # Use the display's show_status method if available
        if hasattr(self._display, 'show_status'):
            self._display.show_status(status)
        else:
            status_lower = status.lower()

            # Try to detect tool-related statuses
            if "search" in status_lower and "file" in status_lower:
                self._display.handle_event(
                    EventType.TOOL_START.value,
                    {"tool_type": "file_search", "tool_id": f"status_tool_{time.time()}", "status": status},
                )
            elif "search" in status_lower and "web" in status_lower:
                self._display.handle_event(
                    EventType.TOOL_START.value,
                    {"tool_type": "web_search", "tool_id": f"status_tool_{time.time()}", "status": status},
                )
            elif "thinking" in status_lower or "reasoning" in status_lower:
                self._display.handle_event(EventType.REASONING_START.value, {"status": status})
            else:
                # Default: treat as text content with newlines
                self._display.handle_event(EventType.TEXT_DELTA.value, {"text": f"\n{status}\n"})

    async def show_status_rich(self, rich_content: Any) -> None:
        """Show rich content like tables - v1 compatibility."""
        # Use the display's show_status_rich method if available
        if hasattr(self._display, 'show_status_rich'):
            self._display.show_status_rich(rich_content)
        else:
            # Fallback: convert to text if possible
            self._display.handle_event(EventType.TEXT_DELTA.value, {"text": str(rich_content)})

    async def show_error(self, error: str) -> None:
        """Convert v1 error to v2 error event."""
        # Use the display's show_error method if available
        if hasattr(self._display, 'show_error'):
            self._display.show_error(error)
        else:
            self._display.handle_event(EventType.STREAM_ERROR.value, {"error": error, "timestamp": time.time()})

    async def finalize(self, response: Dict[str, Any], state: Any) -> None:
        """Complete the v2 display with final response data."""
        # Send stream end event with response metadata
        self._display.handle_event(
            EventType.STREAM_END.value,
            {
                "duration": time.time() - self._start_time,
                "response_id": response.get("id", ""),
                "usage": response.get("usage", {}),
            },
        )

        # If renderer has render_finalize, call it before completing
        renderer = getattr(self._display, '_renderer', None)
        if renderer and hasattr(renderer, 'render_finalize'):
            renderer.render_finalize(response, state)
        else:
            # Complete the display normally
            self._display.complete()

    # Chat-specific methods with default implementations
    async def show_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode."""
        # Use the display's show_welcome method if available
        if hasattr(self._display, 'show_welcome'):
            self._display.show_welcome(config)
        else:
            self._display.handle_event(
                EventType.STREAM_START.value,
                {"query": "Welcome to Knowledge Forge Chat!", "type": "welcome", "timestamp": time.time()},
            )

    async def show_user_message(self, message: str) -> None:
        """Show a user message in chat mode."""
        # In v2, user messages should be handled by the chat controller
        # This is here for compatibility only
        self._display.handle_event(EventType.TEXT_DELTA.value, {"text": f"\nYou: {message}\n", "type": "user_message"})

    async def show_assistant_message(self, message: str) -> None:
        """Show an assistant message in chat mode."""
        self._display.handle_event(
            EventType.TEXT_DELTA.value, {"text": f"\nAssistant: {message}\n", "type": "assistant_message"}
        )

    async def prompt_for_input(self) -> str | None:
        """Input handling removed - raises error to force migration."""
        raise NotImplementedError(
            "Input handling has been removed from display classes. Please use InputHandler for user input collection."
        )


class V2ToV1Adapter(Renderer):
    """Adapter to make v1 Display work as a v2 Renderer.

    This allows existing v1 display implementations to be used in the
    new v2 system during migration.
    """

    def __init__(self, display_v1: BaseDisplay):
        """Initialize adapter with a v1 display.

        Args:
            display_v1: The v1 BaseDisplay instance to adapt
        """
        self._display = display_v1
        self._loop = asyncio.get_event_loop()
        self._response_data = {}
        self._state_data = {}

    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Convert v2 events to v1 method calls."""
        # Convert to EventType enum if possible
        event_enum = EventType.from_string(event_type)

        if event_enum:
            match event_enum:
                case EventType.STREAM_START:
                    self._run_async(
                        self._display.show_request_info(
                            {
                                "question": data.get("query", ""),
                                "model": data.get("model", ""),
                                "effort": data.get("effort", ""),
                                "temperature": data.get("temperature", 0.7),
                            }
                        )
                    )
                case EventType.TEXT_DELTA:
                    text = data.get("text", "")
                    metadata = data.get("metadata")
                    self._run_async(self._display.update_content(text, metadata))
                case EventType.STREAM_ERROR:
                    error = data.get("error", "Unknown error")
                    self._run_async(self._display.show_error(error))
                case EventType.STREAM_END:
                    # Store data for finalize
                    self._response_data.update(data)
                case EventType.TOOL_START | EventType.REASONING_START:
                    # Convert to status message
                    tool_type = data.get("tool_type", "")
                    if tool_type:
                        status = f"Starting {tool_type}..."
                    else:
                        status = "Processing..."
                    self._run_async(self._display.show_status(status))
                case _:
                    # Other events don't have direct v1 equivalents
                    pass

    def finalize(self) -> None:
        """Finalize the v1 display."""
        self._run_async(self._display.finalize(self._response_data, self._state_data))

    def _run_async(self, coro):
        """Run async coroutine in the event loop."""
        try:
            # If there's a running loop, create a task
            if self._loop.is_running():
                task = asyncio.create_task(coro)
                # Add error handling to the task
                task.add_done_callback(self._handle_task_exception)
            else:
                # If no loop is running, run until complete
                self._loop.run_until_complete(coro)
        except Exception as e:
            # Log error but don't crash
            print(f"Error in V2ToV1Adapter: {e}")

    def _handle_task_exception(self, task):
        """Handle exceptions from async tasks."""
        try:
            task.result()
        except Exception as e:
            print(f"Error in async task: {e}")
