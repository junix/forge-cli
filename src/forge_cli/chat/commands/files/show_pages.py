"""Show pages command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowPagesCommand(ChatCommand):
    """Show pages from a document."""
    
    name = "show-pages"
    description = "Show pages from a document"
    aliases = ["pages"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Document operations need to be extracted from original files.py")
        return True
