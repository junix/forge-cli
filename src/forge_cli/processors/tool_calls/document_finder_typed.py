"""Document finder tool call processor with typed API support."""

from typing import Any, cast, List
from forge_cli.common.types import ProcessedToolCallData
from forge_cli.response._types import ResponseDocumentFinderToolCall
from .base_typed import BaseToolCallProcessor


class DocumentFinderProcessor(BaseToolCallProcessor):
    """Processes document finder tool calls with typed API support."""

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
        item: ResponseDocumentFinderToolCall,
        processed: ProcessedToolCallData,
    ) -> None:
        """Add document finder specific data."""
        # Add count parameter
        if hasattr(item, "count") and item.count is not None:
            processed["count"] = item.count
        
        # Add queries if available
        if hasattr(item, "queries") and item.queries:
            processed["queries"] = list(item.queries)

    def _add_tool_specific_formatting(
        self, 
        processed: ProcessedToolCallData, 
        parts: list[str]
    ) -> None:
        """Add document finder specific formatting."""
        # Add count if specified
        count = processed.get("count")
        if count is not None:
            parts.append(f"🔢 返回数量: {count}")
        
        # Add queries if available
        queries = processed.get("queries", [])
        if queries:
            if len(queries) == 1:
                parts.append(f"🔍 查询: {queries[0]}")
            else:
                parts.append(f"🔍 查询 ({len(queries)}个):")
                for i, query in enumerate(queries, 1):
                    parts.append(f"  {i}. {query}")

    def extract_results(self, item: ResponseDocumentFinderToolCall) -> List[Any]:
        """Extract results from document finder tool call."""
        # Document finder doesn't have inline results like file search
        # Results would be in a separate event or through a results property
        if hasattr(item, "results"):
            return list(item.results)
        return []