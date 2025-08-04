"""Delete collection command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class DeleteCollectionCommand(ChatCommand):
    """Delete a vector store collection.

    Usage:
    - /del-collection <collection-id> - Delete a collection by ID
    - /delete-vs vs_123 - Short alias
    """

    name = "del-collection"
    description = "Delete a vector store collection"
    aliases = ["delete-collection", "delete-vs", "del-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the delete-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /del-collection <collection-id>")
            controller.display.show_status("Example: /del-collection vs_abc123")
            return True

        collection_id = args.strip().split()[0]

        # Confirm deletion
        controller.display.show_status(f"⚠️ Are you sure you want to delete collection: {collection_id}?")
        controller.display.show_status("This action cannot be undone and will delete all documents in the collection.")
        controller.display.show_status("Type 'yes' to confirm or anything else to cancel:")

        # Note: In a real implementation, you'd want to get user confirmation
        # For now, we'll skip the confirmation step
        controller.display.show_status("⚠️ Deletion confirmation not implemented in CLI mode")
        controller.display.show_status("Use the web interface for safe collection deletion")

        return True
