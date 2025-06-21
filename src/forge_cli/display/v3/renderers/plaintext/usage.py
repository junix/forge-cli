"""Usage statistics renderer for plaintext display system."""

from rich.text import Text
from forge_cli.response._types.response import Response

from ..rendable import Rendable
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles
from ...style import ICONS


class PlaintextUsageRenderer(Rendable):
    """Plaintext usage statistics renderer."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize the usage renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
        """
        self.styles = styles
        self.config = config
        self._response = None
        self._render_count = 0
    
    def with_response(self, response: Response, render_count: int = 0) -> "PlaintextUsageRenderer":
        """Set the response and render count.
        
        Args:
            response: Response object with usage data
            render_count: Current render count for streaming feedback
            
        Returns:
            Self for method chaining
        """
        self._response = response
        self._render_count = render_count
        return self
    
    def render(self) -> Text | None:
        """Render usage statistics.
        
        Returns:
            Rich Text object with usage statistics or None if disabled
        """
        if not self._response or not self._response.usage or not self.config.show_usage:
            return None
        
        text = Text()
        usage = self._response.usage
        
        # Add newline for separation
        text.append("\n")
        
        # Status icon and render count
        icon, style = self.styles.get_status_icon_and_style(self._response.status)
        text.append(icon, style=style)
        
        text.append("# ", style=self.styles.get_style("info"))
        text.append(f"{self._render_count}", style=self.styles.get_style("warning"))
        
        # Input tokens
        text.append(f" {ICONS['input_tokens']}", style=self.styles.get_style("usage_label"))
        text.append(f"{usage.input_tokens or 0}", style=self.styles.get_style("usage"))
        
        # Output tokens
        text.append(f" {ICONS['output_tokens']}", style=self.styles.get_style("usage_label"))
        text.append(f"{usage.output_tokens or 0}", style=self.styles.get_style("usage"))
        text.append("\n")
        
        return text
    
    @classmethod
    def from_response(cls, response: Response, render_count: int, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextUsageRenderer":
        """Factory method to create renderer from response.
        
        Args:
            response: Response object with usage data
            render_count: Current render count
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Usage renderer configured with response data
        """
        return cls(styles, config).with_response(response, render_count)


# Legacy function for backward compatibility
def render_usage(response: Response, render_count: int, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        response: Response object with usage data
        render_count: Current render count
        styles: Style manager instance
        config: Display configuration
        
    Returns:
        Rendered Text object with usage statistics or None
    """
    renderer = PlaintextUsageRenderer.from_response(response, render_count, styles, config)
    return renderer.render() 