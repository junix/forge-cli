"""Base tool renderer for plaintext display system."""

from forge_cli.response._types.response_output_item import ResponseOutputItem
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS, STATUS_ICONS


class PlaintextToolRenderBase:
    """Base class for plaintext tool renderers."""

    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize base tool renderer.
        
        Args:
            styles: Plaintext styling configuration
            config: Display configuration
        """
        self._styles = styles
        self._config = config
        self._tool_item: ResponseOutputItem | None = None

    def with_tool_item(self, tool_item: ResponseOutputItem) -> "PlaintextToolRenderBase":
        """Set the tool item to render.
        
        Args:
            tool_item: The tool item to render
            
        Returns:
            Self for method chaining
        """
        self._tool_item = tool_item
        return self

    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name. Override in subclasses.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        tool_type = getattr(self._tool_item, 'type', 'unknown_tool')
        tool_icon = ICONS.get(tool_type, ICONS["processing"])
        tool_name = tool_type.replace("_call", "").replace("_", " ").title()
        return tool_icon, tool_name

    def get_tool_details(self) -> str:
        """Get tool-specific details. Override in subclasses.
        
        Returns:
            Formatted details string
        """
        return ""

    def render(self) -> str:
        """Render the tool call as plaintext using the old clean style.
        
        Returns:
            Formatted plaintext string
        """
        if not self._tool_item:
            return ""

        # Get tool metadata
        tool_icon, tool_name = self.get_tool_metadata()
        
        # Get status
        status = getattr(self._tool_item, 'status', 'in_progress')
        status_icon = STATUS_ICONS.get(status, STATUS_ICONS["default"])
        
        # Build the tool line using the old clean format
        tool_line = f"{tool_icon} {tool_name} • {status_icon}{status}"
        
        # Get tool-specific details
        details = self.get_tool_details()
        if details:
            tool_line += f" {ICONS['bullet']} {details}"
        
        return tool_line

    def _format_with_style(self, text: str, style_name: str) -> str:
        """Format text with style (for plaintext, this is a no-op).
        
        Args:
            text: Text to format
            style_name: Style name
            
        Returns:
            Formatted text (unchanged for plaintext)
        """
        return text

    def _format_list(self, items: list[str], prefix: str = "  - ") -> str:
        """Format a list of items with consistent indentation.
        
        Args:
            items: List of items to format
            prefix: Prefix for each item
            
        Returns:
            Formatted list string
        """
        if not items:
            return ""
        return "\n".join(f"{prefix}{item}" for item in items)

    @classmethod
    def from_tool_item(cls, tool_item: ResponseOutputItem, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextToolRenderBase":
        """Create tool renderer from tool item.
        
        Args:
            tool_item: The tool item to render
            styles: Plaintext styling configuration
            config: Display configuration
            
        Returns:
            PlaintextToolRenderBase instance
        """
        renderer = cls(styles, config)
        return renderer.with_tool_item(tool_item) 