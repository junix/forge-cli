"""Function call tool renderer for Rich display system."""

from ....style import ICONS
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
        self._function = None
        self._arguments = None
        self._output = None
    
    def with_function(self, function: str | None) -> "FunctionCallToolRender":
        """Add function name display to the render.
        
        Args:
            function: The function name
            
        Returns:
            Self for method chaining
        """
        if function:
            self._function = function
            self._parts.append(f"{ICONS['function_call']}{function}")
        return self
    
    def with_arguments(self, arguments: str | dict | None) -> "FunctionCallToolRender":
        """Add arguments display to the render.
        
        Args:
            arguments: The function arguments (string or dict)
            
        Returns:
            Self for method chaining
        """
        if arguments:
            self._arguments = arguments
            try:
                import json
                
                args = (
                    json.loads(arguments)
                    if isinstance(arguments, str)
                    else arguments
                )
                if isinstance(args, dict):
                    arg_preview = ", ".join(f"{k}={v}" for k, v in list(args.items())[:2])
                    if len(args) > 2:
                        arg_preview += f", +{len(args) - 2} more"
                    self._parts.append(f"{ICONS['code']}({arg_preview})")
            except Exception:
                self._parts.append(f"{ICONS['code']}(with arguments)")
        return self
    
    def with_output(self, output: str | None) -> "FunctionCallToolRender":
        """Add output display to the render.
        
        Args:
            output: The function execution output
            
        Returns:
            Self for method chaining
        """
        if output:
            self._output = output
            output_str = str(output)[:40] + "..." if len(str(output)) > 40 else str(output)
            self._parts.append(f"{ICONS['check']}{output_str}")
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
    
    def with_execution_trace(self, execution_trace: str | None) -> "FunctionCallToolRender":
        """Add execution trace to the render (handled separately in trace blocks).
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        # Execution trace is handled separately in trace blocks
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string.
        
        Returns:
            The formatted display string for the function call tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}calling function..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> "FunctionCallToolRender":
        """Create a function call tool renderer from a tool item.
        
        Args:
            tool_item: The function call tool item to render
            
        Returns:
            FunctionCallToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add function name
        if hasattr(tool_item, 'function') and tool_item.function:
            renderer.with_function(tool_item.function)
        
        # Add arguments
        if hasattr(tool_item, 'arguments') and tool_item.arguments:
            renderer.with_arguments(tool_item.arguments)
        
        # Add output if available
        output = getattr(tool_item, 'output', None)
        if output:
            renderer.with_output(output)
        
        # Add status
        if hasattr(tool_item, 'status'):
            renderer.with_status(tool_item.status)
        
        return renderer 