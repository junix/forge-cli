"""Show documents command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowDocumentsCommand(ChatCommand):
    """Show all documents known to the system from conversation uploads and vector stores.

    Usage:
    - /show-documents - Show all known documents
    - /show-docs - Alias for show-documents command
    - /all-docs - Another alias
    """

    name = "show-documents"
    description = "Show all documents known to the system"
    aliases = ["show-docs", "all-docs", "all-documents"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-documents command to list all known documents.

        Args:
            args: Command arguments (unused for now)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Get conversation-level documents
        conversation_docs = controller.conversation.get_uploaded_documents()

        # Get vector store IDs from conversation state
        vector_store_ids = controller.conversation.get_current_vector_store_ids()

        # Show conversation documents
        if conversation_docs:
            controller.display.show_status(f"📄 Uploaded Documents ({len(conversation_docs)}):")
            for doc in conversation_docs:
                controller.display.show_status(f"  {doc['id']} - {doc['filename']}")

        # Show vector store documents
        if vector_store_ids:
            controller.display.show_status(f"\n📦 Vector Store Documents:")

            for vs_id in vector_store_ids:
                vs_docs = await self._get_vector_store_documents(vs_id, controller)
                if vs_docs:
                    controller.display.show_status(f"  From {vs_id}:")
                    for doc in vs_docs[:20]:  # Limit to 20 per store
                        doc_id = doc.get("file_id", doc.get("id", "unknown"))
                        filename = doc.get("filename", doc.get("name", "unnamed"))
                        controller.display.show_status(f"    {doc_id} - {filename}")
                    
                    if len(vs_docs) > 20:
                        controller.display.show_status(f"    ... and {len(vs_docs) - 20} more")

        if not conversation_docs and not vector_store_ids:
            controller.display.show_status("No documents found.")

        return True

    async def _get_vector_store_documents(self, vector_store_id: str, controller: ChatController) -> list[dict]:
        """Get documents from a vector store using a broad query.

        Args:
            vector_store_id: The vector store ID to query
            controller: The ChatController instance

        Returns:
            List of document dictionaries from the vector store
        """
        try:
            # Use direct HTTP request to avoid Pydantic parsing issues
            from forge_cli.sdk.config import BASE_URL
            from forge_cli.sdk.http_client import async_make_request
            
            url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/search"
            payload = {
                "query": "document content text information",
                "top_k": 50
            }
            
            status_code, response_data = await async_make_request("POST", url, json_payload=payload)
            
            if status_code == 200 and isinstance(response_data, dict):
                # Handle the actual response structure
                if "results" in response_data:
                    return response_data["results"]
                elif "data" in response_data:
                    return response_data["data"]
                else:
                    return []
            else:
                return []

        except Exception as e:
            # Log error but don't fail the command
            controller.display.show_status(f"    ⚠️ Error accessing vector store {vector_store_id}: {str(e)}")
            return []
