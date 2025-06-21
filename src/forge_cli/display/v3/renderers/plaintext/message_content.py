"""Message content renderer for plaintext display system with Markdown support."""

from rich.text import Text
from rich.markdown import Markdown
from ..rendable import Rendable
from .styles import PlaintextStyles


class PlaintextMessageContentRenderer(Rendable):
    """Plaintext message content renderer with full Markdown support."""
    
    def __init__(self, styles: PlaintextStyles):
        """Initialize the message content renderer.
        
        Args:
            styles: Style manager instance
        """
        self.styles = styles
        self._content = None
    
    def with_content(self, content) -> "PlaintextMessageContentRenderer":
        """Set the content to render.
        
        Args:
            content: Message content object
            
        Returns:
            Self for method chaining
        """
        self._content = content
        return self
    
    def render(self) -> Markdown | Text | None:
        """Render message content as Markdown.
        
        Returns:
            Rich Markdown object or Text for special cases
        """
        if not self._content:
            return None
        
        if self._content.type == "output_text":
            # Simply use Rich's Markdown renderer
            return Markdown(self._content.text)
        elif self._content.type == "output_refusal":
            # Handle refusals as styled text
            text = Text()
            text.append("⚠️  Response Refused: ", style=self.styles.get_style("warning"))
            text.append(f"{self._content.refusal}\n", style=self.styles.get_style("error"))
            return text
        
        return None
    
    @classmethod
    def from_content(cls, content, styles: PlaintextStyles) -> Markdown | Text | None:
        """Factory method to create and render content as Markdown.
        
        Args:
            content: Message content object
            styles: Style manager instance
            
        Returns:
            Rendered Markdown object or Text object or None
        """
        renderer = cls(styles).with_content(content)
        return renderer.render()


# Legacy function for backward compatibility
def render_message_content(content, styles: PlaintextStyles, config=None) -> Markdown | Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        content: Message content object
        styles: Style manager instance
        config: Deprecated parameter (ignored)
        
    Returns:
        Rendered Markdown object or Text object or None
    """
    return PlaintextMessageContentRenderer.from_content(content, styles) 