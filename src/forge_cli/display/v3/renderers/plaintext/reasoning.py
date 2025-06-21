"""Reasoning renderer for plaintext display system."""

from rich.text import Text

from forge_cli.response._types.response_reasoning_item import ResponseReasoningItem
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles


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

    def render(self) -> Text | None:
        """Render reasoning items as Text object.
        
        Returns:
            Text object with formatted reasoning content or None if no reasoning items
        """
        if not self._reasoning_items or not self._config.show_reasoning:
            return None

        text = Text()
        
        # Add reasoning header
        text.append("🤔 Reasoning:\n", style=self._styles.get_style("reasoning_header"))
        
        for idx, item in enumerate(self._reasoning_items):
            if idx > 0:
                text.append("\n")
            
            # Add reasoning content
            if hasattr(item, 'summary') and item.summary:
                for summary_item in item.summary:
                    if hasattr(summary_item, 'text'):
                        # Indent reasoning content
                        for line in summary_item.text.split('\n'):
                            if line.strip():
                                text.append(f"  {line}\n", style=self._styles.get_style("reasoning_content"))
                            else:
                                text.append("\n")
        
        return text

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