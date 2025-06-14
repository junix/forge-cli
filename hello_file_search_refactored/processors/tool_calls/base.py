"""Base class for tool call processors."""

from typing import Dict, Any, Optional, Tuple
from ..base import OutputProcessor


class BaseToolCallProcessor(OutputProcessor):
    """Base processor for tool call output items."""
    
    # Override these in subclasses
    TOOL_TYPE: str = ""
    TOOL_CONFIG: Dict[str, str] = {
        "emoji": "🔧",
        "action": "执行工具",
        "status_searching": "正在执行...",
        "status_completed": "执行已完成",
        "results_text": "个结果"
    }
    
    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == f"{self.TOOL_TYPE}_call"
    
    def process(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process tool call output item."""
        processed = {
            "type": self.TOOL_TYPE,
            "tool_type": self.TOOL_TYPE,
            "queries": item.get("queries", []),
            "status": item.get("status", ""),
            "id": item.get("id", "")
        }
        
        # Extract results count if available
        results = item.get("results")
        if results is not None:
            processed["results_count"] = len(results) if isinstance(results, list) else 0
            processed["results"] = results
        
        # Add any tool-specific processing
        self._add_tool_specific_data(item, processed)
        
        return processed
    
    def _add_tool_specific_data(self, item: Dict[str, Any], processed: Dict[str, Any]) -> None:
        """Override in subclasses to add tool-specific data."""
        pass
    
    def format(self, processed: Dict[str, Any]) -> str:
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
    
    def _add_tool_specific_formatting(self, processed: Dict[str, Any], parts: list) -> None:
        """Override in subclasses to add tool-specific formatting."""
        pass