"""Join documents command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class JoinDocumentsCommand(ChatCommand):
    """Join documents to a collection."""

    name = "join-documents"
    description = "Join documents to a collection"
    aliases = ["join-docs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Join documents needs to be extracted from original files.py")
        return True
