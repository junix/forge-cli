"""Stream state management for stream handling."""

from dataclasses import dataclass

from ..response._types import Response


@dataclass
class StreamState:
    """Lightweight streaming state container - most data comes from response object."""

    # Last completed Response object - the source of truth for all response data
    response: Response | None = None


__all__ = [
    "StreamState",
]
