"""Rich library display implementation."""

import asyncio
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from .base import BaseDisplay


class RichDisplay(BaseDisplay):
    """Rich library display with live updates."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.live: Live | None = None
        self.current_content = ""
        self.current_metadata: dict[str, Any] = {}

    async def show_request_info(self, info: dict[str, Any]) -> None:
        """Display request information using Rich formatting."""
        request_text = Text()
        request_text.append("\n📄 Request Information:\n", style="cyan bold")

        # Question
        if "question" in info:
            request_text.append("  💬 Question: ", style="green")
            request_text.append(f"{info['question']}\n")

        # Vector store IDs
        if "vec_ids" in info and info["vec_ids"]:
            request_text.append("  🔍 Vector Store IDs: ", style="green")
            request_text.append(f"{', '.join(info['vec_ids'])}\n")

        # Model
        if "model" in info:
            request_text.append("  🤖 Model: ", style="green")
            request_text.append(f"{info['model']}\n")

        # Effort level
        if "effort" in info:
            request_text.append("  ⚙️ Effort Level: ", style="green")
            request_text.append(f"{info['effort']}\n")

        # Tools
        if "tools" in info and info["tools"]:
            request_text.append("  🛠️ Enabled Tools: ", style="green")
            request_text.append(f"{', '.join(info['tools'])}\n")

        self.console.print(request_text)
        self.console.print(Text("\n🔄 Streaming response (please wait):", style="yellow bold"))
        self.console.print("=" * 80, style="blue")

        # Start live display
        self.live = Live(Panel(""), refresh_per_second=10, console=self.console, transient=False)
        self.live.start()

    async def update_content(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Update the live display with new content."""
        # In chat mode, if Live display isn't started, start it now
        if hasattr(self, "_in_chat_mode") and self._in_chat_mode and not self.live:
            self.live = Live(Panel(""), refresh_per_second=10, console=self.console, transient=False)
            self.live.start()

        if not self.live:
            return

        self.current_content = content
        if metadata:
            self.current_metadata = metadata

        # Create status text for title
        status_info = self._format_status_info(metadata)

        # Update panel
        try:
            panel = Panel(
                Markdown(content),
                title=status_info,
                border_style="green",
            )
            self.live.update(panel)
        except Exception:
            # Fallback to plain text if markdown fails
            panel = Panel(
                Text(content),
                title=status_info,
                border_style="green",
            )
            self.live.update(panel)

    async def show_status(self, status: str) -> None:
        """Show a status message in the live display."""
        if self.live:
            panel = Panel(Text(status, style="yellow"), title="Status", border_style="yellow")
            self.live.update(panel)
        else:
            # Print directly to console when live display is not initialized
            self.console.print(Panel(Text(status, style="yellow"), title="Status", border_style="yellow"))

    async def show_status_rich(self, rich_content) -> None:
        """Show a rich content (like Table) in the live display."""
        if self.live:
            self.live.update(rich_content)
        else:
            # Print directly to console when live display is not initialized
            self.console.print(rich_content)

    async def show_error(self, error: str) -> None:
        """Show an error message."""
        if self.live:
            error_panel = Panel(Text(f"Error: {error}", style="red bold"), title="Error", border_style="red")
            self.live.update(error_panel)
        else:
            self.console.print(Text(f"\n❌ Error: {error}", style="red bold"))

    async def finalize(self, response: dict[str, Any], state: Any) -> None:
        """Finalize the display."""
        # In chat mode, just stop the live display without re-displaying content
        if hasattr(self, "_in_chat_mode") and self.live:
            # Stop live display - the content is already visible
            self.live.stop()
            self.live = None
            # Add a small spacing for better readability
            self.console.print()

        # Stop live display if still running
        elif self.live:
            self.live.stop()
            self.live = None

        # In non-chat mode, show completion info
        if not hasattr(self, "_in_chat_mode"):
            # Show completion info
            completion_text = Text()
            completion_text.append("\n✅ Response completed successfully!\n", style="green bold")

            if response:
                if "id" in response:
                    completion_text.append("  🆔 Response ID: ", style="yellow")
                    completion_text.append(f"{response['id']}\n")

                if "model" in response:
                    completion_text.append("  🤖 Model used: ", style="yellow")
                    completion_text.append(f"{response['model']}\n")

            self.console.print(completion_text)

    def _format_status_info(self, metadata: dict[str, Any] | None) -> Text:
        """Format status information with usage statistics."""
        if not metadata:
            return Text("")

        status_info = Text()

        # Event count
        if "event_count" in metadata:
            status_info.append(f"{metadata['event_count']:05d}", style="cyan bold")
            status_info.append(" / ", style="white")

        # Event type
        if "event_type" in metadata:
            status_info.append(metadata["event_type"], style="green")
            status_info.append(" / ", style="white")

        # Usage stats
        usage = metadata.get("usage", {})
        if usage:
            status_info.append("  ↑ ", style="blue")
            status_info.append(str(usage.get("input_tokens", 0)), style="blue bold")
            status_info.append("  ↓ ", style="magenta")
            status_info.append(str(usage.get("output_tokens", 0)), style="magenta bold")
            status_info.append("  ∑ ", style="yellow")
            status_info.append(str(usage.get("total_tokens", 0)), style="yellow bold")

        # Left alignment (default)
        return status_info

    # Chat mode specific methods
    async def show_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode."""
        from ...config import SearchConfig

        if isinstance(config, SearchConfig):
            # Create a beautiful welcome panel
            welcome_text = Text()

            # ASCII art logo - using raw string to avoid escape sequence issues
            ascii_art = r"""
 _  __                    _          _              _____
