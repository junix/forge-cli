# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ._models import BaseModel

__all__ = ["ComputerTool"]


class ComputerTool(BaseModel):
    display_height: int
    """The height of the computer display."""

    display_width: int
    """The width of the computer display."""

    environment: Literal["windows", "mac", "linux", "ubuntu", "browser"]
    """The type of computer environment to control."""

    type: Literal["computer_use_preview"]
    """The type of the computer use tool. Always `computer_use_preview`."""

    @staticmethod
    def detail_description(with_arguments: bool = True, **kwargs) -> str:
        """Returns a detailed description of the computer tool.

        This method provides a comprehensive description that can be used
        in prompts, documentation, or UI elements. The description explains
        the tool's purpose, capabilities, and typical use cases.

        The computer tool enables AI to interact with computer interfaces
        through actions like clicking, typing, and taking screenshots.

        Args:
            with_arguments: If True, includes XML format argument descriptions.
                           If False, returns only the basic description.

        Returns:
            str: A detailed description of the computer tool's functionality.
                 The description follows the format "TOOL_NAME: Brief explanation
                 of what the tool does and how it can be used."
                 When with_arguments=True, also includes XML argument format.

        Example:
            >>> tool = ComputerTool(
            ...     type="computer_use_preview",
            ...     display_width=1920,
            ...     display_height=1080,
            ...     environment="windows"
            ... )
            >>> print(tool.description(with_arguments=False))
            COMPUTER_USE: Control computer interface actions
            >>> print(tool.description(with_arguments=True))
            COMPUTER_USE: Control computer interface actions
            
            Arguments:
            <action>click/type/screenshot</action>
            <coordinate>x,y</coordinate>
            <text>text to type</text>
        """
        base_description = "COMPUTER_USE: Control computer interface actions"
        
        if not with_arguments:
            return base_description
            
        return f"""{base_description}

Arguments:
<action>click/type/screenshot</action>
<coordinate>x,y</coordinate>
<text>text to type</text>"""
