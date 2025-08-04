"""Show collection command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowCollectionCommand(ChatCommand):
    """Show detailed information about a specific collection.

    Usage:
    - /show-collection <collection-id> - Show collection details
    - /collection vs_123 - Short alias
    """

    name = "show-collection"
    description = "Show detailed collection information"
    aliases = ["collection", "vs-info"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /show-collection <collection-id>")
            controller.display.show_status("Example: /show-collection vs_abc123")
            return True

        collection_id = args.strip().split()[0]

        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore

            controller.display.show_status(f"🔍 Fetching collection: {collection_id}")

            collection = await async_get_vectorstore(collection_id)

            if not collection:
                controller.display.show_error(f"❌ Collection not found: {collection_id}")
                return True

            # Display collection information
            controller.display.show_status("=" * 50)
            controller.display.show_status(f"📦 Collection: {collection.name}")
            controller.display.show_status(f"🆔 ID: {collection.id}")

            if hasattr(collection, "description") and collection.description:
                controller.display.show_status(f"📄 Description: {collection.description}")

            # Handle file counts
            if hasattr(collection, "file_counts") and collection.file_counts:
                file_counts = collection.file_counts
                if hasattr(file_counts, "model_dump"):
                    counts = file_counts.model_dump()
                elif hasattr(file_counts, "dict"):
                    counts = file_counts.dict()
                else:
                    counts = {
                        "total": getattr(file_counts, "total", 0),
                        "completed": getattr(file_counts, "completed", 0),
                        "in_progress": getattr(file_counts, "in_progress", 0),
                        "failed": getattr(file_counts, "failed", 0),
                        "cancelled": getattr(file_counts, "cancelled", 0),
                    }

                controller.display.show_status("📊 File Statistics:")
                controller.display.show_status(f"  Total: {counts.get('total', 0)}")
                controller.display.show_status(f"  Completed: {counts.get('completed', 0)}")
                controller.display.show_status(f"  In Progress: {counts.get('in_progress', 0)}")
                controller.display.show_status(f"  Failed: {counts.get('failed', 0)}")
                controller.display.show_status(f"  Cancelled: {counts.get('cancelled', 0)}")

            if hasattr(collection, "created_at") and collection.created_at:
                controller.display.show_status(f"📅 Created: {collection.created_at}")

            if hasattr(collection, "bytes") and collection.bytes:
                size_mb = collection.bytes / (1024 * 1024)
                controller.display.show_status(f"💾 Size: {size_mb:.2f} MB")

            controller.display.show_status("=" * 50)

        except Exception as e:
            controller.display.show_error(f"❌ Error fetching collection: {str(e)}")

        return True
