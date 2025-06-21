"""Code interpreter tool renderer for Rich display system."""

from ....style import ICONS
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
        self._code = None
        self._output = None
    
    def with_code(self, code: str | None) -> "CodeInterpreterToolRender":
        """Add code display to the render.
        
        Args:
            code: The code to be executed
            
        Returns:
            Self for method chaining
        """
        if code:
            self._code = code
            # Detect language from code
            code_lower = code.lower()
            if "import" in code_lower or "def " in code_lower:
                lang = "Python"
            elif "const " in code_lower or "function " in code_lower:
                lang = "JavaScript"
            elif "#include" in code_lower:
                lang = "C/C++"
            else:
                lang = "Code"

            # Extract first meaningful line
            lines = [line.strip() for line in code.split("\n") if line.strip() and not line.strip().startswith("#")]
            if lines:
                code_preview = lines[0][:35] + "..." if len(lines[0]) > 35 else lines[0]
                self._parts.append(f"{ICONS['code']}{lang}: `{code_preview}`")

                # Show line count for longer code
                total_lines = len([line for line in code.split("\n") if line.strip()])
                if total_lines > 5:
                    self._parts.append(f"{ICONS['code']}{total_lines} lines")
        return self
    
    def with_output(self, output: str | None) -> "CodeInterpreterToolRender":
        """Add output display to the render.
        
        Args:
            output: The execution output
            
        Returns:
            Self for method chaining
        """
        if output:
            self._output = output
            output_preview = str(output)[:30] + "..." if len(str(output)) > 30 else str(output)
            self._parts.append(f"{ICONS['output_tokens']}output: {output_preview}")
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
    
    def with_execution_trace(self, execution_trace: str | None) -> "CodeInterpreterToolRender":
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
            The formatted display string for the code interpreter tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}executing code..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        """Create a code interpreter tool render from a tool item and return the formatted string.
        
        Args:
            tool_item: The code interpreter tool item to render
            
        Returns:
            Formatted display string
        """
        renderer = cls()
        
        # Add code if available
        code = getattr(tool_item, 'code', None)
        if code:
            renderer.with_code(code)
        
        # Add output if available
        output = getattr(tool_item, 'output', None)
        if output:
            renderer.with_output(output)
        
        # Add status
        if hasattr(tool_item, 'status'):
            renderer.with_status(tool_item.status)
        
        return renderer.render() 