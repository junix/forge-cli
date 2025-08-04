"""Show document command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowDocumentCommand(ChatCommand):
    """Show detailed information about a specific document."""
    
    name = "show-doc"
    description = "Show detailed document information"
    aliases = ["doc", "document"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Document operations need to be extracted from original files.py")
        return True
