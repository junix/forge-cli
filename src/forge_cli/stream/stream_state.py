"""Stream state management for stream handling."""

from dataclasses import dataclass, field

from ..response._types import Response


@dataclass
class StreamState:
    """Lightweight streaming state container - most data comes from response object."""

    # Event counters (needed for streaming metrics)
    event_count: int = 0

    # Vector store IDs used in this session (from configuration, not in response)
    vector_store_ids: set[str] = field(default_factory=set)

    # Last completed Response object - the source of truth for all response data
    response: Response | None = None

    def initialize_vector_store_ids(self, vector_store_ids: list[str]) -> None:
        """Initialize vector store IDs from user configuration.

        Args:
            vector_store_ids: List of vector store IDs from user configuration
        """
        if vector_store_ids:
            self.vector_store_ids.update(vector_store_ids)

    def get_vector_store_ids(self) -> list[str]:
        """Get the list of vector store IDs used in this session.

        Returns:
            Sorted list of unique vector store IDs
        """
        return sorted(self.vector_store_ids)


__all__ = [
    "StreamState",
]
