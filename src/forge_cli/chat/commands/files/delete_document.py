"""Delete document command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class DeleteDocumentCommand(ChatCommand):
    """Delete a document."""
    
    name = "del-document"
    description = "Delete a document"
    aliases = ["delete-doc", "del-doc"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Document operations need to be extracted from original files.py")
        return True
