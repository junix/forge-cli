"""File operation commands for chat mode.

This module contains all file and document related commands organized into sub-modules:
- upload: File upload operations
- documents: Document listing and management
- document_ops: Individual document operations (show, delete, dump)
- collection_ops: Collection management operations
- utils: Utility commands (help, join, pages)
"""

from .collection_ops import (
    DeleteCollectionCommand,
    NewCollectionCommand,
    ShowCollectionCommand,
    ShowCollectionsCommand,
    UnuseCollectionCommand,
    UseCollectionCommand,
)
from .document_ops import (
    DeleteDocumentCommand,
    DumpCommand,
    NewDocumentCommand,
    ShowDocumentCommand,
    ShowDocumentJsonCommand,
    ShowPagesCommand,
)
from .documents import DocumentsCommand, ShowDocumentsCommand
from .upload import UploadCommand
from .utils import FileHelpCommand, JoinDocumentsCommand

__all__ = [
    # Core file operations
    "UploadCommand",
    # Document listing
    "DocumentsCommand",
    "ShowDocumentsCommand",
    # Document operations
    "DeleteDocumentCommand",
    "DumpCommand",
    "NewDocumentCommand",
    "ShowDocumentCommand",
    "ShowDocumentJsonCommand",
    "ShowPagesCommand",
    # Collection operations
    "DeleteCollectionCommand",
    "NewCollectionCommand",
    "ShowCollectionCommand",
    "ShowCollectionsCommand",
    "UnuseCollectionCommand",
    "UseCollectionCommand",
    # Utilities
    "FileHelpCommand",
    "JoinDocumentsCommand",
]
