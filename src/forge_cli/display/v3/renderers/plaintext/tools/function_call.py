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
        
        # Show function name if available
        function_name = getattr(self._tool_item, "name", None)
        if function_name:
            parts.append(f"{ICONS['function_call']}{function_name}()")
        
        # Show arguments preview if available
        arguments = getattr(self._tool_item, "arguments", None)
        if arguments:
            # Show preview of arguments
            if isinstance(arguments, str):
                args_preview = arguments[:30]
                if len(arguments) > 30:
                    args_preview += "..."
            else:
                args_preview = str(arguments)[:30]
                if len(str(arguments)) > 30:
                    args_preview += "..."
            parts.append(f"{ICONS['processing']}{args_preview}")
        
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