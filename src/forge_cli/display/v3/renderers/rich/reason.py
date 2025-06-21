"""Reasoning renderer for Rich display system."""

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
    
    def render(self) -> str:
        """Render a reasoning item with proper formatting.
        
        Returns:
            Formatted reasoning text as blockquote
        """
        # Use the text property to get consolidated reasoning text
        reasoning_text = self.reasoning_item.text
        if reasoning_text:
            # Use Builder pattern for clean text processing
            return TextBuilder.from_text(reasoning_text).with_block_quote().build()
        return ""


# Legacy function for backward compatibility
def render_reasoning_item(reasoning_item) -> str:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        reasoning_item: The reasoning item to render
        
    Returns:
        Formatted reasoning text as blockquote
    """
    return ReasoningRenderer(reasoning_item).render() 