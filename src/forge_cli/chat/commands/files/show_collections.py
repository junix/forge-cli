"""Show collections command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowCollectionsCommand(ChatCommand):
    """Show information about all known collections from config and conversation state.

    Usage:
    - /show-collections - Show all known collections
    - /collections - Alias for show-collections command
    - /list-collections - Another alias
    """

    name = "show-collections"
    description = "Show information about all known collections"
    aliases = ["collections", "list-collections", "ls-collections"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collections command to list all known collections.

        Args:
            args: Command arguments (unused for now)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Get all unique collection IDs from conversation state (now authoritative)
        conversation_ids = set(controller.conversation.get_current_vector_store_ids())
        all_collection_ids = conversation_ids

        if not all_collection_ids:
            controller.display.show_status("📂 No collections configured")
            controller.display.show_status(
                "💡 Use /new-collection to create a collection or /vectorstore to configure existing ones"
            )
            return True

        controller.display.show_status(f"📚 Found {len(all_collection_ids)} collection(s):")
        controller.display.show_status("=" * 60)

        # Track collections by status
        active_collections = []
        failed_collections = []

        # Fetch information for each collection
        for collection_id in sorted(all_collection_ids):
            collection_info = await self._get_collection_info(collection_id, controller)

            if collection_info:
                active_collections.append((collection_id, collection_info, "Active"))
            else:
                failed_collections.append((collection_id, None, "Inaccessible"))

        # Display collections by category
        self._display_collection_category("🟢 Active Collections", active_collections, controller)
        self._display_collection_category("🔴 Inaccessible Collections", failed_collections, controller)

        # Summary and tips
        total_accessible = len(active_collections)
        controller.display.show_status(
            f"\n📊 Summary: {total_accessible} accessible, {len(failed_collections)} inaccessible"
        )

        if active_collections:
            controller.display.show_status("💡 Active collections are available for file search")

        controller.display.show_status("💡 Use /show-collection <id> for detailed information")
        controller.display.show_status("💡 Use /vectorstore to manage active collections")

        return True

    async def _get_collection_info(self, collection_id: str, controller: ChatController) -> dict | None:
        """Get collection information from the API.

        Args:
            collection_id: The collection ID to fetch
            controller: The ChatController instance

        Returns:
            Dictionary with collection info or None if failed
        """
        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore

            collection = await async_get_vectorstore(collection_id)
            if collection:
                # Handle file_counts properly - it's a FileCounts Pydantic model
                file_counts = getattr(collection, "file_counts", None)
                if file_counts:
                    # Convert FileCounts Pydantic model to dict
                    if hasattr(file_counts, "model_dump"):
                        # Pydantic v2
                        file_counts_dict = file_counts.model_dump()
                    elif hasattr(file_counts, "dict"):
                        # Pydantic v1
                        file_counts_dict = file_counts.dict()
                    elif isinstance(file_counts, dict):
                        # Already a dict
                        file_counts_dict = file_counts
                    else:
                        # Fallback: access as attributes (FileCounts model)
                        file_counts_dict = {
                            "total": getattr(file_counts, "total", 0),
                            "completed": getattr(file_counts, "completed", 0),
                            "in_progress": getattr(file_counts, "in_progress", 0),
                            "failed": getattr(file_counts, "failed", 0),
                            "cancelled": getattr(file_counts, "cancelled", 0),
                        }
                else:
                    file_counts_dict = {"total": 0, "completed": 0, "in_progress": 0, "failed": 0, "cancelled": 0}

                return {
                    "id": collection.id,
                    "name": getattr(collection, "name", "Unknown"),
                    "description": getattr(collection, "description", ""),
                    "file_counts": file_counts_dict,
                    "created_at": getattr(collection, "created_at", None),
                    "bytes": getattr(collection, "bytes", 0),
                }
            return None
        except Exception as e:
            # Log the error for debugging but don't fail the command
            controller.display.show_status(f"    ⚠️ Error accessing collection {collection_id}: {str(e)}")
            return None

    def _display_collection_category(self, title: str, collections: list, controller: ChatController) -> None:
        """Display a category of collections.

        Args:
            title: Category title
            collections: List of (id, info, status) tuples
            controller: The ChatController instance
        """
        if not collections:
            return

        controller.display.show_status(f"\n{title}:")

        for collection_id, info, status in collections:
            if info:
                name = info.get("name", "Unknown")
                file_counts = info.get("file_counts", {})
                total_files = file_counts.get("total", 0)
                completed_files = file_counts.get("completed", 0)

                # Format file count info
                if total_files > 0:
                    file_info = f"{completed_files}/{total_files} files"
                    if completed_files < total_files:
                        file_info += f" ({total_files - completed_files} processing)"
                else:
                    file_info = "No files"

                controller.display.show_status(f"  📦 {name} ({collection_id})")
                controller.display.show_status(f"      📊 {file_info}")

                if info.get("description"):
                    desc = info["description"][:60] + "..." if len(info["description"]) > 60 else info["description"]
                    controller.display.show_status(f"      📄 {desc}")
            else:
                controller.display.show_status(f"  ❌ {collection_id} - {status}")
