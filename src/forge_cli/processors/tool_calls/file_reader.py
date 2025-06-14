"""File reader tool call processor."""

import re
from typing import Dict, Union, List
from .base import BaseToolCallProcessor


class FileReaderProcessor(BaseToolCallProcessor):
    """Processes file reader tool calls."""

    TOOL_TYPE = "file_reader"
    TOOL_CONFIG = {
        "emoji": "📖",
        "action": "精读文档",
        "status_searching": "正在精读文档...",
        "status_completed": "精读已完成",
        "results_text": "个内容块",
    }

    def _add_tool_specific_data(self, item: Dict[str, Any], processed: Dict[str, Any]) -> None:
        """Add file reader specific data."""
        # Add query and doc_ids
        query = item.get("query")
        if query:
            processed["query"] = query

        doc_ids = item.get("doc_ids", [])
        if doc_ids:
            processed["doc_ids"] = doc_ids

        # Add execution trace and progress
        execution_trace = item.get("execution_trace")
        if execution_trace:
            processed["execution_trace"] = execution_trace

        progress = item.get("progress")
        if progress is not None:
            processed["progress"] = progress

    def format(self, processed: Dict[str, Any]) -> str:
        """Custom formatting for file reader."""
        parts = []

        # Header with query or doc count
        query = processed.get("query", "")
        doc_ids = processed.get("doc_ids", [])

        if query:
            parts.append(f"{self.TOOL_CONFIG['emoji']} {self.TOOL_CONFIG['action']}: {query}")
        elif doc_ids:
            doc_count = len(doc_ids)
            parts.append(f"{self.TOOL_CONFIG['emoji']} {self.TOOL_CONFIG['action']}: {doc_count} 个文档")

        # Status and progress
        status = processed.get("status", "")
        progress = processed.get("progress", 0.0)

        if status == "completed":
            parts.append(f"\n\n✅ {self.TOOL_CONFIG['status_completed']}")

            # Extract chunk count from execution trace
            execution_trace = processed.get("execution_trace", "")
            if execution_trace and "chunks" in execution_trace:
                chunk_match = re.search(r"(\d+) chunks", execution_trace)
                if chunk_match:
                    chunk_count = chunk_match.group(1)
                    parts.append(f"  📄 获得 {chunk_count} 个内容块")

        elif status in ["searching", "in_progress"]:
            if progress and progress > 0:
                parts.append(f"\n\n⏳ {self.TOOL_CONFIG['status_searching']} ({progress * 100:.0f}%)")
            else:
                parts.append(f"\n\n⏳ {self.TOOL_CONFIG['status_searching']}")

        return "\n".join(parts)
