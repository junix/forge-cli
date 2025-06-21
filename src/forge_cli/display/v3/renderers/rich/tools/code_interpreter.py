"""Code interpreter tool renderer for Rich display system."""

from forge_cli.response._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
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
            # Detect language based on code content
            language = self._detect_language(code)
            
            # Show code preview (first line or short snippet)
            code_preview = code.split('\n')[0][:30] + "..." if len(code) > 30 else code.split('\n')[0]
            code_preview = code_preview.replace('`', "'")  # Avoid markdown conflicts
            
            self._parts.append(f"{ICONS['code']}Code: `{code_preview}`")
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
            output_str = str(output)[:30] + "..." if len(str(output)) > 30 else str(output)
            self._parts.append(f"{ICONS['output_tokens']}output: {output_str}")
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
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content.
        
        Args:
            code: The code string to analyze
            
        Returns:
            Detected language name
        """
        code_lower = code.lower().strip()
        
        # Python indicators
        if any(keyword in code_lower for keyword in ['import ', 'def ', 'print(', 'if __name__']):
            return "Python"
        
        # JavaScript indicators  
        if any(keyword in code_lower for keyword in ['function ', 'const ', 'let ', 'var ', 'console.log']):
            return "JavaScript"
        
        # Default fallback
        return "Code"
    
    def render(self) -> str:
        """Build and return the final rendered string.
        
        Returns:
            The formatted display string for the code interpreter tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}executing code..."
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseCodeInterpreterToolCall) -> "CodeInterpreterToolRender":
        """Create a code interpreter tool renderer from a tool item.
        
        Args:
            tool_item: The code interpreter tool item to render
            
        Returns:
            CodeInterpreterToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add code if available
        if tool_item.code:
            renderer.with_code(tool_item.code)
        
        # Add output if available (from results)
        if tool_item.results:
            # Combine results into a single output string
            output_parts = []
            for result in tool_item.results:
                if hasattr(result, 'text') and result.text:
                    output_parts.append(result.text)
            if output_parts:
                combined_output = "\n".join(output_parts)
                renderer.with_output(combined_output)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        return renderer 