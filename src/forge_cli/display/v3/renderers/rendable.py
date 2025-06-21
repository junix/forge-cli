from rich.text import Text
from rich.panel import Panel
from rich.table import Table

class Rendable:
    """Base class for rendable objects."""

    def render(self) -> str | Text | Panel | Table | None :
        """Render the object."""
        raise NotImplementedError("Subclasses must implement this method")


class ToolRendable(Rendable):
    """Base class for tool renderers with common functionality."""
    
    def __init__(self):
        """Initialize the tool renderer."""
        self._status = "in_progress"
        self._execution_trace = None
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        # To be overridden by subclasses
        from forge_cli.display.v3.style import ICONS
        return ICONS["processing"], "Tool"
    
    def with_execution_trace(self, execution_trace: str | None) -> "ToolRendable":
        """Add execution trace for traceable tools.
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        self._execution_trace = execution_trace
        return self
    
    def _get_trace_block(self) -> list[str] | None:
        """Extract and format trace lines for display.
        
        Returns:
            List of formatted trace lines or None if no trace available
        """
        if not self._execution_trace:
            return None
        
        from forge_cli.display.v3.builder import TextBuilder
        return TextBuilder.from_text(self._execution_trace).with_slide(max_lines=3, format_type="text").build()
    
    def render_complete_tool_line(self) -> str:
        """Render the complete tool line including icon, name, status, and results.
        
        Returns:
            Complete formatted tool line ready for display
        """
        from forge_cli.display.v3.style import ICONS, STATUS_ICONS
        
        # Get tool icon and name from subclass
        tool_icon, tool_name = self.get_tool_metadata()
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Get result summary from subclass render method
        result_summary = self.render()
        
        # Format: Tool Icon + Bold Name + Status Icon + Status + Result
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        return tool_line
    
    def render_complete_tool_with_trace(self) -> list[str]:
        """Render complete tool content including tool line and trace block.
        
        Returns:
            List of markdown parts (tool line and optional trace block)
        """
        parts = []
        
        # Always include the tool line
        tool_line = self.render_complete_tool_line()
        parts.append(tool_line)
        
        # Add trace block if available
        trace_block = self._get_trace_block()
        if trace_block:
            parts.extend(trace_block)
        
        return parts
