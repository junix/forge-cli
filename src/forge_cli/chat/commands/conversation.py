"""Conversation management commands for chat mode."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


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
            args: The filename to save the conversation to. If empty, saves
                using the conversation ID as filename.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        try:
            if args.strip():
                # Custom filename provided
                filename = args.strip()
                # Ensure .json extension
                if not filename.endswith(".json"):
                    filename += ".json"
                path = Path(filename)
                controller.conversation.save(path)
                controller.display.show_status(f"💾 Conversation saved to: {path}")
            else:
                # Use conversation ID as filename (default behavior)
                path = controller.conversation.save_by_id()
                controller.display.show_status(f"💾 Conversation saved as: {controller.conversation.conversation_id}")
                controller.display.show_status(f"📁 Location: {path}")

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
            args: The conversation ID or filename to load.
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        if not args.strip():
            controller.display.show_error("Please specify a conversation ID or filename: /load <id_or_filename>")
            return True

        try:
            arg = args.strip()

            # First try to load by conversation ID
            try:
                from ...models.conversation import ConversationState

                controller.conversation = ConversationState.load_by_id(arg)
                controller.display.show_status(
                    f"📂 Loaded conversation {arg} with {controller.conversation.get_message_count()} messages"
                )
            except FileNotFoundError:
                # If ID not found, try as filename
                path = Path(arg)
                if not path.exists():
                    # Try adding .json extension
                    path = Path(arg + ".json")

                if not path.exists():
                    controller.display.show_error(f"Conversation ID or file not found: {arg}")
                    return True

                controller.conversation = controller.conversation.load(path)
                controller.display.show_status(
                    f"📂 Loaded conversation from {path} with {controller.conversation.get_message_count()} messages"
                )

        except Exception as e:
            controller.display.show_error(f"Failed to load conversation: {e}")

        return True


class ListConversationsCommand(ChatCommand):
    """Lists all saved conversations.

    Shows conversation IDs, creation dates, message counts, and models.
    """

    name = "conversations"
    description = "List all saved conversations"
    aliases = ["convs", "list"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the list conversations command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        try:
            from ...models.conversation import ConversationState

            conversations = ConversationState.list_conversations()

            if not conversations:
                controller.display.show_status("📭 No saved conversations found")
                return True

            # Try to use rich table if available
            try:
                from rich.table import Table

                table = Table(title="💬 Saved Conversations", show_header=True)
                table.add_column("ID", style="cyan", width=12)
                table.add_column("Created", style="green", width=19)
                table.add_column("Messages", style="yellow", width=8, justify="right")
                table.add_column("Model", style="blue", width=15)

                for conv in conversations:
                    table.add_row(conv["id"], conv["created_at"], conv["message_count"], conv["model"])

                # Use the display's renderer console if available
                if hasattr(controller.display, "_renderer") and hasattr(controller.display._renderer, "_console"):
                    controller.display._renderer._console.print(table)
                else:
                    # Fallback to plain text
                    controller.display.show_status("💬 Saved Conversations:")
                    controller.display.show_status(f"{'ID':<12} {'Created':<19} {'Msgs':<8} {'Model':<15}")
                    controller.display.show_status("-" * 60)
                    for conv in conversations:
                        controller.display.show_status(
                            f"{conv['id']:<12} {conv['created_at']:<19} {conv['message_count']:<8} {conv['model']:<15}"
                        )

            except ImportError:
                # Fallback if rich is not available
                controller.display.show_status("💬 Saved Conversations:")
                controller.display.show_status(f"{'ID':<12} {'Created':<19} {'Msgs':<8} {'Model':<15}")
                controller.display.show_status("-" * 60)
                for conv in conversations:
                    controller.display.show_status(
                        f"{conv['id']:<12} {conv['created_at']:<19} {conv['message_count']:<8} {conv['model']:<15}"
                    )

            controller.display.show_status(f"\n📊 Total: {len(conversations)} conversations")
            controller.display.show_status("💡 Use '/load <id>' to resume a conversation")

        except Exception as e:
            controller.display.show_error(f"Failed to list conversations: {e}")

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

            # Extract text content from ResponseInputMessageContentList
            content_parts = []
            for content_item in msg.content:
                # Use type guards to safely extract text content
                from ...response.type_guards import is_input_text

                if is_input_text(content_item):
                    content_parts.append(content_item.text)
                elif hasattr(content_item, "type"):
                    # Handle other content types (images, files, etc.)
                    if content_item.type == "input_image":
                        content_parts.append("[Image]")
                    elif content_item.type == "input_file":
                        content_parts.append("[File]")
                    else:
                        content_parts.append(f"[{content_item.type}]")

            content = " ".join(content_parts) if content_parts else "[No text content]"

            # Truncate long messages
            if len(content) > 200:
                content = content[:197] + "..."
            lines.append(f"\n[{i}] {prefix}: {content}")

        controller.display.show_status("\n".join(lines))
        return True
