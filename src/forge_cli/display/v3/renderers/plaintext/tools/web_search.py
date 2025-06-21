"""Web search tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS, pack_queries


class PlaintextWebSearchToolRender(PlaintextToolRenderBase):
    """Plaintext web search tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("web_search_call", "🌐"), "Web Search"
    
    def get_tool_details(self) -> str:
        """Get web search specific details.
        
        Returns:
            Formatted details string showing queries and results
        """
        if not self._tool_item:
            return ""
        
        parts = []
        
        # Add queries using pack_queries for consistent display
        if hasattr(self._tool_item, 'queries') and self._tool_item.queries:
            shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in self._tool_item.queries]
            packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
            parts.append(packed)
        elif hasattr(self._tool_item, 'query') and self._tool_item.query:
            # Handle single query case
            query = self._tool_item.query
            if len(query) > 30:
                query = query[:27] + "..."
            packed = pack_queries(f'"{query}"')
            parts.append(packed)
        
        # Add result count if available
        if hasattr(self._tool_item, 'result_count') and self._tool_item.result_count is not None:
            result_word = "result" if self._tool_item.result_count == 1 else "results"
            parts.append(f"{ICONS['search_results']}{self._tool_item.result_count} {result_word}")
        
        # Add progress if available
        if hasattr(self._tool_item, 'progress') and self._tool_item.progress is not None:
            progress_percent = int(self._tool_item.progress * 100)
            parts.append(f"{ICONS['processing']}{progress_percent}%")
        
        return f" {ICONS['bullet']} ".join(parts) if parts else ""

    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextWebSearchToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: Web search tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Web search tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 