"""Welcome renderer for Rich display system."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def render_welcome(console: Console, config: Any) -> None:
    """Show welcome message for chat mode.
    
    Args:
        console: Rich console instance
        config: Configuration object with model and tools info
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
    welcome_text.append("! (v3 Rich Renderer)\n\n", style="bold")

    if getattr(config, "model", None):
        welcome_text.append("Model: ", style="yellow")
        welcome_text.append(f"{config.model}\n", style="white")

    if getattr(config, "enabled_tools", None):
        welcome_text.append("Tools: ", style="yellow")
        welcome_text.append(f"{', '.join(config.enabled_tools)}\n", style="white")

    welcome_text.append("\nType ", style="dim")
    welcome_text.append("/help", style="bold green")
    welcome_text.append(" for available commands", style="dim")

    panel = Panel(
        welcome_text,
        title="[bold cyan]Knowledge Forge Chat v3[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel) 