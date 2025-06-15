"""File search tool call processor with typed API support."""

from typing import Any, Literal, TypedDict, cast

from forge_cli.response._types import ResponseFileSearchToolCall

from .base_typed import BaseToolCallProcessor


# Local type definitions for file search processor
class FileSearchResult(TypedDict, total=False):
    file_id: str
    filename: str
    citation_id: int | None


class ProcessedFileSearchData(TypedDict, total=False):
    type: Literal["file_search"]  # from BaseToolCallProcessor
    tool_name: str  # from BaseToolCallProcessor
    status: str  # from BaseToolCallProcessor
    action_text: str  # from BaseToolCallProcessor
    queries: list[str]  # from BaseToolCallProcessor
    results_count: int | None  # from BaseToolCallProcessor
    error_message: str | None  # from BaseToolCallProcessor
    file_id: str | None  # Specific to file search
    vector_store_ids: list[str] | None  # Specific to file search


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
        item: ResponseFileSearchToolCall,
        processed: ProcessedFileSearchData,
    ) -> None:
        """Add file search specific data."""
        # Extract file_id if searching specific file
        if item.file_id:
            processed["file_id"] = str(item.file_id)

        # Extract vector store IDs if available
        if item.vector_store_ids:
            processed["vector_store_ids"] = list(item.vector_store_ids)

    def _add_tool_specific_formatting(self, processed: ProcessedFileSearchData, parts: list[str]) -> None:
        """Add file search specific formatting."""
        # Add file ID if searching specific file
        file_id = processed.get("file_id")
        if file_id:
            parts.append(f"📁 文件: {file_id}")

        # Add vector store IDs if available
        vector_store_ids = processed.get("vector_store_ids", [])
        if vector_store_ids:
            parts.append(f"🗄️ 向量存储: {', '.join(vector_store_ids)}")

    def extract_file_mappings(self, item: ResponseFileSearchToolCall) -> dict[str, str]:
        """Extract file ID to filename mappings from results."""
        mappings = {}

        results: list[Any] = self.extract_results(item)
        for result_dict in results:
            if isinstance(result_dict, dict):  # Ensure it's a dictionary
                # Cast to FileSearchResult to inform the type checker of the expected structure
                result = cast(FileSearchResult, result_dict)
                file_id = result.get("file_id")
                filename = result.get("filename")
                if file_id and filename:
                    mappings[file_id] = filename
            # else: log or handle non-dict items if they can occur

        return mappings
