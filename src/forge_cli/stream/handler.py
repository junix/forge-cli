"""Main stream handler implementation."""

from collections.abc import AsyncIterator

from ..display.v3.base import Display
from ..response._types import Response
from .stream_state import StreamState


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
        initial_request: str,
        vector_store_ids: list[str] | None = None,
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

        # Process events
        async for event_type, event_data in stream:
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
                # Store the Response snapshot directly
                state.response = event_data
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

        return state

    # Note: Most processing logic has been moved to v3 renderers
    # The TypedStreamHandler now focuses purely on routing Response objects to displays


__all__ = [
    "TypedStreamHandler",
]
