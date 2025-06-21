"""Reasoning renderer for plaintext display system."""

from rich.text import Text

from forge_cli.display.v3.builder import TextBuilder
from forge_cli.response._types.response_reasoning_item import ResponseReasoningItem
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles
from rich.markdown import Markdown


class PlaintextReasoningRenderer:
    """Renderer for reasoning content in plaintext format."""

    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize reasoning renderer.
        
        Args:
            styles: Plaintext styling configuration
            config: Display configuration
        """
        self._styles = styles
        self._config = config
        self._reasoning_items: list[ResponseReasoningItem] = []

    def with_reasoning_items(self, items: list[ResponseReasoningItem]) -> "PlaintextReasoningRenderer":
        """Add reasoning items to render.
        
        Args:
            items: List of reasoning items
            
        Returns:
            Self for method chaining
        """
        self._reasoning_items = items
        return self

    def render(self) -> list[Markdown] | None:
        """Render reasoning items as Text object.
        
        Returns:
            Text object with formatted reasoning content or None if no reasoning items
        """
        if not self._reasoning_items:
            return None

        acc = []
        for item in self._reasoning_items:
            text = item.text
            if not text:
                continue

            text = TextBuilder.from_text(text).with_slide(max_lines=5, format_type="markdown").with_block_quote().build()
            acc.append(Markdown(text+"\n"))
        return acc


    @classmethod
    def from_response_items(cls, items: list[ResponseReasoningItem], styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextReasoningRenderer":
        """Create reasoning renderer from response items.
        
        Args:
            items: List of reasoning items from response
            styles: Plaintext styling configuration
            config: Display configuration
            
        Returns:
            PlaintextReasoningRenderer instance
        """
        renderer = cls(styles, config)
        return renderer.with_reasoning_items(items)

    @classmethod
    def from_single_item(cls, item: ResponseReasoningItem, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextReasoningRenderer":
        """Create reasoning renderer from a single reasoning item.
        
        Args:
            item: Single reasoning item
            styles: Plaintext styling configuration
            config: Display configuration
            
        Returns:
            PlaintextReasoningRenderer instance
        """
        renderer = cls(styles, config)
        return renderer.with_reasoning_items([item])


# Legacy function for backward compatibility
def render_reasoning(items: list[ResponseReasoningItem], styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        items: List of reasoning items
        styles: Plaintext styling configuration
        config: Display configuration
        
    Returns:
        Text object with formatted reasoning content or None if no reasoning items
    """
    return PlaintextReasoningRenderer.from_response_items(items, styles, config).render() 