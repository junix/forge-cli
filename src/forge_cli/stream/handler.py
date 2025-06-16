"""Main stream handler implementation."""

from collections.abc import AsyncIterator

from ..display.v3.base import Display
from ..response._types import Response


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
    ) -> Response | None:
        """
        Handle streaming events from typed API.

        Args:
            stream: Iterator yielding (event_type, Response) tuples

        Returns:
            Final Response object after processing all events, or None if no response
        """
        final_response: Response | None = None

        # Process events
        async for event_type, event_data in stream:
            if self.debug:
                # Simple debug logging - detailed JSON output is handled by JsonRenderer
                if event_data is not None and isinstance(event_data, Response):
                    print(f"[DEBUG] {event_type}: Response snapshot (id: {event_data.id})")
                else:
                    print(f"[DEBUG] {event_type}: {type(event_data)}")

            # Handle snapshot events (events with Response objects)
            if event_data is not None and isinstance(event_data, Response):
                # Store the Response snapshot directly
                final_response = event_data
                # Render the complete Response snapshot using v3 display
                self.display.handle_response(event_data)

            # Handle lifecycle events
            elif event_type == "done":
                # Stream completed
                # In chat mode, don't finalize the display as it will be reused
                if getattr(self.display, '_mode', 'default') != 'chat':
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

        return final_response

    # Note: Most processing logic has been moved to v3 renderers
    # The TypedStreamHandler now focuses purely on routing Response objects to displays


__all__ = [
    "TypedStreamHandler",
]
