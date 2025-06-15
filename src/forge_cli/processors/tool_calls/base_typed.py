"""Base class for tool call processors with typed API support."""

from typing import Any

from ..base_typed import TypedToolProcessor


class BaseToolCallProcessor(TypedToolProcessor):
    """Base processor for tool call output items with typed API support."""

    # Override these in subclasses
    TOOL_TYPE: str = ""
    TOOL_CONFIG: dict[str, str] = {
        "emoji": "🔧",
        "action": "执行工具",
        "status_searching": "正在执行...",
        "status_completed": "执行已完成",
        "results_text": "个结果",
    }

    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        return self.TOOL_TYPE

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == f"{self.TOOL_TYPE}_call"

    def process(self, item: Any, state: Any, display: Any) -> None:
        """Process tool call output item (dict or typed)."""
        # Extract common data
        tool_id = self._extract_id(item)
        queries = self.extract_queries(item)
        status = self.extract_status(item)
        results = self.extract_results(item)

        # Create processed data
        processed = {
            "type": self.TOOL_TYPE,
            "tool_type": self.TOOL_TYPE,
            "queries": queries,
            "status": status,
            "id": tool_id,
            "results_count": len(results) if results else 0,
            "results": results,
        }

        # Add tool-specific data
        self._add_tool_specific_data(item, processed)

        # Update state and display
        if hasattr(state, "add_tool_state"):
            state.add_tool_state(tool_id, processed)

        # Format and display
        formatted = self.format(processed)
        if formatted and display:
            display.update_content(formatted, {"type": "tool_call", "tool_type": self.TOOL_TYPE})

    def _extract_id(self, item: Any) -> str:
        """Extract ID from either dict or typed item."""
        if hasattr(item, "id"):
            return str(item.id)
        elif isinstance(item, dict):
            return item.get("id", "")
        return ""

    def _add_tool_specific_data(
        self,
        item: Any,
        processed: dict[str, Any],
    ) -> None:
        """Override in subclasses to add tool-specific data."""
        pass

    def format(self, processed: dict[str, Any]) -> str:
        """Format processed item for display."""
        parts = []

        # Add header with queries
        queries = processed.get("queries", [])
        if queries:
            parts.append(f"{self.TOOL_CONFIG['emoji']} {self.TOOL_CONFIG['action']}:")
            for query in queries:
                parts.append(f"- {query}")

        # Add any tool-specific formatting
        self._add_tool_specific_formatting(processed, parts)

        # Add status
        status = processed.get("status", "")
        if status == "completed":
            parts.append(f"\n✅ {self.TOOL_CONFIG['status_completed']}")
            if "results_count" in processed:
                count = processed["results_count"]
                parts.append(f"找到 {count} {self.TOOL_CONFIG['results_text']}")
        elif status in ["searching", "in_progress"]:
            parts.append(f"\n⏳ {self.TOOL_CONFIG['status_searching']}")

        return "\n".join(parts)

    def _add_tool_specific_formatting(self, processed: dict[str, Any], parts: list[str]) -> None:
        """Override in subclasses to add tool-specific formatting."""
        pass
