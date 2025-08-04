"""Refresh file cache command for @ file completion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class RefreshFilesCommand(ChatCommand):
    """Refresh file cache for @ file completion."""

    name = "refresh-files"
    description = "Refresh file cache for @ completion"
    aliases = ["rf", "refresh"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the refresh files command."""
        # Access the completer through the controller's input handler
        if hasattr(controller, 'input_handler') and hasattr(controller.input_handler, '_completer'):
            if controller.input_handler._completer:
                # Call the refresh method on the completer
                controller.input_handler._completer.refresh_file_cache()
                controller.display.show_status("✅ File cache refreshed. @ completion will show updated files.")
            else:
                controller.display.show_status("ℹ️  File cache will be refreshed when you next type @")
        else:
            controller.display.show_status("ℹ️  File cache will be refreshed automatically.")
        
        return True