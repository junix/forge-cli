# Knowledge Forge CLI Core Data Models

This package contains the core data structures used by Knowledge Forge APIs. These models are based on Pydantic and provide type safety, validation, and clear documentation for the core entities in the Knowledge Forge system.

**Architecture**: Each class is defined in its own module following the **one-file-one-class** pattern to prevent circular import issues and improve maintainability.

## Overview

The core models are organized into individual modules:

### Document Models

- **`Chunk`** (`chunk.py`): Represents a text segment for vector search and retrieval
- **`Page`** (`page.py`): Specialized chunk representing a document page (inherits from Chunk)
- **`DocumentContent`** (`document_content.py`): Contains the parsed and processed content of a document  
- **`Document`** (`document.py`): Represents a complete document with metadata and content

### Vector Store Models

- **`FileCountStats`** (`file_count_stats.py`): Tracks file processing statistics within a vector store
- **`VectorStore`** (`vector_store.py`): Represents a collection of documents and embeddings for semantic search

### Task Tracking Models

- **`Trace`** (`trace.py`): Tracks background task execution status and progress

### File Management Models

- **`FileResponse`** (`file_response.py`): Response object for file upload operations

## Usage

### Basic Import

```python
from forge_cli.core import Document, VectorStore, Trace, FileResponse
```

### Creating a Document

```python
from forge_cli.core import Document, DocumentContent, Chunk

# Create document content with chunks
content = DocumentContent(
    id="md5_hash_here",
    abstract="Document abstract",
    keywords=["ai", "knowledge", "search"],
    segments=[
        Chunk(content="First chunk of text", index=0),
        Chunk(content="Second chunk of text", index=1)
    ]
)

# Create the document
doc = Document(
    id="doc_123",
    md5sum="md5_hash_here", 
    mime_type="application/pdf",
    title="Sample Document",
    content=content
)
```

### Working with Vector Stores

```python
from forge_cli.core import VectorStore, FileCountStats

# Create file statistics
stats = FileCountStats(
    completed=5,
    in_progress=2,
    total=7
)

# Create vector store
vector_store = VectorStore(
    id="vs_123",
    created_at=1699061776,
    name="Knowledge Base",
    description="Company knowledge documents",
    file_counts=stats
)
```

### Tracking Tasks

```python
from forge_cli.core import Trace

# Create a task trace
trace = Trace(
    id="task_123",
    status="in_progress", 
    progress=0.75,
    data={"operation": "file_processing", "files_processed": 3}
)
```

## Model Relationships

```
Document
├── content: DocumentContent  
│   └── segments: List[Chunk|Page]
└── vector_store_ids: List[str] → VectorStore

FileResponse
└── task_id: str → Trace

VectorStore  
├── file_counts: FileCountStats
└── task_id: str → Trace
```

## Validation Features

All models include:

- **Type validation**: Automatic validation of field types
- **Field constraints**: Min/max values, string patterns, etc.
- **Optional fields**: Clear distinction between required and optional data
- **Default values**: Sensible defaults for optional fields
- **Documentation**: Built-in field descriptions for API documentation

## Notes

- These models are designed to be compatible with the Knowledge Forge Response API
- Response API specific models are handled in a separate package
- All models use Pydantic v2 for validation and serialization
- UUIDs are automatically generated for IDs where appropriate 