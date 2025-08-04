from __future__ import annotations

"""Input handling functionality for chat sessions."""

import asyncio
import sys

from ..display.v3.style import ICONS
from ..models.conversation import ConversationState
from .command_completer import CommandCompleter
from .commands import CommandRegistry


class InputHandler:
    """Handles user input for chat sessions with prompt_toolkit integration."""

    def __init__(self, commands: CommandRegistry, conversation: ConversationState):
        """Initialize input handler with command registry for completion.

        Args:
            commands: Command registry for auto-completion
            conversation: Conversation state to check enabled tools
        """
        self.commands = commands
        self.conversation = conversation
        self.input_history = None
        self.history_file = None

    async def get_user_input(self) -> str | None:
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

        # Create custom completer with conversation for file completion
        completer = CommandCompleter(self.commands.commands, self.commands.aliases, self.conversation)

        # Initialize input history if not already done
        if self.input_history is None:
            import os

            self.history_file = os.path.expanduser("~/.forge_cli_history")
            self.input_history = FileHistory(self.history_file)

        # Create style with tool colors
        style = Style.from_dict(
            {
                "prompt": "bold cyan",
                "tool_web": "bold green",
                "tool_file": "bold yellow",
                "tool_bracket": "bold white",
                "": "#ffffff",  # Default text color
            }
        )

        # Create prompt session with custom completer and history
        session = PromptSession(
            completer=completer,
            complete_while_typing=True,
            style=style,
            complete_style="MULTI_COLUMN",  # Show completions in columns
            mouse_support=True,  # Enable mouse support
            history=self.input_history,  # Enable up/down arrow history navigation
        )

        # Build dynamic prompt with tool icons
        prompt_parts = []

        # Add tool indicators with colors
        tools_enabled = []
        if self.conversation.web_search_enabled:
            tools_enabled.append(("class:tool_web", ICONS["web_search_call"].strip()))
        if self.conversation.file_search_enabled:
            tools_enabled.append(("class:tool_file", ICONS["file_search_call"].strip()))

        # Build prompt with styled icons
        if tools_enabled:
            # prompt_parts.append(("class:tool_bracket", "["))
            for i, (style_class, icon) in enumerate(tools_enabled):
                if i > 0:
                    prompt_parts.append(("class:tool_bracket", " "))
                prompt_parts.append((style_class, icon))
            # prompt_parts.append(("class:tool_bracket", "] "))

        prompt_parts.append(("class:prompt", "  "))

        # Use prompt_toolkit with auto-completion
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, lambda: session.prompt(FormattedText(prompt_parts)))
        user_input: str = await future
        return user_input.strip()

    async def _get_non_interactive_input(self) -> str:
        """Get input for non-interactive sessions (pipes, scripts, etc.)."""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, input)
        user_input: str = await future
        return user_input.strip()

    async def _populate_file_cache(self, completer) -> None:
        """Pre-populate the file cache for better completion performance.

        Args:
            completer: The CommandCompleter instance to populate
        """
        if not self.conversation:
            return

        try:
            files = []

            # Get uploaded documents (synchronous)
            uploaded_docs = self.conversation.get_uploaded_documents()
            files.extend(uploaded_docs)

            # For vector stores, we'll use a simpler approach
            # Try to get files from vector stores, but don't fail if it doesn't work
            vector_store_ids = self.conversation.get_current_vector_store_ids()
            if vector_store_ids:
                # Try to get files from the first vector store as a sample
                try:
                    vs_files = await completer._get_vector_store_files_async(vector_store_ids[0])
                    files.extend(vs_files)
                except Exception:
                    # If vector store query fails, add a placeholder to indicate files are available
                    files.append(
                        {
                            "id": "vs_files_hint",
                            "filename": f"📦 Use /show-documents to see {len(vector_store_ids)} vector store file(s)",
                        }
                    )

            # Cache the results
            completer._file_cache = files

        except Exception:
            # If anything fails, just continue without cache
            pass
