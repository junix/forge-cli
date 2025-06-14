"""Base processor protocol for output items."""

from abc import ABC, abstractmethod
from typing import Any


class OutputProcessor(ABC):
    """Abstract base class for processing output items."""

    @abstractmethod
    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the given item type."""
        pass

    @abstractmethod
    def process(self, item: Any) -> dict[str, Any] | None:
        """
        Process the output item and return processed data.

        Args:
            item: Raw output item from the API

        Returns:
            Processed data dictionary or None if processing fails
        """
        pass

    @abstractmethod
    def format(self, processed: dict[str, Any]) -> str:
        """
        Format processed item for display.

        Args:
            processed: Processed data from the process method

        Returns:
            Formatted string for display
        """
        pass
