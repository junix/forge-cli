"""Utility commands for file operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class FileHelpCommand(ChatCommand):
    """Show help for file commands."""
    name = "file-help"
    description = "Show help for file commands"
    aliases = ["files-help"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 File help needs to be extracted from original files.py")
        return True


class JoinDocumentsCommand(ChatCommand):
    """Join documents to a collection."""
    name = "join-documents"
    description = "Join documents to a collection"
    aliases = ["join-docs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.display.show_status("🚧 Join documents needs to be extracted from original files.py")
        return True
