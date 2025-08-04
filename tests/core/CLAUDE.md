# Core Tests - Fundamental Data Structure Testing

## Overview

The core tests directory contains comprehensive tests for the fundamental data structures and business logic in the Forge CLI core module. These tests ensure the reliability, correctness, and performance of core abstractions including documents, chunks, pages, and vector store operations.

## Directory Structure

```
core/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Test package initialization
├── test_chunk.py                # Chunk data structure tests
├── test_document.py             # Document handling tests
├── test_document_content.py     # Document content processing tests
└── test_page.py                 # Page processing tests
```

## Test Architecture

### Testing Philosophy

1. **Domain Model Validation**: Test core business logic and domain models
2. **Data Integrity**: Ensure data structures maintain consistency
3. **Performance Testing**: Validate performance of core operations
4. **Edge Case Coverage**: Test boundary conditions and error scenarios
5. **Type Safety**: Verify Pydantic model validation and type constraints

### Test Categories

#### Unit Tests

- Individual class and function testing
- Pydantic model validation testing
- Business logic verification
- Error condition testing

#### Integration Tests

- Multi-component interaction testing
- Data pipeline testing
- End-to-end workflow validation
- Performance benchmarking

## Core Test Modules

### Chunk Testing (test_chunk.py)

Tests document chunk data structures and processing:

**Test Categories:**

- **Chunk Creation**: Test chunk instantiation and validation
- **Metadata Handling**: Test chunk metadata processing
- **Serialization**: Test chunk serialization/deserialization
- **Validation Rules**: Test Pydantic validation constraints
- **Performance**: Test chunk processing performance

**Example Test Structure:**

```python
import pytest
from pydantic import ValidationError
from forge_cli.core.chunk import Chunk, ChunkMetadata

class TestChunk:
    """Test suite for Chunk data structures."""
    
    def test_chunk_creation_valid(self):
        """Test valid chunk creation."""
        metadata = ChunkMetadata(
            document_id="doc_123",
            page_number=1,
            start_char=0,
            end_char=500,
            chunk_index=0
        )
        
        chunk = Chunk(
            id="chunk_456",
            content="Test chunk content...",
            metadata=metadata
        )
        
        assert chunk.id == "chunk_456"
        assert chunk.content == "Test chunk content..."
        assert chunk.metadata.document_id == "doc_123"
    
    def test_chunk_metadata_validation(self):
        """Test chunk metadata validation rules."""
        # Test invalid character positions
        with pytest.raises(ValidationError):
            ChunkMetadata(
                document_id="doc_123",
                page_number=1,
                start_char=500,  # Invalid: start > end
                end_char=100,
                chunk_index=0
            )
        
        # Test invalid page number
        with pytest.raises(ValidationError):
            ChunkMetadata(
                document_id="doc_123",
                page_number=0,  # Invalid: must be >= 1
                start_char=0,
                end_char=500,
                chunk_index=0
            )
    
    def test_chunk_serialization(self):
        """Test chunk serialization and deserialization."""
        original_chunk = Chunk(
            id="chunk_123",
            content="Test content",
            metadata=ChunkMetadata(
                document_id="doc_456",
                page_number=2,
                start_char=100,
                end_char=600,
                chunk_index=1
            )
        )
        
        # Serialize to dict
        chunk_dict = original_chunk.model_dump()
        
        # Deserialize from dict
        restored_chunk = Chunk.model_validate(chunk_dict)
        
        assert restored_chunk.id == original_chunk.id
        assert restored_chunk.content == original_chunk.content
        assert restored_chunk.metadata.document_id == original_chunk.metadata.document_id
```

### Document Testing (test_document.py)

Tests document handling and metadata management:

**Test Categories:**

- **Document Creation**: Test document instantiation
- **Metadata Processing**: Test document metadata handling
- **Status Management**: Test document status tracking
- **Validation**: Test document validation rules
- **Lifecycle**: Test document lifecycle management

**Example Test Structure:**

```python
import pytest
from datetime import datetime
from forge_cli.core.document import Document, DocumentMetadata

class TestDocument:
    """Test suite for Document data structures."""
    
    def test_document_creation_with_metadata(self):
        """Test document creation with metadata."""
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            file_type="pdf",
            size_bytes=1024000
        )
        
        document = Document(
            id="doc_123",
            metadata=metadata,
            content_hash="abc123def456",
            status="processed"
        )
        
        assert document.id == "doc_123"
        assert document.metadata.title == "Test Document"
        assert document.status == "processed"
        assert isinstance(document.created_at, datetime)
    
    def test_document_id_validation(self):
        """Test document ID validation."""
        metadata = DocumentMetadata(
            title="Test",
            file_type="pdf",
            size_bytes=1000
        )
        
        # Valid ID
        doc = Document(
            id="doc_123",
            metadata=metadata,
            content_hash="hash123"
        )
        assert doc.id == "doc_123"
        
        # Invalid ID format
        with pytest.raises(ValidationError):
            Document(
                id="invalid_123",  # Should start with 'doc_'
                metadata=metadata,
                content_hash="hash123"
            )
    
    def test_document_status_validation(self):
        """Test document status validation."""
        metadata = DocumentMetadata(
            title="Test",
            file_type="pdf",
            size_bytes=1000
        )
        
        # Valid statuses
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        for status in valid_statuses:
            doc = Document(
                id="doc_123",
                metadata=metadata,
                content_hash="hash123",
                status=status
            )
            assert doc.status == status
        
        # Invalid status
        with pytest.raises(ValidationError):
            Document(
                id="doc_123",
                metadata=metadata,
                content_hash="hash123",
                status="invalid_status"
            )
```

