"""Chat controller for managing interactive conversations."""

import asyncio
from typing import TYPE_CHECKING, Any, Final

from ..config import SearchConfig
from ..display.v3.base import Display
from ..models.conversation import ConversationState
from ..response.type_guards import (
    get_content_text,
    is_dict_with_type,
    is_message_item,
    is_output_text,
)
from ..stream.handler_typed import TypedStreamHandler
from .commands import CommandRegistry

if TYPE_CHECKING:
    from ..response._types import (
        Response,
    )


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

        # Initialize conversation state from config
        self._initialize_conversation_from_config()

        # Initialize input history for up/down arrow navigation
        self.input_history = None  # Will be initialized when prompt_toolkit is available
        self.history_file = None  # Will store the history file path

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
        """Gets input from the user.

        This method attempts to use `prompt_toolkit` for a richer input
        experience with command auto-completion if `prompt_toolkit` is installed
        and the session is interactive. Otherwise, it falls back to the
        display's `prompt_for_input` method or the basic `input()` function.

        Returns:
            The user's input as a string, or None if input fails (e.g., EOF).
            The returned string is stripped of leading/trailing whitespace.
        """
        try:
            # Try to use prompt_toolkit for better input experience
            import sys

            if sys.stdin.isatty():
                try:
                    from prompt_toolkit import PromptSession
                    from prompt_toolkit.completion import Completer, Completion
                    from prompt_toolkit.formatted_text import FormattedText
                    from prompt_toolkit.history import FileHistory
                    from prompt_toolkit.styles import Style

                    # Custom completer class for commands
                    class CommandCompleter(Completer):
                        def __init__(self, commands_dict, aliases_dict):
                            self.commands = commands_dict
                            self.aliases = aliases_dict
                            # Build list of all command names with leading slash
                            self.all_commands = []
                            for cmd in commands_dict.keys():
                                self.all_commands.append(f"/{cmd}")
                            for alias in aliases_dict.keys():
                                self.all_commands.append(f"/{alias}")
                            self.all_commands.sort()

                        def get_completions(self, document, complete_event):
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

                        def _get_description(self, cmd_with_slash):
                            # Remove leading slash
                            cmd = cmd_with_slash[1:] if cmd_with_slash.startswith("/") else cmd_with_slash

                            # Check if it's an alias
                            if cmd in self.aliases:
                                actual_cmd = self.commands[self.aliases[cmd]]
                                return f"(alias) {actual_cmd.description}"
                            elif cmd in self.commands:
                                return self.commands[cmd].description
                            return ""

                    # Create custom completer
                    completer = CommandCompleter(self.commands.commands, self.commands.aliases)

                    # Initialize input history if not already done
                    if self.input_history is None:
                        # Create history file path in user's home directory
                        import os

                        self.history_file = os.path.expanduser("~/.forge_cli_history")
                        self.input_history = FileHistory(self.history_file)

                    # Create style
                    style = Style.from_dict(
                        {
                            "prompt": "bold cyan",
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

                    # Use prompt_toolkit with auto-completion
                    loop = asyncio.get_event_loop()
                    future = loop.run_in_executor(None, lambda: session.prompt(FormattedText([("class:prompt", " ")])))
                    user_input: str = await future
                    return user_input.strip()
                except ImportError:
                    pass
                except Exception as e:
                    if self.config.debug:
                        print(f"DEBUG: prompt_toolkit error: {e}")
        except:
            pass

        # Fallback to display method or basic input
        try:
            return await self.display.prompt_for_input()  # type: ignore
        except AttributeError:
            # Basic fallback
            try:
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, input, "\nYou: ")
                user_input = await future
                return user_input.strip()
            except (EOFError, KeyboardInterrupt):
                return None

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

        # Start the display for this message (creates Live display if needed)
        # Use the Display's show_request_info method directly - it handles capability checking internally
        # The v3 Display class always has show_request_info method
        self.display.show_request_info({"question": content})

        if self.config.debug:
            print(f"\nDEBUG: Conversation has {self.conversation.get_message_count()} messages")
            print("DEBUG: Conversation history:")
            for i, msg in enumerate(self.conversation.messages):
                print(f"  [{i}] {msg.role}: {msg.content[:50]}...")

        # Create stream handler
        handler = TypedStreamHandler(self.display, debug=self.config.debug)

        # Import typed SDK
        from ..sdk import astream_typed_response

        # Stream the response
        if self.config.debug:
            print(f"DEBUG: Typed Request: {typed_request.model_dump()}")

        event_stream = astream_typed_response(typed_request, debug=self.config.debug)
        stream_state = await handler.handle_stream(event_stream, content)

        # Update conversation state from stream state
        if stream_state:
            self.conversation.update_stream_state(stream_state)

        # StreamState is a typed dataclass with a final_response attribute
        if stream_state and stream_state.final_response:
            response = stream_state.final_response
            # Extract and add the assistant's response using type guards
            # Response is a typed Pydantic model with guaranteed output attribute
            if response.output:
                assistant_added = False
                for item in response.output:
                    # Use type guard for proper message identification
                    if is_message_item(item):
                        # Type guard ensures item is ResponseOutputMessage
                        if item.content:
                            # Extract text from content
                            assistant_text = ""
                            for content_part in item.content:
                                text = self._extract_text_from_content_item(content_part)
                                if text:
                                    assistant_text += text

                            if assistant_text:
                                self.conversation.add_assistant_message(assistant_text)
                                assistant_added = True
                                if self.config.debug:
                                    print(f"DEBUG: Added assistant message: {assistant_text[:100]}...")
                                break  # Only add the first assistant message

                if self.config.debug and not assistant_added:
                    print("DEBUG: No assistant message found in response output")
                    # Response.output is guaranteed to exist as a list
                    print(
                        f"DEBUG: Response output items: {[getattr(item, 'type', 'unknown') for item in response.output]}"
                    )

            # Update conversation metadata
            # Response.model is a guaranteed attribute (ResponsesModel type)
            if response.model:
                self.conversation.model = response.model

        # Reset display mode to default after chat message
        self.display.mode = "default"

    def _extract_text_from_content_item(self, content_item: Any) -> str | None:
        """Extracts text from a single content item.

        A content item can be a string, a dictionary (e.g., `{"type": "text", "text": "..."}`),
        or a typed content part object (e.g., `ContentPart`).

        Args:
            content_item: The content item to extract text from.

        Returns:
            The extracted text as a string, or None if no text is found.
        """
        if isinstance(content_item, str):
            return content_item

        # Use type guards for proper type checking
        if is_output_text(content_item):
            return content_item.text

        # Check dict types
        if is_dict_with_type(content_item, "output_text"):
            return content_item.get("text", "")
        if is_dict_with_type(content_item, "text"):
            return content_item.get("text", "")

        # Use generic get_content_text helper
        return get_content_text(content_item)

    def extract_text_from_message(self, message_item: dict[str, Any]) -> str | None:
        """Extracts the primary text content from a message dictionary.

        A message item (typically from an API response) can have its content
        represented in various ways (string, list of content parts). This method
        iterates through possible structures to find the textual content.

        Args:
            message_item: A dictionary representing a message, usually part of
                an API response.

        Returns:
            The extracted text content as a string, or None if not found.
        """
        content = message_item.get("content", [])

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            for item_part in content:
                text = self._extract_text_from_content_item(item_part)
                if text:
                    return text
        return None

    def extract_text_from_typed_response(self, response: "Response") -> str | None:
        """Extracts the primary text content from a typed API `Response` object.

        This method navigates the structure of a `Response` object (which might
        contain multiple output items like messages or tool calls) to find and
        return the first piece of textual assistant content.

        Args:
            response: The typed `Response` object from the API.

        Returns:
            The extracted text content from the assistant's message, or None
            if not found.
        """

        # Response is a typed Pydantic model with guaranteed output attribute
        if response.output:
            for item in response.output:
                # Use type guard for proper message identification
                if is_message_item(item):
                    # Type guard ensures item is ResponseOutputMessage
                    if item.content:
                        for content_part in item.content:
                            text = self._extract_text_from_content_item(content_part)
                            if text:
                                return text
                elif isinstance(item, dict) and is_dict_with_type(item, "message"):
                    # If it's a dict-like message, use the refactored extract_text_from_message
                    text = self.extract_text_from_message(item)
                    if text:
                        return text
        return None
