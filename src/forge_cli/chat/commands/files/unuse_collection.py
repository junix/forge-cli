"""Unuse collection command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class UnuseCollectionCommand(ChatCommand):
    """Remove a collection from active vector stores for file search.

    Usage:
    - /unuse-collection <collection-id> - Remove collection from active vector stores
    - /unuse-vs vs_123 - Short alias
    """

    name = "unuse-collection"
    description = "Remove a collection from active vector stores for file search"
    aliases = ["unuse-vs", "remove-collection", "remove-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the unuse-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /unuse-collection <collection-id>")
            controller.display.show_status("Example: /unuse-collection vs_abc123")
            controller.display.show_status("This will remove the collection from active vector stores")
            return True

        # Parse collection ID
        collection_id = args.strip().split()[0]

        # Check if collection is currently in use
        if collection_id not in controller.config.vec_ids:
            controller.display.show_status(f"ℹ️ Collection '{collection_id}' is not in active vector stores")

            # Show current active collections if any
            if controller.config.vec_ids:
                controller.display.show_status("📚 Currently active collections:")
                for idx, vs_id in enumerate(controller.config.vec_ids, 1):
                    controller.display.show_status(f"  {idx}. {vs_id}")
            else:
                controller.display.show_status("📂 No collections are currently active")
                controller.display.show_status("💡 Use /use-collection to add collections")

            return True

        # Optional: Get collection info before removing (for better user feedback)
        collection_name = collection_id  # Default to ID
        try:
            from forge_cli.sdk import async_get_vectorstore

            collection = await async_get_vectorstore(collection_id)
            if collection and hasattr(collection, "name"):
                collection_name = collection.name
        except Exception:
            # If we can't get collection info, that's okay - just use the ID
            pass

        # Only modify conversation state - it's now the authoritative source
        current_vs_ids = controller.conversation.get_current_vector_store_ids()
        if collection_id in current_vs_ids:
            current_vs_ids.remove(collection_id)
            controller.conversation.set_vector_store_ids(current_vs_ids)
            controller.display.show_status(
                f"✅ Collection '{collection_name}' ({collection_id}) removed from active vector stores"
            )
        else:
            controller.display.show_status(f"ℹ️ Collection '{collection_id}' was not in active vector stores")

        # Show updated status
        remaining_count = len(current_vs_ids)
        controller.display.show_status(f"📊 Active collections: {remaining_count}")

        if remaining_count > 0:
            controller.display.show_status("📚 Remaining active collections:")
            for idx, vs_id in enumerate(current_vs_ids, 1):
                controller.display.show_status(f"  {idx}. {vs_id}")
        else:
            controller.display.show_status("📂 No collections are currently active")
            controller.display.show_status("💡 File search will not work without active collections")

            # Auto-disable file search if no collections left
            if controller.conversation.file_search_enabled:
                controller.conversation.disable_file_search()
                controller.display.show_status("🔍 Auto-disabled file search (no active collections)")

        # Show helpful next steps
        controller.display.show_status("💡 Use /show-collections to see all available collections")
        controller.display.show_status("💡 Use /use-collection <id> to add collections back")

        return True
