"""Message content renderer for plaintext display system."""

from rich.text import Text
from ..rendable import Rendable
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles


class PlaintextMessageContentRenderer(Rendable):
    """Plaintext message content renderer."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize the message content renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
        """
        self.styles = styles
        self.config = config
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
    
    def render(self) -> Text | None:
        """Render message content with proper formatting.
        
        Returns:
            Rich Text object with formatted content
        """
        if not self._content:
            return None
        
        if self._content.type == "output_text":
            # Create text with white style for main content
            text = Text()
            self._add_formatted_text(text, self._content.text, style=self.styles.get_style("content"))
            return text
        elif self._content.type == "output_refusal":
            text = Text()
            text.append("⚠️  Response Refused: ", style=self.styles.get_style("warning"))
            text.append(f"{self._content.refusal}\n", style=self.styles.get_style("error"))
            return text
        
        return None
    
    def _add_formatted_text(self, text: Text, content: str, style: str = None) -> None:
        """Add formatted text content with simple markdown-like styling.
        
        Args:
            text: Rich Text object to append to
            content: Content string to format
            style: Base style to use
        """
        if style is None:
            style = self.styles.get_style("content")

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                text.append("\n")
                continue

            # Handle headers
            if line.startswith("# "):
                # Create centered header by calculating padding
                header_text = line[2:]
                console_width = 80  # Default console width
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style=self.styles.get_style("header"))
                text.append("\n")
            elif line.startswith("## "):
                # Create centered header by calculating padding
                header_text = line[3:]
                console_width = 80  # Default console width
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style="bold white")
                text.append("\n")
            elif line.startswith("### "):
                # Create centered header by calculating padding
                header_text = line[4:]
                console_width = 80  # Default console width
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style="bold dim white")
                text.append("\n")
            # Regular text
            else:
                text.append(line)
                text.append("\n")
    
    def _apply_inline_formatting(self, line: str, base_style: str = None) -> Text:
        """Apply simple inline formatting like **bold** and *italic*.
        
        Args:
            line: Line to format
            base_style: Base style to apply
            
        Returns:
            Rich Text object with inline formatting applied
        """
        if base_style is None:
            base_style = self.styles.get_style("content")

        result = Text()
        i = 0

        while i < len(line):
            # Check for **bold**
            if i < len(line) - 3 and line[i : i + 2] == "**":
                end = line.find("**", i + 2)
                if end != -1:
                    result.append(line[i + 2 : end], style="bold " + base_style)
                    i = end + 2
                    continue

            # Check for *italic*
            if i < len(line) - 2 and line[i] == "*" and line[i + 1] != "*":
                end = line.find("*", i + 1)
                if end != -1:
                    result.append(line[i + 1 : end], style="italic " + base_style)
                    i = end + 1
                    continue

            # Check for `code`
            if i < len(line) - 2 and line[i] == "`":
                end = line.find("`", i + 1)
                if end != -1:
                    result.append(line[i + 1 : end], style="bold green")
                    i = end + 1
                    continue

            # Regular character
            result.append(line[i], style=base_style)
            i += 1

        return result
    
    @classmethod
    def from_content(cls, content, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
        """Factory method to create and render content.
        
        Args:
            content: Message content object
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Rendered Text object or None
        """
        renderer = cls(styles, config).with_content(content)
        return renderer.render()


# Legacy function for backward compatibility
def render_message_content(content, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        content: Message content object
        styles: Style manager instance
        config: Display configuration
        
    Returns:
        Rendered Text object or None
    """
    return PlaintextMessageContentRenderer.from_content(content, styles, config) 