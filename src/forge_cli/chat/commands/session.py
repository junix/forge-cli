from __future__ import annotations

"""Session management commands for chat mode."""

from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


class ExitCommand(ChatCommand):
    """Exits the chat session.

    This command terminates the current chat interaction.
    """

    name = "exit"
    description = "Exit the chat"
    aliases = ["quit", "bye", "q"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Executes the exit command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            False, indicating the chat session should end.
        """
        if not controller.config.quiet:
            controller.display.show_status("👋 Goodbye! Thanks for chatting.")
        return False


class ClearCommand(ChatCommand):
    """Clears the conversation history.

    This command removes all messages from the current chat session.
    """

    name = "clear"
    description = "Clear conversation history"
    aliases = ["cls", "reset"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Executes the clear command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        controller.conversation.clear()
        controller.display.show_status("🧹 Conversation history cleared.")
        return True


class HelpCommand(ChatCommand):
    """Shows available commands.

    Displays a table of all registered commands, their aliases, and descriptions.
    """

    name = "help"
    description = "Show this help message"
    aliases = ["h", "?"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Executes the help command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        from rich.align import Align
        from rich.table import Table

        registry = controller.commands

        # Create a table for commands
        table = Table(title="📋 Available Commands", show_header=True, header_style="bold cyan")
        table.add_column("Command", style="green")
        table.add_column("Aliases", style="yellow")
        table.add_column("Description", style="white")

        # Add rows for each command
        for cmd_name, cmd in sorted(registry.commands.items()):
            command = f"/{cmd.name}"
            aliases = f"/{', /'.join(cmd.aliases)}" if cmd.aliases else ""
            description = cmd.description
            table.add_row(command, aliases, description)

        # Center-align the table
        aligned_table = Align.center(table)

        # Display the centered table
        controller.display.show_status_rich(aligned_table)
        return True


class NewCommand(ChatCommand):
    """Starts a new conversation.

    This command clears the current conversation and starts a fresh one.
    It provides a tip to save the current conversation if it's not empty.
    """

    name = "new"
    description = "Start a new conversation"
    aliases = ["n"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Executes the new command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        # Save current conversation if it has messages
        if controller.conversation.messages:
            controller.display.show_status(
                "💡 Tip: Use /save to save the current conversation before starting a new one."
            )

        # Create new conversation
        from ...models.conversation import ConversationState

        controller.conversation = ConversationState.from_config(controller.config)

        controller.display.show_status("🆕 Started new conversation.")
        return True
