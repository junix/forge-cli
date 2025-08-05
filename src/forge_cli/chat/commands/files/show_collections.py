"""Show collections command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..base import ChatCommand
from ..utils import has_json_flag, parse_flag_parameters

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowCollectionsCommand(ChatCommand):
    """Show information about all known collections from config and conversation state.

    Usage:
        /show-collections           (simple format, formatted output)
        /show-collections --json    (flag format with JSON output)
    
    Examples:
        /show-collections
        /show-collections --json
    """

    name = "show-collections"
    description = "Show information about all known collections"
    aliases = ["collections", "list-collections", "ls-collections"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collections command to list all known collections.

        Args:
            args: Command arguments
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Parse arguments for JSON flag
        json_output = self._parse_args(args.strip())

        # Get all unique collection IDs from conversation state (now authoritative)
        collection_ids = controller.conversation.get_current_vector_store_ids()

        if not collection_ids:
            if json_output:
                print(json.dumps({"collections": [], "message": "No collections configured"}, indent=2))
            else:
                controller.display.show_status("No collections configured.")
            return True

        # Fetch collection details
        collections_data = []
        
        if not json_output:
            controller.display.show_status(f"📦 Collections ({len(collection_ids)}):")

        for collection_id in sorted(collection_ids):
            if json_output:
                # Get full collection info for JSON output
                info = await self._get_collection_info(collection_id, controller)
                if info:
                    collections_data.append(info)
                else:
                    collections_data.append({
                        "id": collection_id,
                        "error": "inaccessible",
                        "accessible": False
                    })
            else:
                # Get just the name for formatted output
                name = await self._get_collection_name(collection_id)
                if name:
                    controller.display.show_status(f"  {collection_id} - {name}")
                else:
                    controller.display.show_status(f"  {collection_id} - (inaccessible)")

        if json_output:
            print(json.dumps({
                "collections": collections_data,
                "total": len(collections_data)
            }, indent=2, ensure_ascii=False))

        return True

    def _parse_args(self, args: str) -> bool:
        """Parse command arguments.

        Args:
            args: Raw argument string

        Returns:
            True if --json flag is present
        """
        if not args:
            return False
        
        # Check for flag-based format
        if args.startswith("--"):
            params = parse_flag_parameters(args)
            return has_json_flag(params)
        
        return False

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
