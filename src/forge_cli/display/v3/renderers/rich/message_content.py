"""Message content renderer for Rich display system."""

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
    
    def render(self) -> str:
        """Render message content with proper formatting.
        
        Returns:
            Formatted content text
        """
        if self.content.type == "output_text":
            # Convert long-style citation markers to circled digits
            converted_text = long2circled(self.content.text)
            return converted_text
        elif self.content.type == "output_refusal":
            return f"> ⚠️ Response refused: {self.content.refusal}"
        return ""


# Legacy function for backward compatibility
def render_message_content(content) -> str:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        content: The message content to render
        
    Returns:
        Formatted content text
    """
    return MessageContentRenderer(content).render() 