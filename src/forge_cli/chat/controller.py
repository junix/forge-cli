"""Chat controller for managing interactive conversations."""

import asyncio
from typing import Final

from ..config import SearchConfig
from ..display.v3.base import Display
from ..models.conversation import ConversationState
from ..stream.handler_typed import TypedStreamHandler
from .commands import CommandRegistry
from .inputs import InputHandler

# Constants
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_OUTPUT_TOKENS: Final[int] = 2000
DEFAULT_EFFORT: Final[str] = "low"


class ChatController:
    """Manages the interactive chat session, including user input, commands, and API communication.

    This class orchestrates the entire chat experience, handling everything
    from reading user input and parsing commands to sending requests to the
    language model and displaying responses.

    Attributes:
        config (SearchConfig): The configuration settings for the chat session.
        display (Display): The display handler for rendering output.
        conversation (ConversationState): The current state of the conversation,
            including messages and tool configurations.
        commands (CommandRegistry): The registry of available chat commands.
        running (bool): A flag indicating whether the chat loop is active.
            (Note: Actual loop is managed in main.py for v3).
    """

    def __init__(self, config: SearchConfig, display: Display):
        """Initializes the ChatController.

        Args:
            config: The `SearchConfig` object containing chat settings.
            display: The `Display` object for rendering output.
        """
        self.config = config
        self.display = display
        self.conversation = ConversationState(model=config.model)
        self.commands = CommandRegistry()
        self.running = False  # Actual loop is in main.py for v3
        self.input_handler = InputHandler(self.commands)

        # Initialize conversation state from config
        self._initialize_conversation_from_config()

    def _initialize_conversation_from_config(self) -> None:
        """Initialize conversation state from SearchConfig."""
        # Set tool enablement based on config
        if "web-search" in self.config.enabled_tools:
            self.conversation.enable_web_search()

        if "file-search" in self.config.enabled_tools:
            self.conversation.enable_file_search()

        # Set vector store IDs from config
        if self.config.vec_ids:
            self.conversation.set_vector_store_ids(self.config.vec_ids)

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
        it's handled by `handle_command`. Otherwise, it's treated as a
        message to be sent to the language model via `send_message`.
        Empty messages are not sent.

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
                # self.display.show_error("Empty messages cannot be sent. Please type something.")
                return True

            # Send as message
            await self.send_message(user_input)
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

    async def send_message(self, content: str) -> None:
        """Sends a message to the language model and handles the response.

        The user's message is added to the conversation history.
        A request is prepared using `prepare_request`, and then sent to the
        model via `astream_typed_response`. The response stream is handled by
        `TypedStreamHandler`, and the assistant's reply is added back to the
        conversation.

        Args:
            content: The text content of the user's message.
        """
        # Increment turn count for each user message
        self.conversation.increment_turn_count()

        # Show user message if display supports it
        # For v3 displays, we don't need to show user message - it's already visible in the terminal

        # Set display to chat mode - use the Display's mode property
        self.display.mode = "chat"

        # Create typed request with conversation history (automatically adds user message)
        typed_request = self.conversation.new_request(content, self.config)

        handler = TypedStreamHandler(self.display, debug=self.config.debug)

        # Import typed SDK
        from ..sdk import astream_typed_response

        # Stream the response
        if self.config.debug:
            print(f"DEBUG: Typed Request: {typed_request.model_dump()}")

        event_stream = astream_typed_response(typed_request, debug=self.config.debug)
        response = await handler.handle_stream(event_stream)

        # Update conversation state from response (includes adding assistant message)
        if response:
            self.conversation.update_from_response(response)

        # Reset display mode to default after chat message
        self.display.mode = "default"
