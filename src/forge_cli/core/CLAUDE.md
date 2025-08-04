# Core Module - Fundamental Data Structures and Business Logic

## Overview

The core module contains fundamental data structures and business logic for the Forge CLI application. It provides core abstractions for documents, chunks, pages, vector stores, and other essential components that form the foundation of the Knowledge Forge API client functionality.

## Directory Structure

```
core/
├── CLAUDE.md                    # This documentation file
├── README.md                    # Core module overview
├── __init__.py                  # Module exports
├── chunk.py                     # Document chunk data structures
├── document.py                  # Document handling and metadata
├── document_content.py          # Document content processing
├── file_count_stats.py          # File statistics and counting
├── page.py                      # Page-level document processing
├── trace.py                     # Execution tracing and debugging
└── vector_store.py              # Vector store abstractions
```

## Architecture & Design

### Design Principles

1. **Domain-Driven Design**: Core abstractions match business domain concepts
2. **Type Safety**: Comprehensive Pydantic models with validation
3. **Immutability**: Immutable data structures where appropriate
4. **Composability**: Components can be combined and reused
5. **Performance**: Optimized for common operations and large datasets

### Core Abstractions

#### Document Processing Pipeline

The core module implements a document processing pipeline:

```
Document → Pages → Chunks → Vector Store
```

Each stage has corresponding data structures and processing logic.

## Core Components

### Document Management (document.py)

Provides core document abstractions and metadata handling:

**Key Classes:**

- **Document**: Core document representation with metadata
- **DocumentMetadata**: Document metadata and properties
- **DocumentStatus**: Document processing status tracking

**Features:**

- Document lifecycle management
- Metadata extraction and validation
- Status tracking and updates
- File format support

**Usage Example:**

```python
from forge_cli.core.document import Document, DocumentMetadata

# Create document with metadata
metadata = DocumentMetadata(
    title="Research Paper",
    author="John Doe",
    file_type="pdf",
    size_bytes=1024000
)

document = Document(
    id="doc_123",
    metadata=metadata,
    content_hash="abc123",
    status="processed"
)
```

### Document Content Processing (document_content.py)

Handles document content extraction and processing:

**Key Classes:**

- **DocumentContent**: Structured document content representation
- **ContentExtractor**: Content extraction from various formats
- **ContentProcessor**: Content processing and normalization

**Features:**

- Multi-format content extraction
- Text normalization and cleaning
- Content validation and sanitization
- Performance optimization for large documents

### Page Processing (page.py)

Manages page-level document processing:

**Key Classes:**

- **Page**: Individual page representation
- **PageContent**: Page content and metadata
- **PageProcessor**: Page-level processing logic

**Features:**

- Page extraction and numbering
- Page content validation
- Page metadata handling
- Multi-page document support

### Chunk Management (chunk.py)

Provides document chunking for vector processing:

**Key Classes:**

- **Chunk**: Document chunk with content and metadata
- **ChunkMetadata**: Chunk-specific metadata
- **ChunkProcessor**: Chunking algorithms and strategies

**Features:**

- Intelligent document chunking
- Chunk size optimization
- Overlap management
- Metadata preservation

**Usage Example:**

```python
from forge_cli.core.chunk import Chunk, ChunkMetadata

# Create document chunk
metadata = ChunkMetadata(
    document_id="doc_123",
    page_number=1,
    start_char=0,
    end_char=500,
    chunk_index=0
)

chunk = Chunk(
    id="chunk_456",
    content="Document content text...",
    metadata=metadata,
    embedding_vector=None  # Set after vectorization
)
```

### Vector Store Abstractions (vector_store.py)

Provides abstractions for vector store operations:

**Key Classes:**

- **VectorStore**: Vector store representation and operations
- **VectorStoreMetadata**: Vector store metadata and configuration
- **QueryResult**: Search result representation

**Features:**

- Vector store lifecycle management
- Query and search operations
- Result ranking and filtering
- Metadata management

### File Statistics (file_count_stats.py)

Provides file counting and statistics functionality:

**Key Classes:**

- **FileStats**: File statistics and metrics
- **FileCounter**: File counting utilities
- **StatsCollector**: Statistics collection and aggregation

**Features:**

- File type analysis
- Size distribution statistics
- Processing metrics
- Performance monitoring

### Execution Tracing (trace.py)

Provides execution tracing and debugging support:

**Key Classes:**

- **ExecutionTrace**: Execution trace representation
- **TraceCollector**: Trace collection and management
- **TraceAnalyzer**: Trace analysis and reporting

**Features:**

- Execution path tracing
- Performance profiling
- Debug information collection
- Error tracking and analysis

## Data Models and Validation

### Pydantic Model Integration

