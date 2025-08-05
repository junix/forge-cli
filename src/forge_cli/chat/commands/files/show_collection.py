"""Show collection command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..base import ChatCommand
from ..utils import has_json_flag, parse_flag_parameters

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowCollectionCommand(ChatCommand):
    """Show detailed information about a specific collection.

    Usage:
        /show-collection <collection-id>                (simple format, formatted output)
        /show-collection --id=<collection-id> --json    (flag format with JSON output)
    
    Examples:
        /show-collection vs_abc123
        /show-collection --id=vs_abc123 --json
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
            controller.display.show_error("Please provide a collection ID")
            controller.display.show_status("Usage:")
            controller.display.show_status("  /show-collection <collection-id>              (formatted output)")
            controller.display.show_status("  /show-collection --id=<collection-id> --json  (JSON output)")
            return True

        # Parse arguments
        collection_id, json_output = self._parse_args(args)

        if not collection_id:
            controller.display.show_error("Collection ID is required")
            return True

        # Show status (unless JSON output is requested)
        if not json_output:
            controller.display.show_status(f"🔍 Fetching collection: {collection_id}")

        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore

            collection = await async_get_vectorstore(collection_id)

            if not collection:
                if json_output:
                    print(json.dumps({"error": f"Collection not found: {collection_id}"}, indent=2))
                else:
                    controller.display.show_error(f"❌ Collection not found: {collection_id}")
                return True

            if json_output:
                # Output collection data as JSON
                if hasattr(collection, "model_dump"):
                    collection_data = collection.model_dump()
                elif hasattr(collection, "dict"):
                    collection_data = collection.dict()
                else:
                    # Manual serialization as fallback
                    collection_data = {
                        "id": collection.id,
                        "name": collection.name,
                        "description": getattr(collection, "description", None),
                        "created_at": str(getattr(collection, "created_at", "")),
                        "bytes": getattr(collection, "bytes", 0),
                    }
                    if hasattr(collection, "file_counts"):
                        collection_data["file_counts"] = self._serialize_file_counts(collection.file_counts)
                
                print(json.dumps(collection_data, indent=2, ensure_ascii=False))
            else:
                # Display formatted collection information
                self._display_collection_info(collection, controller)

        except Exception as e:
            error_msg = f"Error fetching collection: {str(e)}"
            if json_output:
                print(json.dumps({"error": error_msg}, indent=2))
            else:
                controller.display.show_error(f"❌ {error_msg}")

        return True

    def _parse_args(self, args: str) -> tuple[str, bool]:
        """Parse command arguments.

        Supports two formats:
        1. Simple: "collection_id" (no JSON output)
        2. Flag-based: "--id=collection_id --json"

        Args:
            args: Raw argument string

        Returns:
            Tuple of (collection_id, json_output)
        """
        args = args.strip()

        # Check if this looks like flag-based format (starts with --)
        if args.startswith("--"):
            params = parse_flag_parameters(args)
            collection_id = params.get("id", "").strip()
            json_output = has_json_flag(params)
            return collection_id, json_output
        else:
            # Simple format: just the collection ID
            collection_id = args.split()[0]
            json_output = False
            return collection_id, json_output

    def _display_collection_info(self, collection, controller: ChatController) -> None:
        """Display formatted collection information.

        Args:
            collection: Collection object from API
            controller: Chat controller for display
        """
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
                counts = self._serialize_file_counts(file_counts)

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

    def _serialize_file_counts(self, file_counts) -> dict:
        """Serialize file counts object to dictionary.

        Args:
            file_counts: File counts object

        Returns:
            Dictionary with file count data
        """
        return {
            "total": getattr(file_counts, "total", 0),
            "completed": getattr(file_counts, "completed", 0),
            "in_progress": getattr(file_counts, "in_progress", 0),
            "failed": getattr(file_counts, "failed", 0),
            "cancelled": getattr(file_counts, "cancelled", 0),
        }
