"""File operation commands for chat mode.

This module contains all file and document related commands, with each command in its own file
for maximum modularity and maintainability.
"""

# Core file operations
# Collection operations
from .delete_collection import DeleteCollectionCommand

# Document operations
from .delete_document import DeleteDocumentCommand

# Document listing
from .documents_list import DocumentsCommand
from .dump import DumpCommand

# Utility commands
from .file_help import FileHelpCommand
from .join_documents import JoinDocumentsCommand
from .new_collection import NewCollectionCommand
from .new_document import NewDocumentCommand
from .show_collection import ShowCollectionCommand
from .show_collections import ShowCollectionsCommand
from .show_document import ShowDocumentCommand
from .show_document_json import ShowDocumentJsonCommand
from .show_documents import ShowDocumentsCommand
from .show_pages import ShowPagesCommand
from .topk_query import TopKQueryCommand
from .unuse_collection import UnuseCollectionCommand
from .upload import UploadCommand
from .use_collection import UseCollectionCommand

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
    # Query operations
    "TopKQueryCommand",
    # Utilities
    "FileHelpCommand",
    "JoinDocumentsCommand",
]
