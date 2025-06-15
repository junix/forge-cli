"""File reader tool call processor with typed API support."""

from typing import Any, List
from forge_cli.common.types import ProcessedToolCallData
from forge_cli.response._types import ResponseFunctionFileReader
from .base_typed import BaseToolCallProcessor


class FileReaderProcessor(BaseToolCallProcessor):
    """Processes file reader tool calls with typed API support."""

    TOOL_TYPE = "file_reader"
    TOOL_CONFIG = {
        "emoji": "📖",
        "action": "读取文件",
        "status_reading": "正在读取文件...",
        "status_searching": "正在搜索内容...",
        "status_completed": "读取已完成",
        "results_text": "个内容块",
    }

    def _add_tool_specific_data(
        self,
        item: ResponseFunctionFileReader,
        processed: ProcessedToolCallData,
    ) -> None:
        """Add file reader specific data."""
        # Add document IDs
        if hasattr(item, "doc_ids") and item.doc_ids:
            processed["doc_ids"] = list(item.doc_ids)
        
        # Add query if available
        if hasattr(item, "query") and item.query:
            processed["query"] = item.query
        
        # Add navigation info if available
        if hasattr(item, "navigation") and item.navigation:
            processed["navigation"] = item.navigation

    def _add_tool_specific_formatting(
        self, 
        processed: ProcessedToolCallData, 
        parts: list[str]
    ) -> None:
        """Add file reader specific formatting."""
        # Add document IDs
        doc_ids = processed.get("doc_ids", [])
        if doc_ids:
            if len(doc_ids) == 1:
                parts.append(f"📄 文档ID: {doc_ids[0]}")
            else:
                parts.append(f"📄 文档ID ({len(doc_ids)}个):")
                for doc_id in doc_ids[:3]:  # Show first 3
                    parts.append(f"  • {doc_id}")
                if len(doc_ids) > 3:
                    parts.append(f"  • ... 还有 {len(doc_ids) - 3} 个")
        
        # Add query if available
        query = processed.get("query")
        if query:
            parts.append(f"❓ 查询: {query}")
        
        # Add navigation info if available  
        navigation = processed.get("navigation")
        if navigation:
            parts.append(f"🧭 导航: {navigation}")

    def extract_results(self, item: ResponseFunctionFileReader) -> List[Any]:
        """Extract results from file reader tool call."""
        # Check if item has _results attribute (private attribute pattern)
        if hasattr(item, "_results") and item._results:
            return list(item._results)
        # Check for public results attribute
        elif hasattr(item, "results") and item.results:
            return list(item.results)
        return []

    def extract_file_mappings(self, item: ResponseFunctionFileReader) -> dict[str, str]:
        """Extract file ID to filename mappings from results."""
        mappings = {}
        
        # File reader typically deals with document IDs rather than file IDs
        # But we can still extract any file references from results
        results = self.extract_results(item)
        for result in results:
            if isinstance(result, dict):
                file_id = result.get("file_id") or result.get("doc_id")
                filename = result.get("filename") or result.get("doc_name")
                if file_id and filename:
                    mappings[file_id] = filename
        
        return mappings