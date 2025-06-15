"""Base processor with typed API support."""

from abc import ABC, abstractmethod
from typing import Any, Union

from forge_cli.response._types import Response


class TypedOutputProcessor(ABC):
    """Abstract base class for processing output items with typed API support."""

    @abstractmethod
    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the given item type."""
        pass

    @abstractmethod
    def process(self, item: Any, state: Any, display: Any) -> None:
        """
        Process the output item and update display.

        This method now supports typed items only.

        Args:
            item: Typed item from Response
            state: StreamState instance
            display: Display instance
        """
        pass

    def extract_item_type(self, item: Any) -> str:
        """
        Extract item type from typed item.

        Args:
            item: Typed object with type attribute

        Returns:
            The item type string
        """
        if hasattr(item, "type"):
            return str(item.type)
        return ""



class TypedToolProcessor(TypedOutputProcessor):
    """Base class for tool processors with typed API support."""

    @abstractmethod
    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        pass

    def extract_queries(self, item: Any) -> list[str]:
        """Extract queries from typed tool call."""
        if hasattr(item, "queries") and item.queries:
            return list(item.queries)
        return []

    def extract_results(self, item: Any) -> list[Any]:
        """Extract results from typed tool call."""
        if hasattr(item, "results") and item.results:
            return list(item.results)
        return []

    def extract_status(self, item: Any) -> str:
        """Extract status from typed tool call."""
        if hasattr(item, "status"):
            return str(item.status)
        return "unknown"


