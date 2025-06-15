"""Base processor with typed API support."""

from abc import ABC, abstractmethod
from typing import Any

from forge_cli.display.v3.base import Display
from forge_cli.models.state import StreamState
from forge_cli.response._types import (
    ResponseDocumentFinderToolCall,
    ResponseFileSearchToolCall,
    ResponseFunctionWebSearch,
    ResponseOutputItem,
)
from forge_cli.response._types.response_output_item import ResponseOutputItem


class TypedOutputProcessor(ABC):
    """Abstract base class for processing output items with typed API support."""

    @abstractmethod
    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the given item type."""
        pass

    @abstractmethod
    def process(self, item: ResponseOutputItem, state: StreamState, display: Display) -> None:
        """
        Process the output item and update display.

        This method now supports typed items only.

        Args:
            item: Typed item from Response
            state: StreamState instance
            display: Display instance
        """
        pass

    def extract_item_type(self, item: ResponseOutputItem) -> str:
        """
        Extract item type from typed item.

        Args:
            item: Typed ResponseOutputItem

        Returns:
            The item type string
        """
        return str(item.type)


class TypedToolProcessor(TypedOutputProcessor):
    """Base class for tool processors with typed API support."""

    @abstractmethod
    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        pass

    def extract_queries(
        self, item: ResponseFileSearchToolCall | ResponseDocumentFinderToolCall | ResponseFunctionWebSearch
    ) -> list[str]:
        """Extract queries from typed tool call."""
        return list(item.queries) if item.queries else []

    def extract_results(
        self, item: ResponseFileSearchToolCall | ResponseDocumentFinderToolCall | ResponseFunctionWebSearch
    ) -> list[Any]:
        """Extract results from typed tool call."""
        # Access 'results' safely as it might be dynamically added
        results_attr = getattr(item, "results", None)
        return list(results_attr) if results_attr else []

    def extract_status(
        self, item: ResponseFileSearchToolCall | ResponseDocumentFinderToolCall | ResponseFunctionWebSearch
    ) -> str:
        """Extract status from typed tool call."""
        return str(item.status)
