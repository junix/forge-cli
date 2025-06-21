"""List documents tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS, pack_queries


class PlaintextListDocumentsToolRender(PlaintextToolRenderBase):
    """Plaintext list documents tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("list_documents_call", "📋"), "List Documents"
    
    def get_tool_details(self) -> str:
        """Get list documents specific details.
        
        Returns:
            Formatted details string showing queries
        """
        if not self._tool_item:
            return ""
        
        parts = []
        if self._tool_item.queries:
            # Show all queries using pack_queries for consistent display
            shortened_queries = [q[:25] + "..." if len(q) > 25 else q for q in self._tool_item.queries]
            packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
            parts.append(packed)
        
        return f"{ICONS['bullet']} ".join(parts) if parts else ""
    
    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextListDocumentsToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: List documents tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            List documents tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 