"""Code interpreter tool renderer for Rich display system."""

from rich.text import Text
from forge_cli.response._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
from ....style import ICONS, STATUS_ICONS, get_status_color
from ...rendable import Rendable


class CodeInterpreterToolRender(Rendable):
    """Specialized renderer for code interpreter tool calls.
    
    This class handles the rendering of code interpreter tool calls with consistent styling
    and support for all code interpreter tool properties.
    """
    
    def __init__(self):
        """Initialize the code interpreter tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._code_snippet = None
        self._progress = None
        self._language = None
        self._execution_time = None
    
    def with_language(self, language: str | None) -> "CodeInterpreterToolRender":
        """Add programming language display to the render.
        
        Args:
            language: The programming language being executed
            
        Returns:
            Self for method chaining
        """
        if language:
            self._language = language
        return self
    
    def with_code_snippet(self, code: str | None) -> "CodeInterpreterToolRender":
        """Add code snippet display to the render.
        
        Args:
            code: The code being executed (will be truncated for display)
            
        Returns:
            Self for method chaining
        """
        if code:
            # Store full code for potential detailed display
            self._code_snippet = code
        return self
    
    def with_status(self, status: str) -> "CodeInterpreterToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the code interpreter call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_progress(self, progress: float | None) -> "CodeInterpreterToolRender":
        """Add progress display to the render.
        
        Args:
            progress: Progress as a float between 0 and 1
            
        Returns:
            Self for method chaining
        """
        if progress is not None:
            self._progress = progress
        return self
    
    def with_execution_time(self, execution_time: float | None) -> "CodeInterpreterToolRender":
        """Add execution time display to the render.
        
        Args:
            execution_time: Execution time in seconds
            
        Returns:
            Self for method chaining
        """
        if execution_time is not None:
            self._execution_time = execution_time
        return self
    
    def render(self) -> list[Text]:
        """Build and return the complete rendered content as Text objects.
        
        Returns:
            List of Text objects with formatted tool line
        """
        parts = []
        
        # Get tool icon and name (keep original icons unchanged)
        tool_icon = ICONS.get("code_interpreter_call", ICONS["processing"])
        tool_name = "CodeInterpreter"
        
        # Get status color using mood-based colors
        status_color = get_status_color(self._status)
        
        # Build the tool line with colors
        tool_line = Text()
        
        # Add tool icon and name - tool name in bright_white + bold
        tool_line.append(f"{tool_icon} ")
        tool_line.append(tool_name, style="bright_white bold italic")
        tool_line.append(" • ")
        
        # Add status with mood-based color
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        tool_line.append(f"{status_icon}")
        tool_line.append(self._status, style=f"{status_color} italic")
        
        # Add progress if available - bright_cyan for active feeling
        if self._progress is not None:
            progress_percent = int(self._progress * 100)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}")
            tool_line.append(f"{progress_percent}%", style="bright_cyan bold")
        
        # Add language if available
        if self._language:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['code_interpreter_call']}")
            tool_line.append(self._language, style="bright_yellow")
        
        # Add code snippet if available - bright_yellow for code queries
        if self._code_snippet:
            # Show first line or truncated version for the tool line
            first_line = self._code_snippet.split('\n')[0]
            if len(first_line) > 40:
                display_code = first_line[:37] + "..."
            else:
                display_code = first_line
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f'{ICONS["code"]}`')
            tool_line.append(display_code, style="bright_yellow")
            tool_line.append("`")
        
        # Add execution time if available
        if self._execution_time is not None:
            if self._execution_time < 1:
                time_str = f"{int(self._execution_time * 1000)}ms"
            else:
                time_str = f"{self._execution_time:.1f}s"
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['timer']}")
            tool_line.append(time_str, style="bright_cyan")
        
        # Add other parts if available
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(result_summary)
        elif not self._language and not self._code_snippet and self._progress is None:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}executing code...")
        
        parts.append(tool_line)
        return parts
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseCodeInterpreterToolCall) -> "CodeInterpreterToolRender":
        """Create a code interpreter tool renderer from a tool item.
        
        Args:
            tool_item: The code interpreter tool item to render
            
        Returns:
            CodeInterpreterToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add language if available
        if hasattr(tool_item, 'language') and tool_item.language:
            renderer.with_language(tool_item.language)
        
        # Add code snippet if available
        if hasattr(tool_item, 'code') and tool_item.code:
            renderer.with_code_snippet(tool_item.code)
        
        # Add progress if available
        if hasattr(tool_item, 'progress') and tool_item.progress is not None:
            renderer.with_progress(tool_item.progress)
        
        # Add execution time if available
        if hasattr(tool_item, 'execution_time') and tool_item.execution_time is not None:
            renderer.with_execution_time(tool_item.execution_time)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        return renderer 