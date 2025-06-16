"""Input handling functionality for chat sessions."""

import asyncio
import sys
from typing import Optional

from .command_completer import CommandCompleter
from .commands import CommandRegistry


class InputHandler:
    """Handles user input for chat sessions with prompt_toolkit integration."""

    def __init__(self, commands: CommandRegistry):
        """Initialize input handler with command registry for completion.
        
        Args:
            commands: Command registry for auto-completion
        """
        self.commands = commands
        self.input_history = None
        self.history_file = None

    async def get_user_input(self) -> Optional[str]:
        """Gets input from the user.

        This method attempts to use `prompt_toolkit` for a richer input
        experience with command auto-completion if `prompt_toolkit` is installed
        and the session is interactive. For non-interactive sessions (pipes,
        scripts), it reads from stdin line by line.

        Returns:
            The user's input as a string, or None if input fails (e.g., EOF).
            The returned string is stripped of leading/trailing whitespace.
        """
        if sys.stdin.isatty():
            return await self._get_interactive_input()
        else:
            return await self._get_non_interactive_input()

    async def _get_interactive_input(self) -> str:
        """Get input using prompt_toolkit for interactive sessions."""
        from prompt_toolkit import PromptSession
        from prompt_toolkit.formatted_text import FormattedText
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style

        # Create custom completer
        completer = CommandCompleter(self.commands.commands, self.commands.aliases)

        # Initialize input history if not already done
        if self.input_history is None:
            import os
            self.history_file = os.path.expanduser("~/.forge_cli_history")
            self.input_history = FileHistory(self.history_file)

        # Create style
        style = Style.from_dict({
            "prompt": "bold cyan",
            "": "#ffffff",  # Default text color
        })

        # Create prompt session with custom completer and history
        session = PromptSession(
            completer=completer,
            complete_while_typing=True,
            style=style,
            complete_style="MULTI_COLUMN",  # Show completions in columns
            mouse_support=True,  # Enable mouse support
            history=self.input_history,  # Enable up/down arrow history navigation
        )

        # Use prompt_toolkit with auto-completion
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None, 
            lambda: session.prompt(FormattedText([("class:prompt", ">> ")]))
        )
        user_input: str = await future
        return user_input.strip()

    async def _get_non_interactive_input(self) -> str:
        """Get input for non-interactive sessions (pipes, scripts, etc.)."""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, input)
        user_input: str = await future
        return user_input.strip()