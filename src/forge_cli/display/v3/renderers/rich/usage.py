"""Usage renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.display.v3.style import ICONS
from forge_cli.response._types.response_usage import ResponseUsage
from ..rendable import Rendable


class UsageRenderer(Rendable):
    """Specialized renderer for response usage information.
    
    This class handles the rendering of token usage statistics with consistent styling
    and icon support.
    """
    
    def __init__(self):
        """Initialize the usage renderer."""
        self._input_tokens = None
        self._output_tokens = None
        self._total_tokens = None
    
    def with_input_tokens(self, input_tokens: int | None) -> "UsageRenderer":
        """Add input token count to the render.
        
        Args:
            input_tokens: Number of input tokens used
            
        Returns:
            Self for method chaining
        """
        self._input_tokens = input_tokens
        return self
    
    def with_output_tokens(self, output_tokens: int | None) -> "UsageRenderer":
        """Add output token count to the render.
        
        Args:
            output_tokens: Number of output tokens generated
            
        Returns:
            Self for method chaining
        """
        self._output_tokens = output_tokens
        return self
    
    def with_total_tokens(self, total_tokens: int | None) -> "UsageRenderer":
        """Add total token count to the render.
        
        Args:
            total_tokens: Total number of tokens (input + output)
            
        Returns:
            Self for method chaining
        """
        self._total_tokens = total_tokens
        return self
    
    def render(self) -> str:
        """Build and return the formatted usage string for panel title.
        
        Note: This returns a string (not Markdown) because it's used for panel titles.
        Use render_as_markdown() for Markdown content.
        
        Returns:
            Formatted usage string with icons and colors, or empty string if no usage data
        """
        if not self._input_tokens and not self._output_tokens:
            return ""
        
        title_parts = []
        
        # Input tokens with icon and color
        if self._input_tokens is not None:
            title_parts.append("[yellow]" + ICONS["input_tokens"] + "[/yellow]")
            title_parts.append(f"[green]{self._input_tokens}[/green]")
        
        # Output tokens with icon and color
        if self._output_tokens is not None:
            title_parts.append("[yellow]" + ICONS["output_tokens"] + "[/yellow]")
            title_parts.append(f"[green]{self._output_tokens}[/green]")
        
        return " ".join(title_parts)
    
    def render_as_markdown(self) -> Markdown | None:
        """Build and return usage information as Markdown.
        
        Returns:
            Markdown object with formatted usage information or None if no usage data
        """
        if not self._input_tokens and not self._output_tokens and not self._total_tokens:
            return None
        
        parts = []
        
        # Input tokens
        if self._input_tokens is not None:
            parts.append(f"**Input tokens:** {self._input_tokens}")
        
        # Output tokens
        if self._output_tokens is not None:
            parts.append(f"**Output tokens:** {self._output_tokens}")
        
        # Total tokens (if different from input + output or if only total is available)
        if self._total_tokens is not None:
            if not self._input_tokens or not self._output_tokens or self._total_tokens != (self._input_tokens + self._output_tokens):
                parts.append(f"**Total tokens:** {self._total_tokens}")
        
        if parts:
            usage_text = " • ".join(parts)
            return Markdown(usage_text)
        return None
    
    def render_detailed(self) -> str:
        """Build and return a detailed usage string including total tokens.
        
        Returns:
            Detailed formatted usage string with all available token information
        """
        if not self._input_tokens and not self._output_tokens and not self._total_tokens:
            return ""
        
        parts = []
        
        # Input tokens
        if self._input_tokens is not None:
            parts.append(f"{ICONS['input_tokens']}Input: {self._input_tokens}")
        
        # Output tokens
        if self._output_tokens is not None:
            parts.append(f"{ICONS['output_tokens']}Output: {self._output_tokens}")
        
        # Total tokens (if different from input + output or if only total is available)
        if self._total_tokens is not None:
            if not self._input_tokens or not self._output_tokens or self._total_tokens != (self._input_tokens + self._output_tokens):
                parts.append(f"{ICONS['processing']}Total: {self._total_tokens}")
        
        return " • ".join(parts)
    
    @classmethod
    def from_usage_object(cls, usage: ResponseUsage) -> "UsageRenderer":
        """Create a usage renderer from a usage object.
        
        Args:
            usage: The usage object containing token information
            
        Returns:
            UsageRenderer instance configured with the usage data
        """
        renderer = cls()
        
        # Add input tokens if available
        if hasattr(usage, 'input_tokens') and usage.input_tokens is not None:
            renderer.with_input_tokens(usage.input_tokens)
        
        # Add output tokens if available
        if hasattr(usage, 'output_tokens') and usage.output_tokens is not None:
            renderer.with_output_tokens(usage.output_tokens)
        
        # Add total tokens if available
        if hasattr(usage, 'total_tokens') and usage.total_tokens is not None:
            renderer.with_total_tokens(usage.total_tokens)
        
        return renderer 