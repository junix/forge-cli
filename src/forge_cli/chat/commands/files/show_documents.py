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

        # Track total document count
        total_docs = 0

        # Show conversation documents
        if conversation_docs:
            total_docs += len(conversation_docs)
            controller.display.show_status(f"📚 {len(conversation_docs)} document(s) uploaded in this conversation:")

            for i, doc in enumerate(conversation_docs, 1):
                # Format upload time
                try:
                    from datetime import datetime

                    upload_dt = datetime.fromisoformat(doc["uploaded_at"])
                    time_str = upload_dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, KeyError):
                    time_str = doc.get("uploaded_at", "Unknown time")

                controller.display.show_status(f"  {i}. 📄 {doc['filename']} (ID: {doc['id']}) - {time_str}")

        # Show vector store documents
        if vector_store_ids:
            controller.display.show_status(f"\n🗂️ Documents from {len(vector_store_ids)} configured vector store(s):")

            for vs_id in vector_store_ids:
                vs_docs = await self._get_vector_store_documents(vs_id, controller)
                if vs_docs:
                    total_docs += len(vs_docs)
                    controller.display.show_status(f"  📦 Vector Store {vs_id}: {len(vs_docs)} document(s)")

                    for i, doc in enumerate(vs_docs[:10], 1):  # Limit to first 10 per vector store
                        doc_id = doc.get("file_id", "Unknown ID")
                        filename = doc.get("filename", "Unknown filename")
                        score = doc.get("score", 0.0)
                        controller.display.show_status(f"    {i}. 📄 {filename} (ID: {doc_id}) - Score: {score:.2f}")

                    if len(vs_docs) > 10:
                        controller.display.show_status(f"    ... and {len(vs_docs) - 10} more documents")
                else:
                    controller.display.show_status(f"  📦 Vector Store {vs_id}: No documents found or inaccessible")

        # Summary
        if total_docs == 0:
            if not vector_store_ids:
                controller.display.show_status(
                    "📂 No documents found. Upload documents with /upload or configure vector stores with /vectorstore"
                )
            else:
                controller.display.show_status("📂 No documents found in conversation or configured vector stores")
        else:
            controller.display.show_status(f"\n📊 Total: {total_docs} document(s) across all sources")
            controller.display.show_status("💡 Use /show-doc <id> for detailed document information")

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
            from forge_cli.sdk.vectorstore import async_query_vectorstore

            # Use a broad query to get all documents
            # We use a generic query that should match most documents
            result = await async_query_vectorstore(
                vector_store_id=vector_store_id,
                query="document content text information",  # Broad query
                top_k=50,  # Get up to 50 documents
                filters=None,
            )

            if result and hasattr(result, "results"):
                return result.results
            elif result and isinstance(result, dict) and "results" in result:
                return result["results"]
            else:
                return []

        except Exception as e:
            # Log error but don't fail the command
            controller.display.show_status(f"    ⚠️ Error accessing vector store {vector_store_id}: {str(e)}")
            return []
