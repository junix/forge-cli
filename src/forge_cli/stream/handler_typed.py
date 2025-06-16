"""Stream handler with typed API support."""

# Re-export from sub-modules for backward compatibility
from .handler import TypedStreamHandler

# StreamState is deprecated - use Response objects directly
# Kept for backward compatibility
from .stream_state import StreamState

__all__ = [
    "TypedStreamHandler",
    "StreamState",  # Deprecated - kept for backward compatibility
]
