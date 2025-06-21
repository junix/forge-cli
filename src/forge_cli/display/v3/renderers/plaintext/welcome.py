"""Welcome screen renderer for plaintext display system."""

from typing import TYPE_CHECKING, Any

from rich.text import Text
from rich.console import Console

from ..rendable import Rendable
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles

if TYPE_CHECKING:
    from ....config import AppConfig


class PlaintextWelcomeRenderer(Rendable):
    """Plaintext welcome screen renderer."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig, console: Console = None):
        """Initialize the welcome renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
            console: Rich console instance (optional)
        """
        self.styles = styles
        self.config = config
        self._console = console or Console()
        self._app_config = None
    
    def with_app_config(self, app_config: "AppConfig") -> "PlaintextWelcomeRenderer":
        """Set the application configuration.
        
        Args:
            app_config: Application configuration object
            
        Returns:
            Self for method chaining
        """
        self._app_config = app_config
        return self
    
    def render(self) -> Text:
        """Render welcome message for chat mode.
        
        Returns:
            Rich Text object with welcome content
        """
        text = Text()

        # ASCII art header
        text.append("╔═══════════════════════════════════════╗\n", style=self.styles.get_style("header"))
        text.append("║        Knowledge Forge v3             ║\n", style=self.styles.get_style("header"))
        text.append("║      Plaintext Display Renderer       ║\n", style=self.styles.get_style("header"))
        text.append("╚═══════════════════════════════════════╝\n", style=self.styles.get_style("header"))

        text.append("\n🔥 Welcome to ", style="bold")
        text.append("Knowledge Forge Chat", style=self.styles.get_style("header"))
        text.append("! (v3 Plaintext Renderer)\n\n", style="bold")

        if self._app_config:
            if getattr(self._app_config, "model", None):
                text.append("🤖 Model: ", style=self.styles.get_style("info"))
                text.append(f"{self._app_config.model}\n", style=self.styles.get_style("model"))

            if getattr(self._app_config, "enabled_tools", None):
                text.append("🛠️  Tools: ", style=self.styles.get_style("info"))
                text.append(f"{', '.join(self._app_config.enabled_tools)}\n", style=self.styles.get_style("content"))

        text.append("\n💡 Type ", style="dim")
        text.append("/help", style=self.styles.get_style("success"))
        text.append(" for available commands\n", style="dim")

        return text
    
    def render_to_console(self) -> None:
        """Render welcome message directly to console.
        
        This method is provided for compatibility with the display interface.
        """
        welcome_text = self.render()
        self._console.print(welcome_text)
    
    @classmethod
    def from_app_config(cls, app_config: "AppConfig", styles: PlaintextStyles, config: PlaintextDisplayConfig, console: Console = None) -> "PlaintextWelcomeRenderer":
        """Factory method to create renderer from app config.
        
        Args:
            app_config: Application configuration object
            styles: Style manager instance
            config: Display configuration
            console: Rich console instance (optional)
            
        Returns:
            Welcome renderer configured with app config
        """
        return cls(styles, config, console).with_app_config(app_config)


# Legacy function for backward compatibility
def render_welcome(app_config: "AppConfig", styles: PlaintextStyles, config: PlaintextDisplayConfig, console: Console = None) -> None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        app_config: Application configuration object
        styles: Style manager instance
        config: Display configuration
        console: Rich console instance (optional)
    """
    renderer = PlaintextWelcomeRenderer.from_app_config(app_config, styles, config, console)
    renderer.render_to_console() 