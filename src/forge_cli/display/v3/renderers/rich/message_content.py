"""Message content renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.display.citation_styling import long2circled
from ..rendable import Rendable


class MessageContentRenderer(Rendable):
    """Renderer for message content (text/refusal) with proper formatting."""
    
    def __init__(self, content):
        """Initialize the message content renderer.
        
        Args:
            content: The message content to render
        """
        self.content = content
    
    def render(self) -> Markdown | None:
        """Render message content as Markdown object.
        
        Returns:
            Markdown object with formatted content or None if no content
        """
        if self.content.type == "output_text":
            # Convert long-style citation markers to circled digits
            converted_text = long2circled(self.content.text)
            return Markdown(converted_text)
        elif self.content.type == "output_refusal":
            refusal_text = f"> ⚠️ Response refused: {self.content.refusal}"
            return Markdown(refusal_text)
        return None


# Legacy function for backward compatibility
def render_message_content(content) -> Markdown | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        content: The message content to render
        
    Returns:
        Markdown object with formatted content or None if no content
    """
    return MessageContentRenderer(content).render() 