| |/ /_ __   _____      _| | ___  __| | __ _  ___  |  ___|__  _ __ __ _  ___
| ' /| '_ \ / _ \ \ /\ / / |/ _ \/ _` |/ _` |/ _ \ | |_ / _ \| '__/ _` |/ _ \
| . \| | | | (_) \ V  V /| |  __/ (_| | (_| |  __/ |  _| (_) | | | (_| |  __/
|_|\_\_| |_|\___/ \_/\_/ |_|\___|\__,_|\__, |\___| |_|  \___/|_|  \__, |\___|
                                       |___/                      |___/
"""
            welcome_text.append(ascii_art, style="cyan")
            welcome_text.append("\nWelcome to ", style="bold")
            welcome_text.append("Knowledge Forge Chat", style="bold cyan")
            welcome_text.append("!\n\n", style="bold")

            welcome_text.append("Model: ", style="yellow")
            welcome_text.append(f"{config.model}\n", style="white")

            if config.enabled_tools:
                welcome_text.append("Tools: ", style="yellow")
                welcome_text.append(f"{', '.join(config.enabled_tools)}\n", style="white")

            welcome_text.append("\nType ", style="dim")
            welcome_text.append("/help", style="bold green")
            welcome_text.append(" for available commands", style="dim")

            panel = Panel(
                welcome_text,
                title="[bold cyan]Knowledge Forge Chat[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            await super().show_welcome(config)

    async def show_user_message(self, message: str) -> None:
        """Show a user message in chat mode."""
        # Don't show user message as it's already displayed by the prompt
        pass

    async def show_assistant_message(self, message: str) -> None:
        """Show an assistant message in chat mode."""
        # The assistant message is shown through update_content during streaming
        pass

    async def prompt_for_input(self) -> str | None:
        """Prompt for user input - let the controller handle prompt_toolkit."""
        # Don't use prompt_toolkit here to avoid conflicts
        # The controller will handle it if available
        try:
            # Use asyncio to run the prompt in a thread
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                None, lambda: Prompt.ask("\n[bold cyan]You[/bold cyan]", console=self.console)
            )
            user_input = await future
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return None
