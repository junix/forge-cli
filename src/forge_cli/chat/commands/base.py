from __future__ import annotations

"""Base classes for chat commands."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controller import ChatController


class ChatCommand(ABC):
    """Abstract base class for chat commands.

    This class defines the interface for all chat commands. Each command
    must implement the `execute` method.

    Attributes:
        name (str): The primary name of the command (e.g., "help").
        description (str): A short description of what the command does.
        aliases (list[str]): A list of alternative names for the command.
    """

    name: str = ""
    description: str = ""
    aliases: list[str] = []

    @abstractmethod
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Executes the command.

        This method is called when the user issues the command. It receives the
        command arguments and a reference to the chat controller.

        Args:
            args: A string containing the arguments passed to the command.
            controller: An instance of `ChatController` to interact with the
                chat session.

        Returns:
            bool: True if the chat session should continue, False if it should exit.
        """
        pass


class CommandRegistry:
    """Manages and provides access to chat commands.

    This class holds a registry of all available chat commands,
    mapping command names and aliases to their respective `ChatCommand` objects.
    It also handles parsing user input to identify commands and arguments.

    Attributes:
        commands (dict[str, ChatCommand]): A dictionary mapping primary command
            names to `ChatCommand` instances.
        aliases (dict[str, str]): A dictionary mapping command aliases to
            primary command names.
    """

    def __init__(self):
        """Initializes the CommandRegistry and registers default commands."""
        self.commands: dict[str, ChatCommand] = {}
        self.aliases: dict[str, str] = {}

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self):
        """Registers all predefined default chat commands."""
        from .config import ModelCommand, ToolsCommand, VectorStoreCommand
        from .conversation import HistoryCommand, ListConversationsCommand, LoadCommand, SaveCommand

        # Import new commands
        from .files import (
            DeleteCollectionCommand,
            DeleteDocumentCommand,
            DocumentsCommand,
            DumpCommand,
            FileHelpCommand,
            JoinDocumentsCommand,
            NewCollectionCommand,
            NewDocumentCommand,
            ShowCollectionCommand,
            ShowDocumentCommand,
            ShowDocumentJsonCommand,
            ShowDocumentsCommand,
            ShowPagesCommand,
            UploadCommand,
            UseCollectionCommand,
        )
        from .info import InspectCommand
        from .session import ClearCommand, ExitCommand, HelpCommand, NewCommand
        from .tool import ToggleToolCommand

        default_commands = [
            ExitCommand(),
            ClearCommand(),
            HelpCommand(),
            SaveCommand(),
            LoadCommand(),
            ListConversationsCommand(),
            HistoryCommand(),
            ModelCommand(),
            ToolsCommand(),
            NewCommand(),
            InspectCommand(),
            VectorStoreCommand(),
            UploadCommand(),
            NewDocumentCommand(),
            DocumentsCommand(),
            JoinDocumentsCommand(),
            NewCollectionCommand(),
            ShowDocumentCommand(),
            ShowDocumentJsonCommand(),
            ShowDocumentsCommand(),
            ShowCollectionCommand(),
            UseCollectionCommand(),
            ShowPagesCommand(),
            DumpCommand(),
            DeleteDocumentCommand(),
            DeleteCollectionCommand(),
            FileHelpCommand(),
            # Web Search Toggle Commands
            ToggleToolCommand(
                tool_name="web-search",
                action="enable",
                command_name="enable-web-search",
                description="Enable web search tool",
                aliases=["ews"],
            ),
            ToggleToolCommand(
                tool_name="web-search",
                action="disable",
                command_name="disable-web-search",
                description="Disable web search tool",
                aliases=["dws"],
            ),
            # File Search Toggle Commands
            ToggleToolCommand(
                tool_name="file-search",
                action="enable",
                command_name="enable-file-search",
                description="Enable file search tool",
                aliases=["efs"],
            ),
            ToggleToolCommand(
                tool_name="file-search",
                action="disable",
                command_name="disable-file-search",
                description="Disable file search tool",
                aliases=["dfs"],
            ),
            # Page Reader Toggle Commands
            ToggleToolCommand(
                tool_name="page-reader",
                action="enable",
                command_name="enable-page-reader",
                description="Enable page reader tool",
                aliases=["epr"],
            ),
            ToggleToolCommand(
                tool_name="page-reader",
                action="disable",
                command_name="disable-page-reader",
                description="Disable page reader tool",
                aliases=["dpr"],
            ),
        ]

        for cmd in default_commands:
            self.register(cmd)

    def register(self, command: ChatCommand) -> None:
        """Registers a new command and its aliases.

        Args:
            command: The `ChatCommand` instance to register.
        """
        self.commands[command.name] = command

        # Register aliases
        for alias in command.aliases:
            self.aliases[alias] = command.name

    def get_command(self, name: str) -> ChatCommand | None:
        """Retrieves a command by its name or one of its aliases.

        Args:
            name: The name or alias of the command to retrieve.

        Returns:
            The `ChatCommand` instance if found, otherwise None.
        """
        # Direct lookup
        if name in self.commands:
            return self.commands[name]

        # Alias lookup
        if name in self.aliases:
            return self.commands[self.aliases[name]]

        return None

    def parse_command(self, input_text: str) -> tuple[str | None, str]:
        """Parses user input to extract a command and its arguments.

        Commands are expected to start with a forward slash `/`.
        If the input starts with `//`, it's treated as a literal message
        starting with `/`, not a command.

        Args:
            input_text: The raw text input from the user.

        Returns:
            A tuple containing:
                - The command name (str) if a command is found, otherwise None.
                - The arguments string (str) if a command is found, otherwise the
                  original input text (or the text after `//` if escaped).
        """
        if not input_text.startswith("/"):
            return None, input_text

        # Handle escape sequence
        if input_text.startswith("//"):
            return None, input_text[1:]

        # Split command and arguments
        parts = input_text[1:].split(maxsplit=1)
        if not parts:
            return None, input_text

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        return command, args
