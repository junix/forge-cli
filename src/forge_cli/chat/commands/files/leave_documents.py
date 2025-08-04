"""Leave documents command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class LeaveDocumentsCommand(ChatCommand):
    """Remove documents from a vector store collection.

    Usage:
    - /left-file <vector_store_id> <file_id> - Remove a single file from the vector store
    - /leave-docs <vector_store_id> <doc_id1> <doc_id2> ... - Remove specific documents
    - /remove-from-collection <vector_store_id> <file_ids...> - Remove files from collection
    """

    name = "leave-documents"
    description = "Remove documents from a vector store collection"
    aliases = ["leave-docs", "left-file", "remove-from-collection", "remove-files"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the leave-documents command.

        Args:
            args: Command arguments containing vector store ID and document IDs
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            self._show_usage(controller)
            return True

        # Parse arguments
        arg_parts = args.strip().split()
        
        if len(arg_parts) < 2:
            controller.display.show_error("❌ Both vector store ID and file ID(s) are required")
            self._show_usage(controller)
            return True

        vector_store_id = arg_parts[0]
        file_ids_to_remove = arg_parts[1:]

        controller.display.show_status(
            f"🗑️  Removing {len(file_ids_to_remove)} file(s) from vector store: {vector_store_id}"
        )

        try:
            # Import SDK function - we'll use the modify vectorstore function with left_file_ids
            from forge_cli.sdk import async_modify_vectorstore

            # Remove files from vector store
            result = await async_modify_vectorstore(
                vector_store_id=vector_store_id, 
                left_file_ids=file_ids_to_remove
            )

            if result:
                controller.display.show_status(
                    f"✅ Successfully removed {len(file_ids_to_remove)} file(s) from vector store"
                )

                # Show removed files
                for file_id in file_ids_to_remove:
                    controller.display.show_status(f"  🗑️  Removed: {file_id}")

                # Show updated collection info
                if hasattr(result, 'metadata') and result.metadata and 'files' in result.metadata:
                    remaining_files = len(result.metadata['files'])
                    controller.display.show_status(f"📁 Remaining files in collection: {remaining_files}")

            else:
                controller.display.show_error("❌ Failed to remove files from vector store")

        except Exception as e:
            controller.display.show_error(f"❌ Error removing files: {str(e)}")

        return True

    def _show_usage(self, controller: ChatController) -> None:
        """Show command usage examples."""
        controller.display.show_status("📋 Usage: /left-file <vector_store_id> <file_id> [file_id2...]")
        controller.display.show_status("")
        controller.display.show_status("⚡ Basic Usage:")
        controller.display.show_status("  /left-file <collection_id> <file_id>        # Remove single file")
        controller.display.show_status("  /leave-docs <collection_id> <file1> <file2> # Remove multiple files")
        controller.display.show_status("  /remove-files <collection_id> <file_ids>    # Alternative alias")
        controller.display.show_status("")
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /left-file vs_abc123 doc_456                # Remove single file")
        controller.display.show_status("  /leave-docs vs_abc123 doc_123 doc_456       # Remove multiple files")
        controller.display.show_status("  /remove-from-collection vs_research doc_789 # Using alternative alias")
        controller.display.show_status("")
        controller.display.show_status("💡 Tips:")
        controller.display.show_status("  • Use '/show-collection <id>' to see files in a collection")
        controller.display.show_status("  • Use '/documents' to see available document IDs")
        controller.display.show_status("  • Removed files are not deleted, just removed from the collection")


class LeftFileCommand(ChatCommand):
    """Alias command for removing a single file from a collection.
    
    This provides a more intuitive counterpart to /join-file.
    """

    name = "left-file"
    description = "Remove a file from a vector store collection"
    aliases = ["leave-file", "remove-file"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the left-file command by delegating to LeaveDocumentsCommand."""
        # Create and execute the leave documents command
        leave_cmd = LeaveDocumentsCommand()
        return await leave_cmd.execute(args, controller)
