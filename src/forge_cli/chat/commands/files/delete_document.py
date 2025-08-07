"""Delete document command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand
from forge_cli.sdk.files import async_delete_file

if TYPE_CHECKING:
    from ...controller import ChatController


class DeleteDocumentCommand(ChatCommand):
    """Delete a document."""
    
    name = "del-document"
    description = "Delete a document"
    aliases = ["delete-doc", "del-doc"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the delete document command."""
        if not args.strip():
            controller.display.show_error("❌ Document ID required. Usage: /del-doc <document_id>")
            return True
        
        document_id = args.strip()
        
        try:
            controller.display.show_status(f"🗑️ Deleting document {document_id}...")
            
            # Call the SDK function to delete the file
            result = await async_delete_file(document_id)
            
            if result:
                controller.display.show_status(f"✅ Successfully deleted document {document_id}")
            else:
                controller.display.show_error(f"❌ Failed to delete document {document_id}. Document may not exist or deletion failed.")
                
        except Exception as e:
            controller.display.show_error(f"❌ Error deleting document {document_id}: {str(e)}")
        
        return True
