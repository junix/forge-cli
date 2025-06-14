"""File search tool call processor."""


from .base import BaseToolCallProcessor


class FileSearchProcessor(BaseToolCallProcessor):
    """Processes file search tool calls."""

    TOOL_TYPE = "file_search"
    TOOL_CONFIG = {
        "emoji": "📄",
        "action": "搜索文档",
        "status_searching": "正在搜索文档...",
        "status_completed": "搜索已完成",
        "results_text": "个相关内容块",
    }

    def _add_tool_specific_data(
        self,
        item: dict[str, str | int | float | bool | list | dict],
        processed: dict[str, str | int | float | bool | list | dict],
    ) -> None:
        """Add file search specific data."""
        # Add file_id if searching specific file
        file_id = item.get("file_id")
        if file_id:
            processed["file_id"] = file_id

    def _add_tool_specific_formatting(
        self, processed: dict[str, str | int | float | bool | list | dict], parts: list[str]
    ) -> None:
        """Add file search specific formatting."""
        # Add file ID if searching specific file
        file_id = processed.get("file_id")
        if file_id:
            parts.append(f"📁 文件: {file_id}")
