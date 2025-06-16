"""Command system for chat mode."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .controller import ChatController


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
    async def execute(self, args: str, controller: "ChatController") -> bool:
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


class ExitCommand(ChatCommand):
    """Exits the chat session.

    This command terminates the current chat interaction.
    """

    name = "exit"
    description = "Exit the chat"
    aliases = ["quit", "bye", "q"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
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

    async def execute(self, args: str, controller: "ChatController") -> bool:
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

    async def execute(self, args: str, controller: "ChatController") -> bool:
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


class SaveCommand(ChatCommand):
    """Saves the current conversation to a file.

    The conversation is saved in JSON format. If no filename is provided,
    a default filename with a timestamp is used.
    """

    name = "save"
    description = "Save conversation to file"
    aliases = ["s"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the save command.

        Args:
            args: The filename to save the conversation to. If empty, a
                default filename is generated.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        from pathlib import Path

        # Determine filename
        if args.strip():
            filename = args.strip()
        else:
            # Default filename with timestamp
            import time

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{controller.conversation.session_id}_{timestamp}.json"

        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        try:
            path = Path(filename)
            controller.conversation.save(path)
            controller.display.show_status(f"💾 Conversation saved to: {path}")
        except Exception as e:
            controller.display.show_error(f"Failed to save conversation: {e}")

        return True


class LoadCommand(ChatCommand):
    """Loads a conversation from a file.

    The conversation is loaded from a JSON file. If the specified file is not
    found, it attempts to load the file with a `.json` extension.
    """

    name = "load"
    description = "Load conversation from file"
    aliases = ["l"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the load command.

        Args:
            args: The filename to load the conversation from.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        from pathlib import Path

        if not args.strip():
            controller.display.show_error("Please specify a file to load: /load <filename>")
            return True

        try:
            path = Path(args.strip())
            if not path.exists():
                # Try adding .json extension
                path = Path(args.strip() + ".json")

            if not path.exists():
                controller.display.show_error(f"File not found: {args.strip()}")
                return True

            controller.conversation = controller.conversation.load(path)
            controller.display.show_status(
                f"📂 Loaded conversation with {controller.conversation.get_message_count()} messages"
            )

            # Show conversation history
            if controller.conversation.messages:
                controller.display.show_status("\n--- Conversation History ---")
                for msg in controller.conversation.messages[-5:]:  # Show last 5 messages
                    if msg.role == "user":
                        controller.display.show_status(f"You: {msg.content[:100]}...")
                    else:
                        controller.display.show_status(f"Assistant: {msg.content[:100]}...")

                if controller.conversation.get_message_count() > 5:
                    controller.display.show_status(
                        f"... and {controller.conversation.get_message_count() - 5} more messages"
                    )

        except Exception as e:
            controller.display.show_error(f"Failed to load conversation: {e}")

        return True


class HistoryCommand(ChatCommand):
    """Shows the conversation history.

    Displays the last N messages from the current conversation.
    Defaults to showing the last 10 messages if N is not specified.
    """

    name = "history"
    description = "Show conversation history"
    aliases = ["hist"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the history command.

        Args:
            args: The number of messages to show. Defaults to 10.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        if not controller.conversation.messages:
            controller.display.show_status("No conversation history yet.")
            return True

        # Parse number of messages to show
        try:
            n = int(args.strip()) if args.strip() else 10
        except ValueError:
            n = 10

        messages = controller.conversation.get_last_n_messages(n)

        lines = [f"📜 Last {len(messages)} messages:"]
        for i, msg in enumerate(messages, 1):
            prefix = "You" if msg.role == "user" else "Assistant"
            # Truncate long messages
            content = msg.content
            if len(content) > 200:
                content = content[:197] + "..."
            lines.append(f"\n[{i}] {prefix}: {content}")

        controller.display.show_status("\n".join(lines))
        return True


class ModelCommand(ChatCommand):
    """Shows or changes the language model.

    If no arguments are provided, displays the current model and available models.
    If a model name is provided as an argument, switches to that model.
    """

    name = "model"
    description = "Show or change the model"
    aliases = ["m"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the model command.

        Args:
            args: The name of the model to switch to. If empty, displays
                current and available models.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        if not args.strip():
            # Show current model
            controller.display.show_status(f"🤖 Current model: {controller.config.model}")
            controller.display.show_status("Available models: qwen-max-latest, gpt-4, gpt-3.5-turbo, deepseek-chat")
        else:
            # Change model
            new_model = args.strip()
            controller.config.model = new_model
            controller.conversation.model = new_model
            controller.display.show_status(f"🤖 Model changed to: {new_model}")

        return True


class ToolsCommand(ChatCommand):
    """Shows or manages available tools.

    If no arguments are provided, displays the currently enabled tools and
    available tools.
    Tools can be enabled or disabled using `add` or `remove` subcommands.
    For example: `/tools add file-search` or `/tools remove web-search`.
    """

    name = "tools"
    description = "Show or manage tools"
    aliases = ["t"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the tools command.

        Args:
            args: The subcommand and tool name (e.g., "add file-search").
                If empty, displays current and available tools.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        if not args.strip():
            # Show current tools
            if controller.config.enabled_tools:
                tools_str = ", ".join(controller.config.enabled_tools)
                controller.display.show_status(f"🛠️ Enabled tools: {tools_str}")
            else:
                controller.display.show_status("🛠️ No tools enabled")

            controller.display.show_status(
                "Available tools: file-search, web-search\nUse: /tools add <tool> or /tools remove <tool>"
            )
        else:
            # Parse add/remove command
            parts = args.strip().split(maxsplit=1)
            if len(parts) < 2:
                controller.display.show_error("Usage: /tools add|remove <tool-name>")
                return True

            action, tool_name = parts

            if action == "add":
                if tool_name not in ["file-search", "web-search"]:
                    controller.display.show_error(f"Unknown tool: {tool_name}")
                    return True

                if tool_name not in controller.config.enabled_tools:
                    controller.config.enabled_tools.append(tool_name)
                    controller.display.show_status(f"✅ Added tool: {tool_name}")
                else:
                    controller.display.show_status(f"Tool already enabled: {tool_name}")

            elif action == "remove":
                if tool_name in controller.config.enabled_tools:
                    controller.config.enabled_tools.remove(tool_name)
                    controller.display.show_status(f"❌ Removed tool: {tool_name}")
                else:
                    controller.display.show_status(f"Tool not enabled: {tool_name}")

            else:
                controller.display.show_error(f"Unknown action: {action}")

        return True


class NewCommand(ChatCommand):
    """Starts a new conversation.

    This command clears the current conversation and starts a fresh one.
    It provides a tip to save the current conversation if it's not empty.
    """

    name = "new"
    description = "Start a new conversation"
    aliases = ["n"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
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
        from ..models.conversation import ConversationState

        controller.conversation = ConversationState(model=controller.config.model)

        controller.display.show_status("🆕 Started new conversation.")
        return True


class InspectCommand(ChatCommand):
    """Displays comprehensive session state information.

    Shows token usage, conversation metrics, vector store info, file usage, and model configuration.
    """

    name = "inspect"
    description = "Display comprehensive session state information"
    aliases = ["i", "status", "info"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the inspect command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        from rich.align import Align
        from rich.panel import Panel
        from rich.table import Table

        # Create main table for session information
        table = Table(title="📊 Session State Information", show_header=False, box=None)
        table.add_column("Category", style="bold cyan", width=20)
        table.add_column("Details", style="white")

        # 1. Token Usage Statistics
        usage = controller.conversation.get_token_usage()
        if usage:
            token_info = f"Input: {usage.input_tokens:,} tokens, Output: {usage.output_tokens:,} tokens, Total: {usage.total_tokens:,} tokens"
        else:
            token_info = "No token usage data available"
        table.add_row("🔢 Token Usage", token_info)

        # 2. Conversation Metrics
        turn_info = f"Turn: {controller.conversation.turn_count}"
        table.add_row("💬 Conversation", turn_info)

        # 3. Vector Store Information
        try:
            vector_store_info = await self._get_vector_store_info(controller)
        except Exception as e:
            vector_store_info = f"Error retrieving vector store info: {str(e)[:50]}..."
        table.add_row("🗂️ Vector Store", vector_store_info)

        # 4. Model Configuration
        model_info = f"Model: {controller.conversation.model}"
        table.add_row("🤖 Model", model_info)

        # 5. File Usage Tracking
        accessed_files = controller.conversation.get_accessed_files()
        if accessed_files:
            file_info = "\n".join([f"• {file}" for file in accessed_files])
        else:
            file_info = "No files accessed in this session"
        table.add_row("📁 Files Accessed", file_info)

        # Display the table in a panel
        panel = Panel(
            Align.center(table),
            title="Session Inspector",
            border_style="blue",
            padding=(1, 2),
        )

        # Use the display's renderer console if available, otherwise fallback to show_status
        if hasattr(controller.display, "_renderer") and hasattr(controller.display._renderer, "_console"):
            controller.display._renderer._console.print(panel)
        else:
            # Fallback: convert to string and use show_status
            controller.display.show_status("📊 Session State Information")
            controller.display.show_status(f"🔢 Token Usage: {token_info}")
            controller.display.show_status(f"💬 Turn: {turn_info}")
            # Handle multiline vector store info for fallback display
            vs_lines = vector_store_info.split("\n")
            if len(vs_lines) == 1:
                controller.display.show_status(f"🗂️ Vector Store: {vector_store_info}")
            else:
                controller.display.show_status("🗂️ Vector Store:")
                for line in vs_lines:
                    controller.display.show_status(f"  {line}")
            controller.display.show_status(f"🤖 Model: {model_info}")
            if accessed_files:
                controller.display.show_status(
                    f"📁 Files: {', '.join(accessed_files[:3])}{'...' if len(accessed_files) > 3 else ''}"
                )
            else:
                controller.display.show_status("📁 Files: No files accessed")

        return True

    async def _get_vector_store_info(self, controller: "ChatController") -> str:
        """Get vector store information from configuration and API.

        Args:
            controller: The ChatController instance.

        Returns:
            Formatted string with vector store information.
        """
        vec_ids = controller.config.vec_ids
        if not vec_ids:
            return "None"

        # Try to get vector store details from API, but handle errors gracefully
        vector_stores = []
        for vec_id in vec_ids:
            try:
                from ..sdk.vectorstore import async_get_vectorstore

                vs = await async_get_vectorstore(vec_id)
                if vs and hasattr(vs, "name") and vs.name:
                    vector_stores.append(f"{vec_id} - {vs.name}")
                else:
                    vector_stores.append(f"{vec_id} - Unnamed")
            except Exception as e:
                # Handle different types of errors with more specific messages
                error_msg = str(e)
                if "validation errors" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (Schema mismatch)")
                elif "method not allowed" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (API not supported)")
                elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (Connection error)")
                else:
                    vector_stores.append(f"{vec_id} - (API error)")

        return "\n".join([f"• {vs}" for vs in vector_stores])


class ToggleToolCommand(ChatCommand):
    """Generic command to enable or disable a specific tool.

    This command is used to create specific commands for enabling or disabling
    tools like "web-search" or "file-search".

    Attributes:
        tool_name (str): The internal name of the tool (e.g., "web-search").
        action (str): Either "enable" or "disable".
        tool_display_name (str): A user-friendly name for the tool.
    """

    def __init__(
        self,
        tool_name: str,
        action: str,  # "enable" or "disable"
        command_name: str,
        description: str,
        aliases: list[str],
    ):
        """Initializes the ToggleToolCommand.

        Args:
            tool_name: The internal name of the tool.
            action: "enable" or "disable".
            command_name: The name of the command (e.g., "/enable-web-search").
            description: A short description of the command.
            aliases: A list of alternative names for the command.
        """
        self.tool_name = tool_name
        self.action = action
        self.name = command_name  # From ChatCommand
        self.description = description  # From ChatCommand
        self.aliases = aliases  # From ChatCommand

        # For more descriptive messages, create a display-friendly name
        self.tool_display_name = tool_name.replace("-", " ").capitalize()

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Enables or disables the specified tool based on the `action`.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        enabled_tools = controller.config.enabled_tools

        if self.action == "enable":
            if self.tool_name not in enabled_tools:
                enabled_tools.append(self.tool_name)
                controller.display.show_status(f"✅ {self.tool_display_name} enabled")
            else:
                controller.display.show_status(f"{self.tool_display_name} is already enabled")

            # Update conversation state
            if self.tool_name == "web-search":
                controller.conversation.enable_web_search()
            elif self.tool_name == "file-search":
                controller.conversation.enable_file_search()

        elif self.action == "disable":
            if self.tool_name in enabled_tools:
                enabled_tools.remove(self.tool_name)
                controller.display.show_status(f"❌ {self.tool_display_name} disabled")
            else:
                controller.display.show_status(f"{self.tool_display_name} is already disabled")

            # Update conversation state
            if self.tool_name == "web-search":
                controller.conversation.disable_web_search()
            elif self.tool_name == "file-search":
                controller.conversation.disable_file_search()

        else:
            # Should not happen if constructor is used correctly
            controller.display.show_error(f"Invalid action '{self.action}' for {self.tool_name}")

        return True


class VectorStoreCommand(ChatCommand):
    """Manages vector store IDs for file search.

    Usage:
    - /vectorstore - Show current vector store IDs
    - /vectorstore set <id1> [id2] ... - Set vector store IDs
    - /vectorstore add <id> - Add a vector store ID
    - /vectorstore remove <id> - Remove a vector store ID
    - /vectorstore clear - Clear all vector store IDs
    """

    name = "vectorstore"
    description = "Manage vector store IDs for file search"
    aliases = ["vs", "vec"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Execute vector store management command.

        Args:
            args: Command arguments
            controller: The ChatController instance

        Returns:
            True, indicating the chat session should continue
        """
        if not args.strip():
            # Show current vector store IDs
            current_ids = controller.conversation.get_current_vector_store_ids()
            if current_ids:
                ids_str = ", ".join(current_ids)
                controller.display.show_status(f"📁 Current vector store IDs: {ids_str}")
            else:
                controller.display.show_status("📁 No vector store IDs configured")

            # Also show if file search is enabled
            if controller.conversation.is_file_search_enabled():
                controller.display.show_status("🔍 File search is enabled")
            else:
                controller.display.show_status("🔍 File search is disabled")
            return True

        parts = args.strip().split()
        action = parts[0].lower()

        if action == "set":
            if len(parts) < 2:
                controller.display.show_error("Usage: /vectorstore set <id1> [id2] ...")
                return True

            new_ids = parts[1:]
            controller.conversation.set_vector_store_ids(new_ids)
            ids_str = ", ".join(new_ids)
            controller.display.show_status(f"✅ Set vector store IDs: {ids_str}")

            # Auto-enable file search if not already enabled
            if not controller.conversation.is_file_search_enabled():
                controller.conversation.enable_file_search()
                controller.display.show_status("🔍 Auto-enabled file search")

        elif action == "add":
            if len(parts) != 2:
                controller.display.show_error("Usage: /vectorstore add <id>")
                return True

            new_id = parts[1]
            current_ids = controller.conversation.get_current_vector_store_ids()
            if new_id not in current_ids:
                current_ids.append(new_id)
                controller.conversation.set_vector_store_ids(current_ids)
                controller.display.show_status(f"✅ Added vector store ID: {new_id}")

                # Auto-enable file search if not already enabled
                if not controller.conversation.is_file_search_enabled():
                    controller.conversation.enable_file_search()
                    controller.display.show_status("🔍 Auto-enabled file search")
            else:
                controller.display.show_status(f"Vector store ID already exists: {new_id}")

        elif action == "remove":
            if len(parts) != 2:
                controller.display.show_error("Usage: /vectorstore remove <id>")
                return True

            remove_id = parts[1]
            current_ids = controller.conversation.get_current_vector_store_ids()
            if remove_id in current_ids:
                current_ids.remove(remove_id)
                controller.conversation.set_vector_store_ids(current_ids)
                controller.display.show_status(f"❌ Removed vector store ID: {remove_id}")

                # Auto-disable file search if no IDs left
                if not current_ids and controller.conversation.is_file_search_enabled():
                    controller.conversation.disable_file_search()
                    controller.display.show_status("🔍 Auto-disabled file search (no vector store IDs)")
            else:
                controller.display.show_status(f"Vector store ID not found: {remove_id}")

        elif action == "clear":
            controller.conversation.set_vector_store_ids([])
            controller.display.show_status("🗑️ Cleared all vector store IDs")

            # Auto-disable file search
            if controller.conversation.is_file_search_enabled():
                controller.conversation.disable_file_search()
                controller.display.show_status("🔍 Auto-disabled file search")

        else:
            controller.display.show_error(f"Unknown action: {action}")
            controller.display.show_status("Available actions: set, add, remove, clear")

        return True


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
        default_commands = [
            ExitCommand(),
            ClearCommand(),
            HelpCommand(),
            SaveCommand(),
            LoadCommand(),
            HistoryCommand(),
            ModelCommand(),
            ToolsCommand(),
            NewCommand(),
            InspectCommand(),
            VectorStoreCommand(),
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
