"""Chat controller for managing interactive conversations."""

from typing import Final

from ..config import AppConfig
from ..display.v3.base import Display
from ..models.conversation import ConversationState
from .commands import CommandRegistry
from .inputs import InputHandler

# Constants
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_OUTPUT_TOKENS: Final[int] = 2000
DEFAULT_EFFORT: Final[str] = "low"


class ChatController:
    """Manages the interactive chat session, including user input and commands.

    This class orchestrates chat input handling and command processing.
    Message processing and API communication is handled in main.py.

    Attributes:
        config (AppConfig): The configuration settings for the chat session.
        display (Display): The display handler for rendering output.
        conversation (ConversationState): The current state of the conversation,
            including messages and tool configurations.
        commands (CommandRegistry): The registry of available chat commands.
        running (bool): A flag indicating whether the chat loop is active.
            (Note: Actual loop is managed in main.py for v3).
    """

    def __init__(self, config: AppConfig, display: Display):
        """Initializes the ChatController.

        Args:
            config: The `AppConfig` object containing chat settings.
            display: The `Display` object for rendering output.
        """
        self.config = config
        self.display = display
        self.conversation = ConversationState.from_config(config)
        self.commands = CommandRegistry()
        self.running = False  # Actual loop is in main.py for v3
        self.input_handler = InputHandler(self.commands, self.conversation)

    async def start_chat_loop(self) -> None:
        """Starts the interactive chat loop.

        Note:
            This method is currently a placeholder for backward compatibility.
            The main chat loop logic has been moved to `main.py` for v3.
        """
        # This method is kept for backward compatibility
        # The actual loop is now in main.py
        pass

    def show_welcome(self) -> None:
        """Displays a welcome message to the user.

        The message includes information about the current model, session ID,
        and enabled tools. It attempts to use the display's `show_welcome`
        method if available, otherwise falls back to a default formatted message.
        """
        # Use the Display's show_welcome method - it should always be available
        self.display.show_welcome(self.config)

    async def get_user_input(self) -> str | None:
        """Gets input from the user via the input handler.

        Returns:
            The user's input as a string, or None if input fails (e.g., EOF).
        """
        return await self.input_handler.get_user_input()

    async def process_input(self, user_input: str) -> bool:
        """Processes the user's input, determining if it's a command or a message.

        If the input is recognized as a command (e.g., starts with `/`),
        it's handled by `handle_command`. Otherwise, empty messages are ignored
        and non-empty messages return True to continue the chat session.

        Args:
            user_input: The raw input string from the user.

        Returns:
            bool: True if the chat session should continue, False if a command
            (like `/exit`) signals to terminate the session.
        """
        # Parse for commands
        command_name, args = self.commands.parse_command(user_input)

        if command_name is not None:
            # Handle command
            return await self.handle_command(command_name, args)
        else:
            # Check for empty messages
            if not user_input or user_input.isspace():
                return True

            # Non-empty message - continue chat session
            return True

    async def handle_command(self, command_name: str, args: str) -> bool:
        """Executes a parsed chat command.

        Retrieves the command from the `CommandRegistry` and calls its
        `execute` method. If the command is not found, an error message
        is displayed.

        Args:
            command_name: The name of the command to execute.
            args: The arguments string for the command.

        Returns:
            bool: The result of the command's `execute` method, indicating
            whether to continue or exit the chat.
        """
        command = self.commands.get_command(command_name)

        if command is None:
            self.display.show_error(f"Unknown command: /{command_name}\nType /help to see available commands.")
            return True

        # Execute command
        return await command.execute(args, self)
