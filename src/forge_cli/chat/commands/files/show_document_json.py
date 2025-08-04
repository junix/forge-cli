"""Show document JSON command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowDocumentJsonCommand(ChatCommand):
    """Show document information in JSON format."""
    
    name = "show-doc-json"
    description = "Show document information in JSON format"
    aliases = ["doc-json"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Document operations need to be extracted from original files.py")
        return True
