"""File search tool call processor with typed API support."""

from typing import Any
from .base_typed import BaseToolCallProcessor


class FileSearchProcessor(BaseToolCallProcessor):
    """Processes file search tool calls with typed API support."""

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
        item: Any,
        processed: dict[str, Any],
    ) -> None:
        """Add file search specific data."""
        # Extract file_id if searching specific file
        if hasattr(item, "file_id"):
            processed["file_id"] = str(item.file_id)
        elif isinstance(item, dict):
            file_id = item.get("file_id")
            if file_id:
                processed["file_id"] = file_id

        # Extract vector store IDs if available
        if hasattr(item, "vector_store_ids"):
            processed["vector_store_ids"] = list(item.vector_store_ids)
        elif isinstance(item, dict) and "vector_store_ids" in item:
            processed["vector_store_ids"] = item["vector_store_ids"]

    def _add_tool_specific_formatting(self, processed: dict[str, Any], parts: list[str]) -> None:
        """Add file search specific formatting."""
        # Add file ID if searching specific file
        file_id = processed.get("file_id")
        if file_id:
            parts.append(f"📁 文件: {file_id}")

        # Add vector store IDs if available
        vector_store_ids = processed.get("vector_store_ids", [])
        if vector_store_ids:
            parts.append(f"🗄️ 向量存储: {', '.join(vector_store_ids)}")

    def extract_file_mappings(self, item: Any) -> dict[str, str]:
        """Extract file ID to filename mappings from results."""
        mappings = {}

        results = self.extract_results(item)
        for result in results:
            if hasattr(result, "file_id") and hasattr(result, "filename"):
                mappings[result.file_id] = result.filename
            elif isinstance(result, dict):
                file_id = result.get("file_id")
                filename = result.get("filename")
                if file_id and filename:
                    mappings[file_id] = filename

        return mappings
