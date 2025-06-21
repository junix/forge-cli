"""Base class for plaintext tool renderers."""

from typing import Any

from rich.text import Text
from ...rendable import Rendable
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS


class PlaintextToolRenderBase(Rendable):
    """Base class for plaintext tool renderers."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize the tool renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
        """
        self.styles = styles
        self.config = config
        self._tool_item = None
        self._status = "in_progress"
    
    def with_tool_item(self, tool_item: Any) -> "PlaintextToolRenderBase":
        """Set the tool item to render.
        
        Args:
            tool_item: Tool item object
            
        Returns:
            Self for method chaining
        """
        self._tool_item = tool_item
        self._status = getattr(tool_item, 'status', 'in_progress')
        return self
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name) - subclasses should override
        """
        return ICONS.get("processing", "🔧"), "Tool"
    
    def get_tool_details(self) -> str:
        """Get tool-specific details string.
        
        Returns:
            Formatted details string - subclasses should override
        """
        return ""
    
    def render(self) -> Text:
        """Render tool item with colorful display.
        
        Returns:
            Rich Text object with formatted tool display
        """
        text = Text()
        
        # Get tool metadata
        tool_icon, tool_name = self.get_tool_metadata()
        
        # Tool icon with yellow color
        text.append(f"{tool_icon}", style=self.styles.get_style("tool_icon"))
        
        # Tool name with vibrant magenta color
        text.append(f"{tool_name}", style=self.styles.get_style("tool_name"))
        text.append(f" {ICONS['bullet']} ", style=self.styles.get_style("separator"))
        
        # Status with appropriate color and icon
        icon, style = self.styles.get_status_icon_and_style(self._status)
        text.append(icon, style=style)
        
        # Tool-specific details with cyan color
        details = self.get_tool_details()
        if details:
            text.append(f" {ICONS['bullet']} ", style=self.styles.get_style("separator"))
            text.append(details, style=self.styles.get_style("tool_details"))
        
        text.append("\n\n")
        return text
    
    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextToolRenderBase":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: Tool item object
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Tool renderer configured with tool item
        """
        return cls(styles, config).with_tool_item(tool_item) 