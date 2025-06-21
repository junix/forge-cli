"""Welcome renderer for Rich display system."""

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.text import Text

from ..rendable import Rendable

if TYPE_CHECKING:
    from ....config import AppConfig


class WelcomeRenderer(Rendable):
    """Specialized renderer for welcome messages in chat mode.
    
    This class handles the rendering of welcome panels with configuration
    information like model and enabled tools.
    """
    
    def __init__(self):
        """Initialize the welcome renderer."""
        self._model = None
        self._enabled_tools = []
        self._title = "Knowledge Forge Chat v3"
        self._version_info = "(v3 Rich Renderer)"
    
    def with_model(self, model: str | None) -> "WelcomeRenderer":
        """Add model information to the welcome message.
        
        Args:
            model: The model name to display
            
        Returns:
            Self for method chaining
        """
        self._model = model
        return self
    
    def with_tools(self, tools: list[str] | None) -> "WelcomeRenderer":
        """Add enabled tools information to the welcome message.
        
        Args:
            tools: List of enabled tool names
            
        Returns:
            Self for method chaining
        """
        self._enabled_tools = tools or []
        return self
    
    def with_title(self, title: str) -> "WelcomeRenderer":
        """Set custom title for the welcome panel.
        
        Args:
            title: Custom title text
            
        Returns:
            Self for method chaining
        """
        self._title = title
        return self
    
    def with_version_info(self, version_info: str) -> "WelcomeRenderer":
        """Set version information display.
        
        Args:
            version_info: Version information text
            
        Returns:
            Self for method chaining
        """
        self._version_info = version_info
        return self
    
    def render(self) -> Panel:
        """Build and return the welcome panel.
        
        Returns:
            Rich Panel object ready for display
        """
        welcome_text = Text()

        # ASCII art logo
        ascii_art = r"""
  ____            _            _      _____             _
 / ___|___  _ __ | |_ _____  _| |_   | ____|_ __   __ _(_)_ __   ___
| |   / _ \| '_ \| __/ _ \ \/ / __|  |  _| | '_ \ / _` | | '_ \ / _ \
| |__| (_) | | | | ||  __/>  <| |_   | |___| | | | (_| | | | | |  __/
 \____\___/|_| |_|\__\___/_/\_\\__|  |_____|_| |_|\__, |_|_| |_|\___|
                                                  |___/

"""
        welcome_text.append(ascii_art, style="cyan")
        welcome_text.append("\nWelcome to ", style="bold")
        welcome_text.append("Knowledge Forge Chat", style="bold cyan")
        welcome_text.append(f"! {self._version_info}\n\n", style="bold")

        # Add model information if available
        if self._model:
            welcome_text.append("Model: ", style="yellow")
            welcome_text.append(f"{self._model}\n", style="white")

        # Add tools information if available
        if self._enabled_tools:
            welcome_text.append("Tools: ", style="yellow")
            welcome_text.append(f"{', '.join(self._enabled_tools)}\n", style="white")

        welcome_text.append("\nType ", style="dim")
        welcome_text.append("/help", style="bold green")
        welcome_text.append(" for available commands", style="dim")

        return Panel(
            welcome_text,
            title=f"[bold cyan]{self._title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    
    @classmethod
    def from_config(cls, config: "AppConfig") -> "WelcomeRenderer":
        """Create a welcome renderer from a configuration object.
        
        Args:
            config: AppConfig instance with model and tools info
            
        Returns:
            WelcomeRenderer instance configured with the config data
        """
        renderer = cls()
        
        # Extract model information
        if hasattr(config, 'model') and config.model:
            model = getattr(config, 'model', None)
            # Check if it's a real value, not a Mock object
            if model and isinstance(model, str):
                renderer.with_model(model)
        
        # Extract tools information - ensure it's a real list
        if hasattr(config, 'enabled_tools') and config.enabled_tools:
            tools = getattr(config, 'enabled_tools', None)
            # Check if it's a real list, not a Mock object
            if tools and isinstance(tools, list) and all(isinstance(tool, str) for tool in tools):
                renderer.with_tools(tools)
        
        return renderer


# Legacy function for backward compatibility
def render_welcome(console, config: "AppConfig") -> None:
    """Legacy function for backward compatibility.
    
    Creates a welcome renderer and prints it to the console.
    
    Args:
        console: Rich console instance
        config: AppConfig instance with model and tools info
    """
    renderer = WelcomeRenderer.from_config(config)
    console.print(renderer.render()) 