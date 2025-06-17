"""Chat commands module."""

from .base import ChatCommand, CommandRegistry
from .session import ExitCommand, ClearCommand, HelpCommand, NewCommand
from .conversation import SaveCommand, LoadCommand, ListConversationsCommand, HistoryCommand
from .config import ModelCommand, ToolsCommand, VectorStoreCommand
from .info import InspectCommand
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
