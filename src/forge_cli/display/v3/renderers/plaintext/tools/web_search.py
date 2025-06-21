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
            Formatted details string showing queries
        """
        if not self._tool_item:
            return ""
        
        parts = []
        if self._tool_item.queries:
            # Use pack_queries for consistent display
            shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in self._tool_item.queries]
            packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
            parts.append(packed)
        
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