All core data structures use Pydantic models for validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class Document(BaseModel):
    """Core document model with validation."""
    
    id: str = Field(..., description="Unique document identifier")
    metadata: DocumentMetadata
    content_hash: str = Field(..., description="Content hash for integrity")
    status: str = Field(default="pending", description="Processing status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @validator('id')
    def validate_id(cls, v):
        if not v.startswith('doc_'):
            raise ValueError("Document ID must start with 'doc_'")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
```

### Type Safety and Validation

```python
from typing import Union, Literal
from pydantic import BaseModel, Field

class ChunkMetadata(BaseModel):
    """Chunk metadata with comprehensive validation."""
    
    document_id: str
    page_number: int = Field(ge=1, description="Page number (1-based)")
    start_char: int = Field(ge=0, description="Start character position")
    end_char: int = Field(gt=0, description="End character position")
    chunk_index: int = Field(ge=0, description="Chunk index in document")
    chunk_type: Literal["text", "table", "image", "header"] = "text"
    
    @validator('end_char')
    def validate_char_positions(cls, v, values):
        if 'start_char' in values and v <= values['start_char']:
            raise ValueError("end_char must be greater than start_char")
        return v
```

## Business Logic Patterns

### Processing Pipelines

```python
from typing import List, Iterator
from forge_cli.core.document import Document
from forge_cli.core.chunk import Chunk

class DocumentProcessor:
    """Document processing pipeline."""
    
    def process_document(self, document: Document) -> List[Chunk]:
        """Process document through complete pipeline."""
        # Extract content
        content = self.extract_content(document)
        
        # Process pages
        pages = self.extract_pages(content)
        
        # Create chunks
        chunks = self.create_chunks(pages)
        
        # Validate and return
        return self.validate_chunks(chunks)
    
    def extract_content(self, document: Document) -> str:
        """Extract content from document."""
        # Implementation specific to document type
        pass
    
    def extract_pages(self, content: str) -> List[Page]:
        """Extract pages from content."""
        # Page extraction logic
        pass
    
    def create_chunks(self, pages: List[Page]) -> List[Chunk]:
        """Create chunks from pages."""
        # Chunking algorithm
        pass
```

### Error Handling and Recovery

```python
from typing import Optional
from forge_cli.core.trace import ExecutionTrace

class RobustProcessor:
    """Processor with error handling and recovery."""
    
    def __init__(self):
        self.trace = ExecutionTrace()
    
    def safe_process(self, document: Document) -> Optional[List[Chunk]]:
        """Process document with error handling."""
        try:
            self.trace.start("document_processing", document.id)
            
            # Processing logic
            result = self.process_document(document)
            
            self.trace.success("document_processing")
            return result
            
        except Exception as e:
            self.trace.error("document_processing", str(e))
            
            # Attempt recovery
            recovery_result = self.attempt_recovery(document, e)
            if recovery_result:
                self.trace.info("recovery_successful")
                return recovery_result
            
            # Log and return None if recovery fails
            self.trace.fatal("recovery_failed")
            return None
    
    def attempt_recovery(self, document: Document, error: Exception) -> Optional[List[Chunk]]:
        """Attempt to recover from processing error."""
        # Recovery logic based on error type
        pass
```

## Performance Optimization

### Lazy Loading and Caching

```python
from functools import lru_cache
from typing import Dict, Any

class OptimizedDocument(Document):
    """Document with performance optimizations."""
    
    _content_cache: Optional[str] = None
    _chunks_cache: Optional[List[Chunk]] = None
    
    @property
    def content(self) -> str:
        """Lazy-loaded document content."""
        if self._content_cache is None:
            self._content_cache = self._load_content()
        return self._content_cache
    
    @lru_cache(maxsize=128)
    def get_chunks(self, chunk_size: int = 1000) -> List[Chunk]:
        """Cached chunk generation."""
        if self._chunks_cache is None:
            self._chunks_cache = self._generate_chunks(chunk_size)
        return self._chunks_cache
    
    def _load_content(self) -> str:
        """Load content from storage."""
        # Implementation
        pass
    
    def _generate_chunks(self, chunk_size: int) -> List[Chunk]:
        """Generate chunks with specified size."""
        # Implementation
        pass
```

## Integration Points

### SDK Integration

```python
from forge_cli.sdk import async_upload_file, async_create_vectorstore
from forge_cli.core.document import Document
from forge_cli.core.vector_store import VectorStore

async def create_knowledge_base(documents: List[Document]) -> VectorStore:
    """Create knowledge base from documents."""
    # Upload documents
    file_ids = []
    for doc in documents:
        result = await async_upload_file(doc.file_path)
        file_ids.append(result['id'])
    
    # Create vector store
    vs_result = await async_create_vectorstore(
        name="Knowledge Base",
        file_ids=file_ids
    )
    
    # Return core abstraction
    return VectorStore(
        id=vs_result['id'],
        name=vs_result['name'],
        file_ids=file_ids,
        document_count=len(documents)
    )
```

## Related Components

- **SDK** (`../sdk/`) - Uses core abstractions for API operations
- **Models** (`../models/`) - Extends core models for application-specific needs
- **Response Types** (`../response/_types/`) - API response types that map to core abstractions
- **Display** (`../display/`) - Renders core data structures for output

## Best Practices

### Data Modeling

1. **Use Pydantic Models**: Comprehensive validation and type safety
2. **Immutable Data**: Prefer immutable data structures where possible
3. **Clear Hierarchies**: Establish clear relationships between entities
4. **Validation Rules**: Include comprehensive validation logic
5. **Performance Awareness**: Optimize for common access patterns

### Business Logic

1. **Single Responsibility**: Each class has one clear purpose
2. **Error Handling**: Robust error handling and recovery
3. **Tracing**: Include execution tracing for debugging
4. **Testing**: Comprehensive unit tests for all logic
5. **Documentation**: Clear documentation for all public interfaces

The core module provides the foundational abstractions and business logic that enable the Forge CLI to work effectively with documents, vector stores, and the Knowledge Forge API.
