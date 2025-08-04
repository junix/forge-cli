"""List documents with concise ID and name only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ListDocsCommand(ChatCommand):
    """List documents with only ID and name (concise format).

    Usage:
    - /list-docs - Show document IDs and names only
    - /ld - Short alias
    """

    name = "list-docs"
    description = "List documents (ID and name only)"
    aliases = ["ld", "docs-list"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the list-docs command.

        Args:
            args: Command arguments (unused)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Get conversation-level documents
        conversation_docs = controller.conversation.get_uploaded_documents()
        
        # Get vector store IDs
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
                docs = await self._get_vector_store_docs_simple(vs_id)
                if docs:
                    controller.display.show_status(f"  From {vs_id}:")
                    for doc in docs[:20]:  # Limit to 20 per store
                        doc_id = doc.get("file_id", doc.get("id", "unknown"))
                        filename = doc.get("filename", doc.get("name", "unnamed"))
                        controller.display.show_status(f"    {doc_id} - {filename}")
                    
                    if len(docs) > 20:
                        controller.display.show_status(f"    ... and {len(docs) - 20} more")
        
        if not conversation_docs and not vector_store_ids:
            controller.display.show_status("No documents found.")
        
        return True
    
    async def _get_vector_store_docs_simple(self, vector_store_id: str) -> list[dict]:
        """Get document list from vector store."""
        try:
            from forge_cli.sdk.vectorstore import async_query_vectorstore
            
            result = await async_query_vectorstore(
                vector_store_id=vector_store_id,
                query="document",
                top_k=100
            )
            
            if result and hasattr(result, "results"):
                return result.results
            elif isinstance(result, dict) and "results" in result:
                return result["results"]
            else:
                return []
        except:
            return []