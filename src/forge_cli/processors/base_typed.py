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

        This method now supports both dict and typed items.

        Args:
            item: Raw output item (dict) or typed item from Response
            state: StreamState instance
            display: Display instance
        """
        pass

    def extract_item_type(self, item: Any) -> str:
        """
        Extract item type from either dict or typed item.

        Args:
            item: Dict with 'type' key or typed object with type attribute

        Returns:
            The item type string
        """
        if hasattr(item, "type"):
            return str(item.type)
        elif isinstance(item, dict):
            return item.get("type", "")
        return ""

    def is_typed_item(self, item: Any) -> bool:
        """Check if item is a typed object (not dict)."""
        return hasattr(item, "type") and not isinstance(item, dict)


class TypedToolProcessor(TypedOutputProcessor):
    """Base class for tool processors with typed API support."""

    @abstractmethod
    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        pass

    def extract_queries(self, item: Any) -> list[str]:
        """Extract queries from either dict or typed tool call."""
        if hasattr(item, "queries") and item.queries:
            return list(item.queries)
        elif isinstance(item, dict):
            return item.get("queries", [])
        return []

    def extract_results(self, item: Any) -> list[Any]:
        """Extract results from either dict or typed tool call."""
        if hasattr(item, "results") and item.results:
            return list(item.results)
        elif isinstance(item, dict):
            return item.get("results", [])
        return []

    def extract_status(self, item: Any) -> str:
        """Extract status from either dict or typed tool call."""
        if hasattr(item, "status"):
            return str(item.status)
        elif isinstance(item, dict):
            return item.get("status", "unknown")
        return "unknown"


class ProcessorAdapter:
    """Adapter to make old processors work with typed items."""

    def __init__(self, legacy_processor: Any):
        """Wrap a legacy processor."""
        self.legacy_processor = legacy_processor

    def can_process(self, item_type: str) -> bool:
        """Delegate to legacy processor."""
        return self.legacy_processor.can_process(item_type)

    def process(self, item: Any, state: Any, display: Any) -> None:
        """Convert typed item to dict if needed, then process."""
        if hasattr(item, "model_dump"):
            # Convert typed item to dict
            dict_item = item.model_dump()
            self.legacy_processor.process(dict_item, state, display)
        else:
            # Already a dict
            self.legacy_processor.process(item, state, display)
