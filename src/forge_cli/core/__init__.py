"""Knowledge Forge CLI Core Data Models.

This package contains the core data structures used by Knowledge Forge APIs,
including document models, vector stores, task tracking, and file management.

Each class is defined in its own module to prevent circular import issues.
"""

# Document-related models
from .chunk import Chunk
from .document import Document
from .document_content import DocumentContent
from .page import Page

# File management models  
from ..sdk.file_response import FileResponse

# Task tracking models
from .trace import Trace

# Vector store models
from .file_count_stats import FileCountStats
from .vector_store import VectorStore

__all__ = [
    # Document models
    "Chunk",
    "Document", 
    "DocumentContent",
    "Page",
    # File models
    "FileResponse",
    # Task tracking models
    "Trace",
    # Vector store models
    "FileCountStats",
    "VectorStore",
]
