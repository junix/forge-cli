"""Join documents command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class JoinDocumentsCommand(ChatCommand):
    """Join uploaded documents to a vector store collection.

    Usage:
    - /join-docs <vector_store_id> - Join all uploaded documents to the vector store
    - /join-docs <vector_store_id> <doc_id1> <doc_id2> ... - Join specific documents
    - /join-file <vector_store_id> <file_id> - Join a single file to the vector store
    """

    name = "join-documents"
    description = "Join uploaded documents to a vector store collection"
    aliases = ["join-docs", "join-file", "join", "add-to-collection"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the join-documents command.

        Args:
            args: Command arguments containing vector store ID and optional document IDs
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            self._show_usage(controller)
            return True

        # Parse arguments
        arg_parts = args.strip().split()
        vector_store_id = arg_parts[0]

        # Get uploaded documents from conversation state
        uploaded_docs = controller.conversation.get_uploaded_documents()

        if not uploaded_docs:
            controller.display.show_error("❌ No uploaded documents found")
            controller.display.show_status("💡 Use '/upload <file_path>' to upload documents first")
            return True

        # Determine which documents to join
        if len(arg_parts) > 1:
            # Specific document IDs provided
            requested_doc_ids = arg_parts[1:]
            documents_to_join = []

            for doc_id in requested_doc_ids:
                doc = next((d for d in uploaded_docs if d["id"] == doc_id), None)
                if doc:
                    documents_to_join.append(doc)
                else:
                    controller.display.show_error(f"❌ Document ID not found: {doc_id}")

            if not documents_to_join:
                controller.display.show_error("❌ No valid document IDs provided")
                return True
        else:
            # Join all uploaded documents
            documents_to_join = uploaded_docs

        controller.display.show_status(
            f"🔗 Joining {len(documents_to_join)} document(s) to vector store: {vector_store_id}"
        )

        try:
            # Import SDK function
            from forge_cli.sdk import async_join_files_to_vectorstore

            # Extract document IDs
            file_ids = [doc["id"] for doc in documents_to_join]

            # Join documents to vector store
            result = await async_join_files_to_vectorstore(vector_store_id=vector_store_id, file_ids=file_ids)

            if result:
                controller.display.show_status(
                    f"✅ Successfully joined {len(documents_to_join)} document(s) to vector store"
                )

                # Update conversation state to include this vector store
                current_vs_ids = controller.conversation.get_current_vector_store_ids()
                if vector_store_id not in current_vs_ids:
                    current_vs_ids.append(vector_store_id)
                    controller.conversation.set_vector_store_ids(current_vs_ids)
                    controller.display.show_status(f"📚 Vector store {vector_store_id} added to conversation")

                # Show joined documents
                for doc in documents_to_join:
                    controller.display.show_status(f"  📄 {doc.get('filename', doc['id'])} (ID: {doc['id']})")

            else:
                controller.display.show_error("❌ Failed to join documents to vector store")

        except Exception as e:
            controller.display.show_error(f"❌ Error joining documents: {str(e)}")

        return True

    def _show_usage(self, controller: ChatController) -> None:
        """Show command usage examples."""
        controller.display.show_status("📋 Usage: /join-docs <vector_store_id> [document_ids...]")
        controller.display.show_status("")
        controller.display.show_status("⚡ Basic Usage:")
        controller.display.show_status("  /join-docs <collection_id>                  # Join all documents")
        controller.display.show_status("  /join-docs <collection_id> <doc1> <doc2>    # Join specific documents")
        controller.display.show_status("  /join-file <collection_id> <file_id>        # Join single file")
        controller.display.show_status("")
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /join-docs vs_abc123                        # Join all uploaded docs")
        controller.display.show_status("  /join-docs vs_abc123 doc_123 doc_456        # Join specific documents")
        controller.display.show_status("  /join-file vs_research doc_789              # Join single file")
        controller.display.show_status("")
        controller.display.show_status("💡 Tip: Use '/documents' to see available document IDs")
