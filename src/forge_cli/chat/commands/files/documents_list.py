"""Documents list command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class DocumentsCommand(ChatCommand):
    """List documents uploaded during this conversation.

    Usage:
    - /documents - List all uploaded documents
    - /docs - Alias for documents command
    """

    name = "documents"
    description = "List documents uploaded during this conversation"
    aliases = ["docs", "files"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the documents command to list uploaded documents.

        Args:
            args: Command arguments (unused for now)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        uploaded_docs = controller.conversation.get_uploaded_documents()

        if not uploaded_docs:
            controller.display.show_status("📂 No documents uploaded in this conversation yet")
            return True

        controller.display.show_status(f"📚 {len(uploaded_docs)} document(s) uploaded in this conversation:")

        for i, doc in enumerate(uploaded_docs, 1):
            # Format upload time
            try:
                from datetime import datetime

                upload_dt = datetime.fromisoformat(doc["uploaded_at"])
                time_str = upload_dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                time_str = doc.get("uploaded_at", "Unknown time")

            controller.display.show_status(f"  {i}. 📄 {doc['filename']} (ID: {doc['id']}) - {time_str}")

        controller.display.show_status("💡 Use /upload to add more documents")
        return True
