"""Document finder tool call processor."""

from .base import BaseToolCallProcessor


class DocumentFinderProcessor(BaseToolCallProcessor):
    """Processes document finder tool calls."""

    TOOL_TYPE = "document_finder"
    TOOL_CONFIG = {
        "emoji": "🔍",
        "action": "查找文档",
        "status_searching": "正在查找文档...",
        "status_completed": "查找已完成",
        "results_text": "个文档",
    }

    def _add_tool_specific_data(
        self,
        item: dict[str, str | int | float | bool | list | dict],
        processed: dict[str, str | int | float | bool | list | dict],
    ) -> None:
        """Add document finder specific data."""
        # Add count parameter
        count = item.get("count")
        if count is not None:
            processed["count"] = count
