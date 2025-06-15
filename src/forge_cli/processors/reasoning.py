"""Processor for reasoning output items."""

from typing import Any

from ..response._types import ResponseReasoningItem
from .base import OutputProcessor


class ReasoningProcessor(OutputProcessor):
    """Processes reasoning output items containing thinking/analysis."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "reasoning"

    def process(self, item: Any) -> dict[str, Any] | None:
        """Extract reasoning text from summary items."""
        reasoning_texts = []

        # Handle typed ResponseReasoningItem only
        if isinstance(item, ResponseReasoningItem):
            # Extract from typed object
            for summary in item.summary or []:
                if hasattr(summary, "type") and summary.type in ["summary_text", "text"]:
                    text = getattr(summary, "text", "")
                    if text:
                        reasoning_texts.append(text)

            return {
                "type": "reasoning",
                "content": "\n\n".join(reasoning_texts),
                "status": item.status or "completed",
                "id": item.id or "",
            }

        return None

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
