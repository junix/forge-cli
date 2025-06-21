"""Code interpreter tool renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.response._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
from ....style import ICONS, STATUS_ICONS
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
    
    def with_language(self, language: str | None) -> "CodeInterpreterToolRender":
        """Add programming language display to the render.
        
        Args:
            language: The programming language being executed
            
        Returns:
            Self for method chaining
        """
        if language:
            self._parts.append(f"{ICONS['code_interpreter_call']}{language}")
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
            # Show first line or truncated version for the tool line
            first_line = code.split('\n')[0]
            if len(first_line) > 40:
                display_code = first_line[:37] + "..."
            else:
                display_code = first_line
            self._parts.append(f'{ICONS["code"]}`{display_code}`')
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
            progress_percent = int(progress * 100)
            self._parts.append(f"{ICONS['processing']}{progress_percent}%")
        return self
    
    def with_execution_time(self, execution_time: float | None) -> "CodeInterpreterToolRender":
        """Add execution time display to the render.
        
        Args:
            execution_time: Execution time in seconds
            
        Returns:
            Self for method chaining
        """
        if execution_time is not None:
            if execution_time < 1:
                time_str = f"{int(execution_time * 1000)}ms"
            else:
                time_str = f"{execution_time:.1f}s"
            self._parts.append(f"{ICONS['timer']}{time_str}")
        return self
    
    def render(self) -> Markdown:
        """Build and return the complete rendered content as Markdown.
        
        Returns:
            Markdown object with formatted tool line
        """
        # Get tool icon and name
        tool_icon = ICONS.get("code_interpreter_call", ICONS["processing"])
        tool_name = "CodeInterpreter"
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        else:
            result_summary = f"{ICONS['processing']}executing code..."
        
        # Create complete tool line
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        return Markdown(tool_line)
    
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