"""Processor for reasoning output items."""

from typing import Dict, Union, List, Optional
from .base import OutputProcessor


class ReasoningProcessor(OutputProcessor):
    """Processes reasoning output items containing thinking/analysis."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "reasoning"

    def process(self, item: Dict[str, Union[str, int, float, bool, List, Dict]]) -> Optional[Dict[str, Union[str, int, float, bool, List, Dict]]]:
        """Extract reasoning text from summary items."""
        reasoning_texts = []

        for summary in item.get("summary", []):
            # Handle both "summary_text" and "text" types
            if summary.get("type") in ["summary_text", "text"]:
                text = summary.get("text", "")
                if text:
                    reasoning_texts.append(text)

        return {
            "type": "reasoning",
            "content": "\n\n".join(reasoning_texts),
            "status": item.get("status", "completed"),
            "id": item.get("id", ""),
        }

    def format(self, processed: Dict[str, Union[str, int, float, bool, List, Dict]]) -> str:
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
