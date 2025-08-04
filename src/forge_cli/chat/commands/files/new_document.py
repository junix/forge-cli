"""New document command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class NewDocumentCommand(ChatCommand):
    """Create a new document."""
    
    name = "new-document"
    description = "Create a new document"
    aliases = ["new-doc"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Document operations need to be extracted from original files.py")
        return True
