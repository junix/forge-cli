"""Chat controller for managing interactive conversations."""

import asyncio

from ..config import SearchConfig
from ..display.v3.base import Display
from ..models.conversation import ConversationState
from ..stream.handler_typed import TypedStreamHandler
from .commands import CommandRegistry


class ChatController:
    """Controls the chat interaction flow."""

    def __init__(self, config: SearchConfig, display: Display):
        self.config = config
        self.display = display
        self.conversation = ConversationState(model=config.model, tools=self.prepare_tools())
        self.commands = CommandRegistry()
        self.running = False

    def prepare_tools(self) -> list[dict[str, str | bool | list[str]]]:
        """Prepare tools configuration based on config."""
        tools = []

        # File search tool
        if "file-search" in self.config.enabled_tools and self.config.vec_ids:
            tools.append(
                {
                    "type": "file_search",
                    "vector_store_ids": self.config.vec_ids,
                    "max_num_results": self.config.max_results,
                }
            )

        # Web search tool
        if "web-search" in self.config.enabled_tools:
            web_tool = {"type": "web_search"}

            # Add location if provided
            location = self.config.get_web_location()
            if location:
                web_tool["user_location"] = {"type": "approximate", **location}

            tools.append(web_tool)

        return tools

    def prepare_typed_tools(self) -> list:
        """Prepare typed tools configuration based on config."""
        from ..response._types import FileSearchTool, WebSearchTool

        tools = []

        # File search tool
        if "file-search" in self.config.enabled_tools and self.config.vec_ids:
            tools.append(
                FileSearchTool(
                    type="file_search",
                    vector_store_ids=self.config.vec_ids,
                    max_num_results=self.config.max_results,
                )
            )

        # Web search tool
        if "web-search" in self.config.enabled_tools:
            tool_params = {"type": "web_search"}
            location = self.config.get_web_location()
            if location:
                if "country" in location:
                    tool_params["country"] = location["country"]
                if "city" in location:
                    tool_params["city"] = location["city"]
            tools.append(WebSearchTool(**tool_params))

        return tools

    async def start_chat_loop(self) -> None:
        """Start the interactive chat loop."""
        # This method is kept for backward compatibility
        # The actual loop is now in main.py
        pass

    def show_welcome(self) -> None:
        """Show welcome message and chat info."""
        if hasattr(self.display, "show_welcome"):
            self.display.show_welcome(self.config)
        else:
            # Fallback welcome message
            lines = [
                "╭─ Knowledge Forge Chat ─────────────────────────────────────╮",
                f"│ Model: {self.config.model:<20} Session: {self.conversation.session_id} │",
            ]

            if self.config.enabled_tools:
                tools_str = ", ".join(self.config.enabled_tools)
                lines.append(f"│ Tools: {tools_str:<49} │")

            lines.append("╰─────────────────────────────────────────────────────────────╯")
            lines.append("\nWelcome to Knowledge Forge Chat! Type /help for commands.")

            self.display.show_status("\n".join(lines))

    async def get_user_input(self) -> str | None:
        """Get input from the user with prompt_toolkit support for auto-completion."""
        try:
            # Try to use prompt_toolkit for better input experience
            import sys

            if sys.stdin.isatty():
                try:
                    from prompt_toolkit import PromptSession
                    from prompt_toolkit.completion import Completer, Completion
                    from prompt_toolkit.formatted_text import FormattedText
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

                    # Create style
                    style = Style.from_dict(
                        {
                            "prompt": "bold cyan",
                            "": "#ffffff",  # Default text color
                        }
                    )

                    # Create prompt session with custom completer
                    session = PromptSession(
                        completer=completer,
                        complete_while_typing=True,
                        style=style,
                        complete_style="MULTI_COLUMN",  # Show completions in columns
                        mouse_support=True,  # Enable mouse support
                    )

                    # Use prompt_toolkit with auto-completion
                    loop = asyncio.get_event_loop()
                    future = loop.run_in_executor(None, lambda: session.prompt(FormattedText([("class:prompt", " ")])))
                    user_input = await future
                    return user_input.strip()
                except ImportError:
                    pass
                except Exception as e:
                    if self.config.debug:
                        print(f"DEBUG: prompt_toolkit error: {e}")
        except:
            pass

        # Fallback to display method or basic input
        if hasattr(self.display, "prompt_for_input"):
            return await self.display.prompt_for_input()
        else:
            # Basic fallback
            try:
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, input, "\nYou: ")
                user_input = await future
                return user_input.strip()
            except (EOFError, KeyboardInterrupt):
                return None

    async def process_input(self, user_input: str) -> bool:
        """
        Process user input - either as command or message.

        Returns:
            True to continue chat, False to exit
        """
        # Parse for commands
        command_name, args = self.commands.parse_command(user_input)

        if command_name is not None:
            # Handle command
            return await self.handle_command(command_name, args)
        else:
            # Check for empty messages
            if not user_input or user_input.isspace():
                self.display.show_error("Empty messages cannot be sent. Please type something.")
                return True

            # Send as message
            await self.send_message(user_input)
            return True

    async def handle_command(self, command_name: str, args: str) -> bool:
        """
        Handle a chat command.

        Returns:
            True to continue chat, False to exit
        """
        command = self.commands.get_command(command_name)

        if command is None:
            self.display.show_error(f"Unknown command: /{command_name}\nType /help to see available commands.")
            return True

        # Execute command
        return await command.execute(args, self)

    async def send_message(self, content: str) -> None:
        """Send a message and get response."""
        # Add user message to conversation
        user_message = self.conversation.add_user_message(content)

        # Show user message if display supports it
        # For v3 displays, we don't need to show user message - it's already visible in the terminal

        # Mark display as in chat mode
        if hasattr(self.display, "console"):
            self.display._in_chat_mode = True

        # Prepare request with conversation history
        request = self.prepare_request()

        # Start the display for this message (creates Live display if needed)
        if hasattr(self.display, "show_request_info"):
            # Don't show full request info in chat mode, just ensure display is ready
            self.display.handle_event("stream_start", {"query": content})

        if self.config.debug:
            print(f"\nDEBUG: Conversation has {self.conversation.get_message_count()} messages")
            print("DEBUG: Conversation history:")
            for i, msg in enumerate(self.conversation.messages):
                print(f"  [{i}] {msg.role}: {msg.content[:50]}...")

        # Create stream handler
        handler = TypedStreamHandler(self.display, debug=self.config.debug)

        # Store the final formatted content
        final_content = None

        try:
            # Import typed SDK
            from ..response._types import InputMessage, Request
            from ..sdk import astream_typed_response

            # Convert dict request to typed Request
            input_messages = []
            if isinstance(request.get("input_messages"), list):
                for msg in request["input_messages"]:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        input_messages.append(InputMessage(role=msg["role"], content=msg["content"]))
            elif isinstance(request.get("input_messages"), str):
                input_messages = [InputMessage(role="user", content=request["input_messages"])]

            # Use typed tools
            typed_tools = self.prepare_typed_tools()

            typed_request = Request(
                input=input_messages,
                model=request.get("model", "qwen-max"),
                tools=typed_tools,
                temperature=request.get("temperature", 0.7),
                max_output_tokens=request.get("max_output_tokens", 2000),
                effort=request.get("effort", "low"),
            )

            # Stream the response
            if self.config.debug:
                print(f"DEBUG: Typed Request: {typed_request.model_dump()}")

            event_stream = astream_typed_response(typed_request, debug=self.config.debug)
            response = await handler.handle_stream(event_stream, content)

            if response:
                # Extract and add the assistant's response
                if "output" in response:
                    # The API returns the assistant's response in the output array
                    # We need to add all message items from the output
                    assistant_added = False
                    for item in response.get("output", []):
                        if item.get("type") == "message" and item.get("role") == "assistant":
                            # Extract the text content
                            assistant_text = self.extract_text_from_message(item)
                            if assistant_text:
                                self.conversation.add_assistant_message(assistant_text)
                                assistant_added = True
                                if self.config.debug:
                                    print(f"DEBUG: Added assistant message: {assistant_text[:100]}...")
                                break  # Only add the first assistant message

                    if self.config.debug and not assistant_added:
                        print("DEBUG: No assistant message found in response output")
                        print(
                            f"DEBUG: Response output items: {[item.get('type') for item in response.get('output', [])]}"
                        )

                # Update conversation metadata
                if "model" in response:
                    self.conversation.model = response["model"]

        except Exception as e:
            self.display.show_error(f"Failed to get response: {str(e)}")
            if self.config.debug:
                import traceback

                traceback.print_exc()
        finally:
            # Unmark chat mode
            if hasattr(self.display, "_in_chat_mode"):
                delattr(self.display, "_in_chat_mode")

    def prepare_request(self) -> dict[str, str | int | float | bool | list]:
        """Prepare API request with conversation history."""
        # Update tools in case they changed
        self.conversation.tools = self.prepare_tools()

        # The SDK expects "input_messages"
        request = {
            "input_messages": self.conversation.to_api_format(),
            "model": self.config.model,
            "effort": self.config.effort,
            "store": True,
            "debug": self.config.debug,
        }

        # Add tools if any
        if self.conversation.tools:
            request["tools"] = self.conversation.tools

        return request

    def extract_text_from_message(self, message_item: dict[str, str | int | float | bool | list | dict]) -> str | None:
        """Extract text content from a message item."""
        # Handle different content formats
        content = message_item.get("content", [])

        # If content is a string, return it directly
        if isinstance(content, str):
            return content

        # If content is a list, look for text items
        if isinstance(content, list):
            for content_item in content:
                if isinstance(content_item, dict):
                    # Look for output_text type
                    if content_item.get("type") == "output_text":
                        return content_item.get("text", "")
                    # Also check for plain text type
                    elif content_item.get("type") == "text":
                        return content_item.get("text", "")
                elif isinstance(content_item, str):
                    # If content item is just a string
                    return content_item

        return None

    def extract_text_from_typed_response(self, response: "Response") -> str | None:
        """Extract text content from a typed response object."""
        from ..response._types import ResponseOutputMessage

        # Check if response has output attribute
        if hasattr(response, "output") and response.output:
            for item in response.output:
                # Check if it's a message type
                if hasattr(item, "type") and item.type == "message":
                    # For typed ResponseOutputMessage
                    if isinstance(item, ResponseOutputMessage):
                        if hasattr(item, "content") and item.content:
                            # Extract text from content
                            for content_item in item.content:
                                if hasattr(content_item, "type") and content_item.type == "text":
                                    if hasattr(content_item, "text"):
                                        return content_item.text
                    # For dict-like message
                    elif isinstance(item, dict):
                        return self.extract_text_from_message(item)

        return None
