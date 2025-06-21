"""Function call tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS


class PlaintextFunctionCallToolRender(PlaintextToolRenderBase):
    """Plaintext function call tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("function_call", "⚙️"), "Function Call"
    
    def get_tool_details(self) -> str:
        """Get function call specific details.
        
        Returns:
            Formatted details string showing function name and arguments
        """
        if not self._tool_item:
            return ""
        
        parts = []
        
        # Add function name
        if hasattr(self._tool_item, 'name') and self._tool_item.name:
            parts.append(f"{ICONS['function_call']}{self._tool_item.name}")
        
        # Add call ID (shortened)
        if hasattr(self._tool_item, 'call_id') and self._tool_item.call_id:
            call_id_short = self._tool_item.call_id[:8] if len(self._tool_item.call_id) > 8 else self._tool_item.call_id
            parts.append(f"{ICONS['info']}{call_id_short}")
        
        # Add arguments preview if available
        if hasattr(self._tool_item, 'arguments') and self._tool_item.arguments:
            # Truncate long arguments for display
            args_str = str(self._tool_item.arguments)
            if len(args_str) > 50:
                args_str = args_str[:47] + "..."
            parts.append(f"{ICONS['processing']}{args_str}")
        
        return f" {ICONS['bullet']} ".join(parts) if parts else ""

    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextFunctionCallToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: Function call tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Function call tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 