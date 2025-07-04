from __future__ import annotations

"""Chat commands module."""

from .base import ChatCommand, CommandRegistry
from .config import ModelCommand, ToolsCommand, VectorStoreCommand
from .conversation import HistoryCommand, ListConversationsCommand, LoadCommand, SaveCommand
from .info import InspectCommand
from .session import ClearCommand, ExitCommand, HelpCommand, NewCommand
from .tool import ToggleToolCommand

__all__ = [
    # Base classes
    "ChatCommand",
    "CommandRegistry",
    # Session commands
    "ExitCommand",
    "ClearCommand",
    "HelpCommand",
    "NewCommand",
    # Conversation commands
    "SaveCommand",
    "LoadCommand",
    "ListConversationsCommand",
    "HistoryCommand",
    # Configuration commands
    "ModelCommand",
    "ToolsCommand",
    "VectorStoreCommand",
    # Information commands
    "InspectCommand",
    # Tool commands
    "ToggleToolCommand",
]
