"""Processor for reasoning output items."""

from typing import Any

from ..response._types import ResponseReasoningItem
from .base import OutputProcessor


class ReasoningProcessor(OutputProcessor):
    """Processes reasoning output items containing thinking/analysis."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "reasoning"

    def process(self, item: ResponseReasoningItem) -> dict[str, Any] | None:
        """Extract reasoning text from summary items."""
        reasoning_texts = []

        # Extract text from summary items
        for summary in item.summary or []:
            # Safely access text attribute
            if hasattr(summary, "text") and summary.text:
                reasoning_texts.append(summary.text)

        return {
            "type": "reasoning",
            "content": "\n\n".join(reasoning_texts),
            "status": item.status or "completed",
            "id": item.id or "",
        }

    def format(self, processed: dict[str, Any]) -> str:
        """Format reasoning for display as quoted text."""
        content = processed.get("content", "")
        if not content:
            return ""

        # Format as markdown blockquote
        lines = content.split("\n")
        quoted_lines = []

        for line in lines:
            if line.strip():
                quoted_lines.append(f"> {line}")
            else:
                quoted_lines.append(">")

        return "\n".join(quoted_lines)
