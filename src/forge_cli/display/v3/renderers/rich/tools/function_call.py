"""Function call tool renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.response._types.response_function_tool_call import ResponseFunctionToolCall
from ....style import ICONS, STATUS_ICONS
from ...rendable import Rendable


class FunctionCallToolRender(Rendable):
    """Specialized renderer for function call tool calls.
    
    This class handles the rendering of function call tool calls with consistent styling
    and support for all function call tool properties.
    """
    
    def __init__(self):
        """Initialize the function call tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._function_name = None
    
    def with_function_name(self, function_name: str | None) -> "FunctionCallToolRender":
        """Add function name display to the render.
        
        Args:
            function_name: The name of the function being called
            
        Returns:
            Self for method chaining
        """
        if function_name:
            self._function_name = function_name
            self._parts.append(f"{ICONS['function_call']}{function_name}()")
        return self
    
    def with_arguments(self, arguments: dict | str | None) -> "FunctionCallToolRender":
        """Add function arguments display to the render.
        
        Args:
            arguments: The function arguments (dict or JSON string)
            
        Returns:
            Self for method chaining
        """
        if arguments:
            if isinstance(arguments, dict):
                # Show key count for dict
                arg_count = len(arguments)
                if arg_count > 0:
                    arg_word = "arg" if arg_count == 1 else "args"
                    self._parts.append(f"{ICONS['info']}{arg_count} {arg_word}")
            elif isinstance(arguments, str):
                # Show truncated string for JSON
                if len(arguments) > 30:
                    display_args = arguments[:27] + "..."
                else:
                    display_args = arguments
                self._parts.append(f"{ICONS['code']}`{display_args}`")
        return self
    
    def with_status(self, status: str) -> "FunctionCallToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the function call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_progress(self, progress: float | None) -> "FunctionCallToolRender":
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
    
    def with_execution_time(self, execution_time: float | None) -> "FunctionCallToolRender":
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
        tool_icon = ICONS.get("function_call", ICONS["processing"])
        tool_name = "Function"
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        elif self._function_name:
            result_summary = f"{ICONS['function_call']}{self._function_name}()"
        else:
            result_summary = f"{ICONS['processing']}calling function..."
        
        # Create complete tool line
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        return Markdown(tool_line)
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionToolCall) -> "FunctionCallToolRender":
        """Create a function call tool renderer from a tool item.
        
        Args:
            tool_item: The function call tool item to render
            
        Returns:
            FunctionCallToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add function name if available
        if tool_item.name:
            renderer.with_function_name(tool_item.name)
        
        # Add arguments if available
        if hasattr(tool_item, 'arguments') and tool_item.arguments:
            renderer.with_arguments(tool_item.arguments)
        
        # Add progress if available
        if hasattr(tool_item, 'progress') and tool_item.progress is not None:
            renderer.with_progress(tool_item.progress)
        
        # Add execution time if available
        if hasattr(tool_item, 'execution_time') and tool_item.execution_time is not None:
            renderer.with_execution_time(tool_item.execution_time)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        return renderer 