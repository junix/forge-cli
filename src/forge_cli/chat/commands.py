"""Command system for chat mode."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from .controller import ChatController


class ChatCommand(ABC):
    """Base class for chat commands."""

    name: str = ""
    description: str = ""
    aliases: List[str] = []

    @abstractmethod
    async def execute(self, args: str, controller: "ChatController") -> bool:
        """
        Execute the command.

        Args:
            args: Command arguments
            controller: Chat controller instance

        Returns:
            True to continue chat, False to exit
        """
        pass


class ExitCommand(ChatCommand):
    """Exit the chat session."""

    name = "exit"
    description = "Exit the chat"
    aliases = ["quit", "bye", "q"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Exit the chat."""
        if not controller.config.quiet:
            await controller.display.show_status("👋 Goodbye! Thanks for chatting.")
        return False


class ClearCommand(ChatCommand):
    """Clear conversation history."""

    name = "clear"
    description = "Clear conversation history"
    aliases = ["cls", "reset"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Clear the conversation."""
        controller.conversation.clear()
        await controller.display.show_status("🧹 Conversation history cleared.")
        return True


class HelpCommand(ChatCommand):
    """Show available commands."""

    name = "help"
    description = "Show this help message"
    aliases = ["h", "?"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Show help message."""
        registry = controller.commands

        lines = ["📋 Available Commands:"]
        for cmd_name, cmd in sorted(registry.commands.items()):
            if cmd.aliases:
                aliases = f", /{', /'.join(cmd.aliases)}"
            else:
                aliases = ""
            lines.append(f"  /{cmd.name}{aliases:<20} - {cmd.description}")

        help_text = "\n".join(lines)
        await controller.display.show_status(help_text)
        return True


class SaveCommand(ChatCommand):
    """Save conversation to file."""

    name = "save"
    description = "Save conversation to file"
    aliases = ["s"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Save the conversation."""
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
            await controller.display.show_status(f"💾 Conversation saved to: {path}")
        except Exception as e:
            await controller.display.show_error(f"Failed to save conversation: {e}")

        return True


class LoadCommand(ChatCommand):
    """Load conversation from file."""

    name = "load"
    description = "Load conversation from file"
    aliases = ["l"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Load a conversation."""
        from pathlib import Path

        if not args.strip():
            await controller.display.show_error("Please specify a file to load: /load <filename>")
            return True

        try:
            path = Path(args.strip())
            if not path.exists():
                # Try adding .json extension
                path = Path(args.strip() + ".json")

            if not path.exists():
                await controller.display.show_error(f"File not found: {args.strip()}")
                return True

            controller.conversation = controller.conversation.load(path)
            await controller.display.show_status(
                f"📂 Loaded conversation with {controller.conversation.get_message_count()} messages"
            )

            # Show conversation history
            if controller.conversation.messages:
                await controller.display.show_status("\n--- Conversation History ---")
                for msg in controller.conversation.messages[-5:]:  # Show last 5 messages
                    if msg.role == "user":
                        await controller.display.show_status(f"You: {msg.content[:100]}...")
                    else:
                        await controller.display.show_status(f"Assistant: {msg.content[:100]}...")

                if controller.conversation.get_message_count() > 5:
                    await controller.display.show_status(
                        f"... and {controller.conversation.get_message_count() - 5} more messages"
                    )

        except Exception as e:
            await controller.display.show_error(f"Failed to load conversation: {e}")

        return True


class HistoryCommand(ChatCommand):
    """Show conversation history."""

    name = "history"
    description = "Show conversation history"
    aliases = ["hist"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Show conversation history."""
        if not controller.conversation.messages:
            await controller.display.show_status("No conversation history yet.")
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

        await controller.display.show_status("\n".join(lines))
        return True


class ModelCommand(ChatCommand):
    """Show or change the model."""

    name = "model"
    description = "Show or change the model"
    aliases = ["m"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Show or change model."""
        if not args.strip():
            # Show current model
            await controller.display.show_status(f"🤖 Current model: {controller.config.model}")
            await controller.display.show_status(
                "Available models: qwen-max-latest, gpt-4, gpt-3.5-turbo, deepseek-chat"
            )
        else:
            # Change model
            new_model = args.strip()
            controller.config.model = new_model
            controller.conversation.model = new_model
            await controller.display.show_status(f"🤖 Model changed to: {new_model}")

        return True


class ToolsCommand(ChatCommand):
    """Show or manage tools."""

    name = "tools"
    description = "Show or manage tools"
    aliases = ["t"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Show or manage tools."""
        if not args.strip():
            # Show current tools
            if controller.config.enabled_tools:
                tools_str = ", ".join(controller.config.enabled_tools)
                await controller.display.show_status(f"🛠️ Enabled tools: {tools_str}")
            else:
                await controller.display.show_status("🛠️ No tools enabled")

            await controller.display.show_status(
                "Available tools: file-search, web-search\nUse: /tools add <tool> or /tools remove <tool>"
            )
        else:
            # Parse add/remove command
            parts = args.strip().split(maxsplit=1)
            if len(parts) < 2:
                await controller.display.show_error("Usage: /tools add|remove <tool-name>")
                return True

            action, tool_name = parts

            if action == "add":
                if tool_name not in ["file-search", "web-search"]:
                    await controller.display.show_error(f"Unknown tool: {tool_name}")
                    return True

                if tool_name not in controller.config.enabled_tools:
                    controller.config.enabled_tools.append(tool_name)
                    await controller.display.show_status(f"✅ Added tool: {tool_name}")
                else:
                    await controller.display.show_status(f"Tool already enabled: {tool_name}")

            elif action == "remove":
                if tool_name in controller.config.enabled_tools:
                    controller.config.enabled_tools.remove(tool_name)
                    await controller.display.show_status(f"❌ Removed tool: {tool_name}")
                else:
                    await controller.display.show_status(f"Tool not enabled: {tool_name}")

            else:
                await controller.display.show_error(f"Unknown action: {action}")

        return True


class NewCommand(ChatCommand):
    """Start a new conversation."""

    name = "new"
    description = "Start a new conversation"
    aliases = ["n"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Start new conversation."""
        # Save current conversation if it has messages
        if controller.conversation.messages:
            await controller.display.show_status(
                "💡 Tip: Use /save to save the current conversation before starting a new one."
            )

        # Create new conversation
        from ..models.conversation import ConversationState

        controller.conversation = ConversationState(model=controller.config.model, tools=controller.prepare_tools())

        await controller.display.show_status("🆕 Started new conversation.")
        return True


class EnableWebSearchCommand(ChatCommand):
    """Enable web search tool."""

    name = "enable-web-search"
    description = "Enable web search tool"
    aliases = ["ews"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Enable web search."""
        if "web-search" not in controller.config.enabled_tools:
            controller.config.enabled_tools.append("web-search")
            await controller.display.show_status("✅ Web search enabled")
        else:
            await controller.display.show_status("Web search is already enabled")
        return True


class DisableWebSearchCommand(ChatCommand):
    """Disable web search tool."""

    name = "disable-web-search"
    description = "Disable web search tool"
    aliases = ["dws"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Disable web search."""
        if "web-search" in controller.config.enabled_tools:
            controller.config.enabled_tools.remove("web-search")
            await controller.display.show_status("❌ Web search disabled")
        else:
            await controller.display.show_status("Web search is already disabled")
        return True


class EnableFileSearchCommand(ChatCommand):
    """Enable file search tool."""

    name = "enable-file-search"
    description = "Enable file search tool"
    aliases = ["efs"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Enable file search."""
        if "file-search" not in controller.config.enabled_tools:
            controller.config.enabled_tools.append("file-search")
            await controller.display.show_status("✅ File search enabled")
        else:
            await controller.display.show_status("File search is already enabled")
        return True


class DisableFileSearchCommand(ChatCommand):
    """Disable file search tool."""

    name = "disable-file-search"
    description = "Disable file search tool"
    aliases = ["dfs"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Disable file search."""
        if "file-search" in controller.config.enabled_tools:
            controller.config.enabled_tools.remove("file-search")
            await controller.display.show_status("❌ File search disabled")
        else:
            await controller.display.show_status("File search is already disabled")
        return True


class CommandRegistry:
    """Registry for chat commands."""

    def __init__(self):
        self.commands: Dict[str, ChatCommand] = {}
        self.aliases: Dict[str, str] = {}

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self):
        """Register all default commands."""
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
            EnableWebSearchCommand(),
            DisableWebSearchCommand(),
            EnableFileSearchCommand(),
            DisableFileSearchCommand(),
        ]

        for cmd in default_commands:
            self.register(cmd)

    def register(self, command: ChatCommand) -> None:
        """Register a command and its aliases."""
        self.commands[command.name] = command

        # Register aliases
        for alias in command.aliases:
            self.aliases[alias] = command.name

    def get_command(self, name: str) -> Optional[ChatCommand]:
        """Get command by name or alias."""
        # Direct lookup
        if name in self.commands:
            return self.commands[name]

        # Alias lookup
        if name in self.aliases:
            return self.commands[self.aliases[name]]

        return None

    def parse_command(self, input_text: str) -> tuple[Optional[str], str]:
        """
        Parse command and arguments from user input.

        Returns:
            Tuple of (command_name, arguments) or (None, original_text) if not a command
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
