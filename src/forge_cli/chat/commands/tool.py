from __future__ import annotations

"""Tool management commands for chat mode."""

from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


class ToggleToolCommand(ChatCommand):
    """Generic command to enable or disable a specific tool.

    This command is used to create specific commands for enabling or disabling
    tools like "web-search" or "file-search".

    Attributes:
        tool_name (str): The internal name of the tool (e.g., "web-search").
        action (str): Either "enable" or "disable".
        tool_display_name (str): A user-friendly name for the tool.
    """

    def __init__(
        self,
        tool_name: str,
        action: str,  # "enable" or "disable"
        command_name: str,
        description: str,
        aliases: list[str],
    ):
        """Initializes the ToggleToolCommand.

        Args:
            tool_name: The internal name of the tool.
            action: "enable" or "disable".
            command_name: The name of the command (e.g., "/enable-web-search").
            description: A short description of the command.
            aliases: A list of alternative names for the command.
        """
        self.tool_name = tool_name
        self.action = action
        self.name = command_name  # From ChatCommand
        self.description = description  # From ChatCommand
        self.aliases = aliases  # From ChatCommand

        # For more descriptive messages, create a display-friendly name
        self.tool_display_name = tool_name.replace("-", " ").capitalize()

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Enables or disables the specified tool based on the `action`.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        enabled_tools = controller.config.enabled_tools

        if self.action == "enable":
            if self.tool_name not in enabled_tools:
                enabled_tools.append(self.tool_name)
                controller.display.show_status(f"✅ {self.tool_display_name} enabled")
            else:
                controller.display.show_status(f"{self.tool_display_name} is already enabled")

            # Update conversation state
            if self.tool_name == "web-search":
                controller.conversation.enable_web_search()
            elif self.tool_name == "file-search":
                controller.conversation.enable_file_search()
            elif self.tool_name == "page-reader":
                controller.conversation.page_reader_enabled = True

        elif self.action == "disable":
            if self.tool_name in enabled_tools:
                enabled_tools.remove(self.tool_name)
                controller.display.show_status(f"❌ {self.tool_display_name} disabled")
            else:
                controller.display.show_status(f"{self.tool_display_name} is already disabled")

            # Update conversation state
            if self.tool_name == "web-search":
                controller.conversation.disable_web_search()
            elif self.tool_name == "file-search":
                controller.conversation.disable_file_search()
            elif self.tool_name == "page-reader":
                controller.conversation.page_reader_enabled = False

        else:
            # Should not happen if constructor is used correctly
            controller.display.show_error(f"Invalid action '{self.action}' for {self.tool_name}")

        return True
