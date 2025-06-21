"""Code interpreter tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS


class PlaintextCodeInterpreterToolRender(PlaintextToolRenderBase):
    """Plaintext code interpreter tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("code_interpreter_call", "💻"), "Code Interpreter"
    
    def get_tool_details(self) -> str:
        """Get code interpreter specific details.
        
        Returns:
            Formatted details string showing language and code info
        """
        if not self._tool_item:
            return ""
        
        parts = []
        
        # Show language if available
        language = getattr(self._tool_item, "language", None)
        if language:
            parts.append(f"{ICONS['code_interpreter_call']}{language}")
        
        # Show code preview if available
        code = getattr(self._tool_item, "code", None)
        if code:
            # Show first line of code as preview
            first_line = code.split('\n')[0].strip()
            if len(first_line) > 30:
                first_line = first_line[:27] + "..."
            parts.append(f"{ICONS['processing']}{first_line}")
        
        return f" {ICONS['bullet']} ".join(parts) if parts else ""
    
    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextCodeInterpreterToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: Code interpreter tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Code interpreter tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 