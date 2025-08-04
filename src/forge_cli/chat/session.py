from __future__ import annotations

"""Chat session management for interactive conversations."""

from typing import TYPE_CHECKING

from forge_cli.chat.controller import ChatController
from forge_cli.config import AppConfig
from forge_cli.sdk import astream_typed_response
from forge_cli.stream.handler_typed import TypedStreamHandler

if TYPE_CHECKING:
    from forge_cli.display.v3.base import Display


class ChatSessionManager:
    """Manages chat sessions including conversation flow and message processing."""

    def __init__(self, config: AppConfig, display: Display):
        """Initialize chat session manager.

        Args:
            config: AppConfig containing chat settings
            display: Display instance for rendering output
        """
        self.config = config
        self.display = display
        self.controller = ChatController(config, display)

    async def start_session(
        self, initial_question: str | None = None, resume_conversation_id: str | None = None
    ) -> None:
        """Start interactive chat session with typed API.

        Args:
            initial_question: Optional initial question to process
            resume_conversation_id: Optional conversation ID to resume
        """
        # Resume existing conversation if requested
        if resume_conversation_id:
            from forge_cli.models.conversation import ConversationState

            self.controller.conversation = ConversationState.load_by_id(resume_conversation_id)
            self.display.show_status(
                f"📂 Resumed conversation {resume_conversation_id} with {self.controller.conversation.get_message_count()} messages"
            )

        # Show welcome
        self.controller.show_welcome()

        # If initial question provided, process it first
        if initial_question:
            await self._handle_user_message(initial_question)

        # Start chat loop
        self.controller.running = True

        while self.controller.running:
            # Get user input
            user_input = await self.controller.get_user_input()

            if user_input is None:  # EOF or interrupt
                break

            # Parse for commands first
            command_name, args = self.controller.commands.parse_command(user_input)

            if command_name is not None:
                # Handle command
                continue_chat = await self.controller.handle_command(command_name, args)
                if not continue_chat:
                    break
            else:
                # Check for empty messages
                if not user_input or user_input.isspace():
                    continue

                # Handle user message
                await self._handle_user_message(user_input)

    async def _handle_user_message(self, content: str) -> None:
        """Handle user message using typed API with proper chat support.

        Args:
            content: User message content to process
        """
        # Reset display for reuse in chat mode
        if hasattr(self.display, "reset"):
            self.display.reset()

        # Increment turn count for each user message
        self.controller.conversation.increment_turn_count()

        # Create typed request with full conversation history (automatically adds user message)
        # ConversationState is now the authoritative source, no need to pass config
        request = self.controller.conversation.new_request(content)

        # Create typed handler and stream - use conversation state as authoritative source
        handler = TypedStreamHandler(self.display, debug=self.controller.conversation.debug)

        # Stream the response
        event_stream = astream_typed_response(request, debug=self.controller.conversation.debug)
        response = await handler.handle_stream(event_stream)

        # Update conversation state from response (includes adding assistant message)
        if response:
            self.controller.conversation.update_from_response(response)
