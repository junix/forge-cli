"""Reasoning content renderer for plaintext display system."""

from typing import Any

from rich.text import Text
from forge_cli.response.type_guards import is_reasoning_item

from ..rendable import Rendable
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles


class PlaintextReasoningRenderer(Rendable):
    """Plaintext reasoning content renderer."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize the reasoning renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
        """
        self.styles = styles
        self.config = config
        self._reasoning_items = []
    
    def with_reasoning_items(self, items: list[Any]) -> "PlaintextReasoningRenderer":
        """Set the reasoning items to render.
        
        Args:
            items: List of reasoning items
            
        Returns:
            Self for method chaining
        """
        self._reasoning_items = items
        return self
    
    def render(self) -> Text | None:
        """Render reasoning content with proper formatting.
        
        Returns:
            Rich Text object with formatted reasoning content or None if disabled
        """
        if not self._reasoning_items or not self.config.show_reasoning:
            return None
        
        text = Text()
        
        for item in self._reasoning_items:
            if hasattr(item, 'text') and item.text:
                # Add spacing before reasoning content
                text.append("\n")
                
                # Add reasoning text with dark green italic style
                reasoning_lines = item.text.split("\n")
                for line in reasoning_lines:
                    if line.strip():
                        indent = " " * self.config.indent_size
                        text.append(f"{indent}{line.strip()}\n", style=self.styles.get_style("reasoning"))
                    else:
                        text.append("\n")
                
                # Add spacing after reasoning content
                text.append("\n")
        
        return text
    
    @classmethod
    def from_response_items(cls, items: list[Any], styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextReasoningRenderer":
        """Factory method to create renderer from response items.
        
        Args:
            items: List of response output items
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Reasoning renderer with filtered reasoning items
        """
        reasoning_items = [item for item in items if is_reasoning_item(item)]
        return cls(styles, config).with_reasoning_items(reasoning_items)
    
    @classmethod
    def from_single_item(cls, item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextReasoningRenderer":
        """Factory method to create renderer from a single reasoning item.
        
        Args:
            item: Single reasoning item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Reasoning renderer with single item
        """
        items = [item] if is_reasoning_item(item) else []
        return cls(styles, config).with_reasoning_items(items)


# Legacy function for backward compatibility
def render_reasoning(items: list[Any], styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        items: List of response output items
        styles: Style manager instance
        config: Display configuration
        
    Returns:
        Rendered Text object with reasoning content or None
    """
    renderer = PlaintextReasoningRenderer.from_response_items(items, styles, config)
    return renderer.render() 