### Document Content Testing (test_document_content.py)

Tests document content processing and extraction:

**Test Categories:**

- **Content Extraction**: Test content extraction from various formats
- **Content Processing**: Test content normalization and cleaning
- **Performance**: Test content processing performance
- **Error Handling**: Test error conditions and recovery

### Page Testing (test_page.py)

Tests page-level document processing:

**Test Categories:**

- **Page Extraction**: Test page extraction from documents
- **Page Numbering**: Test page numbering and ordering
- **Page Content**: Test page content validation
- **Multi-page Documents**: Test multi-page document handling

## Test Utilities

### Test Data Factories

```python
# test_factories.py - Test data factories
from forge_cli.core.document import Document, DocumentMetadata
from forge_cli.core.chunk import Chunk, ChunkMetadata

class DocumentFactory:
    """Factory for creating test documents."""
    
    @staticmethod
    def create_document(
        doc_id: str = "doc_123",
        title: str = "Test Document",
        file_type: str = "pdf",
        status: str = "processed"
    ) -> Document:
        """Create a test document."""
        metadata = DocumentMetadata(
            title=title,
            file_type=file_type,
            size_bytes=1024000
        )
        
        return Document(
            id=doc_id,
            metadata=metadata,
            content_hash="test_hash_123",
            status=status
        )

class ChunkFactory:
    """Factory for creating test chunks."""
    
    @staticmethod
    def create_chunk(
        chunk_id: str = "chunk_123",
        document_id: str = "doc_123",
        content: str = "Test chunk content",
        page_number: int = 1
    ) -> Chunk:
        """Create a test chunk."""
        metadata = ChunkMetadata(
            document_id=document_id,
            page_number=page_number,
            start_char=0,
            end_char=len(content),
            chunk_index=0
        )
        
        return Chunk(
            id=chunk_id,
            content=content,
            metadata=metadata
        )
```

### Performance Testing

```python
import pytest
import time
from forge_cli.core.chunk import Chunk, ChunkMetadata

class TestPerformance:
    """Performance tests for core components."""
    
    @pytest.mark.performance
    def test_chunk_creation_performance(self):
        """Test chunk creation performance."""
        start_time = time.time()
        
        # Create many chunks
        chunks = []
        for i in range(1000):
            metadata = ChunkMetadata(
                document_id=f"doc_{i}",
                page_number=1,
                start_char=0,
                end_char=500,
                chunk_index=0
            )
            
            chunk = Chunk(
                id=f"chunk_{i}",
                content=f"Test content {i}",
                metadata=metadata
            )
            chunks.append(chunk)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should create 1000 chunks in reasonable time
        assert execution_time < 1.0  # Less than 1 second
        assert len(chunks) == 1000
    
    @pytest.mark.performance
    def test_chunk_serialization_performance(self):
        """Test chunk serialization performance."""
        # Create test chunk
        chunk = ChunkFactory.create_chunk()
        
        start_time = time.time()
        
        # Serialize many times
        for _ in range(1000):
            chunk_dict = chunk.model_dump()
            restored_chunk = Chunk.model_validate(chunk_dict)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should serialize/deserialize quickly
        assert execution_time < 2.0  # Less than 2 seconds
```

## Running Tests

### Test Execution

```bash
# Run all core tests
python -m pytest tests/core/

# Run specific test file
python -m pytest tests/core/test_chunk.py

# Run with coverage
python -m pytest tests/core/ --cov=forge_cli.core --cov-report=html

# Run performance tests
python -m pytest tests/core/ -m "performance"

# Run with verbose output
python -m pytest tests/core/ -v
```

## Related Components

- **Core Implementation** (`../src/forge_cli/core/`) - Code being tested
- **Main Test Suite** (`../`) - Additional integration tests
- **SDK Tests** (`../src/forge_cli/sdk/tests/`) - SDK-specific tests
- **Documentation** (`../docs/`) - Test documentation

## Best Practices

### Core Testing Guidelines

1. **Test Domain Logic**: Focus on business rules and domain constraints
2. **Validate Data Models**: Test Pydantic model validation thoroughly
3. **Performance Awareness**: Include performance tests for critical operations
4. **Edge Cases**: Test boundary conditions and error scenarios
5. **Type Safety**: Verify type annotations and constraints

### Maintenance

1. **Keep Updated**: Update tests when core models change
2. **Monitor Performance**: Track performance test results over time
3. **Review Coverage**: Maintain high test coverage for core components
4. **Document Edge Cases**: Document and test important edge cases
5. **Refactor Tests**: Improve test quality and maintainability

The core tests ensure the reliability and correctness of fundamental data structures and business logic that form the foundation of the Forge CLI application.
