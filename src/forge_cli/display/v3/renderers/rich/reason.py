"""Reasoning renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.display.citation_styling import long2circled
from ...builder import TextBuilder
from ..rendable import Rendable


class ReasoningRenderer(Rendable):
    """Renderer for reasoning items with proper formatting."""
    
    def __init__(self, reasoning_item):
        """Initialize the reasoning renderer.
        
        Args:
            reasoning_item: The reasoning item to render
        """
        self.reasoning_item = reasoning_item
    
    def render(self) -> Markdown | None:
        """Render a reasoning item as a Markdown blockquote.
        
        Returns:
            Markdown object with reasoning text as blockquote, or None if no text
        """
        # Use the text property to get consolidated reasoning text
        reasoning_text = self.reasoning_item.text
        if reasoning_text:
            # Convert long-style citation markers to circled digits
            converted_text = long2circled(reasoning_text)
            # Format as blockquote markdown and return Markdown object
            blockquote_text = TextBuilder.from_text(converted_text).with_block_quote().build()
            return Markdown(blockquote_text)
        return None


# Legacy function for backward compatibility
def render_reasoning_item(reasoning_item) -> Markdown | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        reasoning_item: The reasoning item to render
        
    Returns:
        Markdown object with reasoning text as blockquote, or None if no text
    """
    return ReasoningRenderer(reasoning_item).render() 