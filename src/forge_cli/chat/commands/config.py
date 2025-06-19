from __future__ import annotations

"""Configuration management commands for chat mode."""

from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


class ModelCommand(ChatCommand):
    """Shows or changes the language model.

    If no arguments are provided, displays the current model and available models.
    If a model name is provided as an argument, switches to that model.
    """

    name = "model"
    description = "Show or change the model"
    aliases = ["m"]

    async def execute(self, args: str, controller: ChatController) -> bool:
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

    async def execute(self, args: str, controller: ChatController) -> bool:
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

    async def execute(self, args: str, controller: ChatController) -> bool:
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
