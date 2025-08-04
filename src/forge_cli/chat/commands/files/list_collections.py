"""List collections with concise ID and name only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ListCollectionsCommand(ChatCommand):
    """List collections with only ID and name (concise format).

    Usage:
    - /list-collections - Show collection IDs and names only
    - /lc - Short alias
    """

    name = "list-collections"
    description = "List collections (ID and name only)"
    aliases = ["lc", "cols-list"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the list-collections command.

        Args:
            args: Command arguments (unused)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Get collection IDs from conversation state
        collection_ids = controller.conversation.get_current_vector_store_ids()
        
        if not collection_ids:
            controller.display.show_status("No collections configured.")
            return True
        
        controller.display.show_status(f"📦 Collections ({len(collection_ids)}):")
        
        for collection_id in sorted(collection_ids):
            # Try to get collection name
            name = await self._get_collection_name(collection_id)
            if name:
                controller.display.show_status(f"  {collection_id} - {name}")
            else:
                controller.display.show_status(f"  {collection_id} - (inaccessible)")
        
        return True
    
    async def _get_collection_name(self, collection_id: str) -> str | None:
        """Get collection name from API."""
        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore
            
            collection = await async_get_vectorstore(collection_id)
            if collection:
                return getattr(collection, "name", "Unknown")
            return None
        except:
            return None