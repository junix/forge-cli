from __future__ import annotations

"""Command completion for chat interface using prompt_toolkit."""

from collections.abc import Iterator
from typing import Any

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class CommandCompleter(Completer):
    """Auto-completion for chat commands.

    Provides intelligent auto-completion for chat commands and their aliases
    when using prompt_toolkit for input. Supports completion for commands
    starting with '/' and shows command descriptions as metadata.

    Attributes:
        commands: Dictionary mapping command names to command objects.
        aliases: Dictionary mapping aliases to primary command names.
        all_commands: Sorted list of all commands and aliases with '/' prefix.
    """

    def __init__(self, commands_dict: dict[str, Any], aliases_dict: dict[str, str]) -> None:
        """Initialize the command completer.

        Args:
            commands_dict: Dictionary mapping command names to command objects.
            aliases_dict: Dictionary mapping aliases to primary command names.
        """
        self.commands = commands_dict
        self.aliases = aliases_dict

        # Build list of all command names with leading slash
        self.all_commands: list[str] = []
        for cmd in commands_dict.keys():
            self.all_commands.append(f"/{cmd}")
        for alias in aliases_dict.keys():
            self.all_commands.append(f"/{alias}")
        self.all_commands.sort()

    def get_completions(self, document: Document, complete_event: Any) -> Iterator[Completion]:
        """Generate completions for the current input.

        Args:
            document: The current document state from prompt_toolkit.
            complete_event: The completion event (unused by this implementation).

        Yields:
            Completion objects for matching commands.
        """
        del complete_event  # Unused parameter required by interface
        text = document.text_before_cursor.lstrip()

        # If text starts with /, show command completions
        if text.startswith("/"):
            # Get the partial command (including the /)
            partial = text.lower()

            # Find all matching commands
            for cmd in self.all_commands:
                if cmd.lower().startswith(partial):
                    # Calculate the completion text (what to add)
                    completion_text = cmd[len(text) :]
                    yield Completion(
                        completion_text,
                        start_position=0,
                        display=cmd,  # Show full command in menu
                        display_meta=self._get_description(cmd),
                    )

        # If just typed /, show all commands
        elif text == "":
            word_before_cursor = document.get_word_before_cursor(WORD=True)
            if word_before_cursor == "/":
                for cmd in self.all_commands:
                    yield Completion(
                        cmd[1:],  # Remove the leading /
                        start_position=-1,  # Replace the /
                        display=cmd,
                        display_meta=self._get_description(cmd),
                    )

    def _get_description(self, cmd_with_slash: str) -> str:
        """Get the description for a command.

        Args:
            cmd_with_slash: Command name with leading slash.

        Returns:
            Description string for the command, or empty string if not found.
        """
        # Remove leading slash
        cmd = cmd_with_slash[1:] if cmd_with_slash.startswith("/") else cmd_with_slash

        # Check if it's an alias
        if cmd in self.aliases:
            actual_cmd = self.commands[self.aliases[cmd]]
            return f"(alias) {actual_cmd.description}"
        elif cmd in self.commands:
            return self.commands[cmd].description
        return ""
