"""Processor for reasoning output items."""

from typing import Dict, Any, Optional, Union

from .base import OutputProcessor
from ..response._types import ResponseStreamEvent, ResponseReasoningItem


class ReasoningProcessor(OutputProcessor):
    """Processes reasoning output items containing thinking/analysis."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "reasoning"

    def process(
        self, item: Union[Dict[str, Any], ResponseStreamEvent]
    ) -> Optional[Dict[str, Any]]:
        """Extract reasoning text from summary items."""
        reasoning_texts = []
        
        # Handle typed event
        if isinstance(item, ResponseReasoningItem):
            # Extract from typed object
            for summary in item.summary or []:
                if hasattr(summary, 'type') and summary.type in ["summary_text", "text"]:
                    text = getattr(summary, 'text', '')
                    if text:
                        reasoning_texts.append(text)
            
            return {
                "type": "reasoning",
                "content": "\n\n".join(reasoning_texts),
                "status": item.status or "completed",
                "id": item.id or "",
            }
        
        # Handle dict for backward compatibility
        elif isinstance(item, dict):
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
        
        return None

    def format(self, processed: Dict[str, Any]) -> str:
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
