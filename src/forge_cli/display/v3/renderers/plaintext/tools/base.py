"""Base tool renderer for plaintext display system."""

from forge_cli.response._types.response_output_item import ResponseOutputItem
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles


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

    def render(self) -> str:
        """Render the tool call as plaintext.
        
        Returns:
            Formatted plaintext string
        """
        if not self._tool_item:
            return ""

        # Build basic tool information
        parts = []
        
        # Add tool header
        tool_type = getattr(self._tool_item, 'type', 'unknown_tool')
        tool_id = getattr(self._tool_item, 'id', 'unknown_id')
        status = getattr(self._tool_item, 'status', 'unknown')
        
        header = f"[{tool_type.upper()}] {tool_id} - {status}"
        parts.append(header)
        
        # Add tool-specific content
        tool_content = self._render_tool_specific_content()
        if tool_content:
            parts.append(tool_content)
        
        return "\n".join(parts)

    def _render_tool_specific_content(self) -> str:
        """Render tool-specific content. Override in subclasses.
        
        Returns:
            Tool-specific content string
        """
        return ""

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