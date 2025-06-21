"""Function call tool renderer for Rich display system."""

from rich.text import Text
from forge_cli.response._types.response_function_tool_call import ResponseFunctionToolCall
from ....style import ICONS, STATUS_ICONS, get_status_color
from ....builder import TextBuilder
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
        self._execution_trace = None
        self._progress = None
        self._function_name = None
        self._arguments = None
    
    def with_function_name(self, function_name: str | None) -> "FunctionCallToolRender":
        """Add function name display to the render.
        
        Args:
            function_name: The name of the function being called
            
        Returns:
            Self for method chaining
        """
        if function_name:
            self._function_name = function_name
        return self
    
    def with_arguments(self, arguments: dict | str | None) -> "FunctionCallToolRender":
        """Add function arguments display to the render.
        
        Args:
            arguments: The arguments passed to the function
            
        Returns:
            Self for method chaining
        """
        if arguments:
            self._arguments = arguments
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
            self._progress = progress
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "FunctionCallToolRender":
        """Add execution trace for later inclusion in complete render.
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        self._execution_trace = execution_trace
        return self
    
    def render(self) -> list[Text]:
        """Build and return the complete rendered content including tool line and trace.
        
        Returns:
            List of Text objects (tool line and optional trace block)
        """
        parts = []
        
        # Get tool icon and name (keep original icons unchanged) 
        tool_icon = ICONS.get("function_call", ICONS["processing"])
        tool_name = "Function"
        
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
        
        # Add function name if available - bright_yellow for function names
        if self._function_name:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['function_call']}")
            tool_line.append(self._function_name, style="bright_yellow bold")
        
        # Add arguments preview if available
        if self._arguments:
            # Show a brief preview of arguments
            if isinstance(self._arguments, dict):
                if len(self._arguments) == 1:
                    key, value = next(iter(self._arguments.items()))
                    if isinstance(value, str) and len(value) < 20:
                        args_preview = f"{key}={value}"
                    else:
                        args_preview = f"{key}=..."
                else:
                    args_preview = f"{len(self._arguments)} args"
            elif isinstance(self._arguments, str):
                if len(self._arguments) < 30:
                    args_preview = self._arguments
                else:
                    args_preview = self._arguments[:27] + "..."
            else:
                args_preview = "args"
            
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"({args_preview})")
        
        # Add other parts in default white
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(result_summary)
        elif not self._function_name and self._progress is None:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}calling function...")
        
        parts.append(tool_line)
        
        # Add execution trace if available
        if self._execution_trace:
            trace_block = TextBuilder.from_text(self._execution_trace).with_slide(max_lines=3, format_type="text").build()
            if trace_block:
                # Convert trace block strings to Text objects
                for trace_line in trace_block:
                    if isinstance(trace_line, str):
                        parts.append(Text(trace_line))
                    else:
                        parts.append(trace_line)
        
        return parts
    
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
        if hasattr(tool_item, 'function_name') and tool_item.function_name:
            renderer.with_function_name(tool_item.function_name)
        elif hasattr(tool_item, 'name') and tool_item.name:
            renderer.with_function_name(tool_item.name)
        
        # Add arguments if available
        if hasattr(tool_item, 'arguments') and tool_item.arguments:
            renderer.with_arguments(tool_item.arguments)
        
        # Add progress if available
        if hasattr(tool_item, 'progress') and tool_item.progress is not None:
            renderer.with_progress(tool_item.progress)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add execution trace if available
        execution_trace = getattr(tool_item, "execution_trace", None)
        if execution_trace:
            renderer.with_execution_trace(execution_trace)
        
        return renderer 