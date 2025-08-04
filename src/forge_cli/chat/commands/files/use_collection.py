"""Use collection command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class UseCollectionCommand(ChatCommand):
    """Add a collection to active vector stores for file search.

    Usage:
    - /use-collection <collection-id> - Add collection to active vector stores
    - /use-vs vs_123 - Short alias
    """

    name = "use-collection"
    description = "Add a collection to active vector stores for file search"
    aliases = ["use-vs", "add-collection", "add-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the use-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /use-collection <collection-id>")
            controller.display.show_status("Example: /use-collection vs_abc123")
            controller.display.show_status("This will add the collection to active vector stores for file search")
            return True

        # Parse collection ID
        collection_id = args.strip().split()[0]

        # Optional: Validate the collection exists
        controller.display.show_status(f"🔍 Checking collection: {collection_id}")

        try:
            # Import SDK function
            from forge_cli.sdk import async_get_vectorstore

            # Check if collection exists
            collection = await async_get_vectorstore(collection_id)

            if collection is None:
                controller.display.show_error(f"❌ Collection not found: {collection_id}")
                controller.display.show_status("💡 Make sure the collection ID is correct")
                controller.display.show_status("Use /vectorstore to see available collections")
                return True

            # Only modify conversation state - it's now the authoritative source
            current_vs_ids = controller.conversation.get_current_vector_store_ids()
            if collection_id not in current_vs_ids:
                current_vs_ids.append(collection_id)
                controller.conversation.set_vector_store_ids(current_vs_ids)
                controller.display.show_status(f"✅ Collection '{collection_id}' added to active vector stores")

                # Show collection info
                controller.display.show_status(f"📚 Collection: {collection.name}")
                if collection.description:
                    controller.display.show_status(f"📄 Description: {collection.description}")

                # Show current status
                controller.display.show_status(f"📊 Active collections: {len(controller.config.vec_ids)}")

                # Show helpful next steps
                if not controller.conversation.file_search_enabled:
                    controller.display.show_status("💡 Use /enable-file-search to start searching documents")
                else:
                    controller.display.show_status("✅ File search is enabled - you can now search this collection!")

            else:
                controller.display.show_status(f"ℹ️ Collection '{collection_id}' is already in active vector stores")
                current_vs_ids = controller.conversation.get_current_vector_store_ids()
                controller.display.show_status(f"📊 Active collections: {len(current_vs_ids)}")

                # Show all active collections
                if len(current_vs_ids) > 1:
                    controller.display.show_status("📚 Active collections:")
                    for idx, vs_id in enumerate(current_vs_ids, 1):
                        controller.display.show_status(f"  {idx}. {vs_id}")

        except Exception as e:
            controller.display.show_error(f"❌ Error adding collection: {str(e)}")
            controller.display.show_status("💡 Check the collection ID and server connectivity")

        return True
