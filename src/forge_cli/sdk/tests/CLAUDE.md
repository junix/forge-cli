# SDK Tests - Comprehensive SDK Test Suite

## Overview

The SDK tests directory contains comprehensive tests for the Knowledge Forge SDK functionality. These tests ensure the reliability, correctness, and performance of all SDK operations including file management, vector store operations, response generation, and API communication.

## Directory Structure

```
tests/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Test package initialization
├── test_files.py                # File operations testing
└── test_vectorstore.py          # Vector store operations testing
```

## Test Architecture

### Testing Philosophy

1. **Comprehensive Coverage**: Test all critical SDK functionality
2. **Integration Testing**: Test real API interactions with proper mocking
3. **Error Handling**: Verify error conditions and edge cases
4. **Performance Testing**: Ensure acceptable performance characteristics
5. **Type Safety**: Validate type annotations and Pydantic models

### Test Categories

#### Unit Tests

- Individual function testing in isolation
- Pydantic model validation testing
- Type guard function verification
- Utility function testing

#### Integration Tests

- End-to-end API workflow testing
- Multi-component interaction testing
- Real API communication testing (with proper setup)
- Error propagation testing

#### Performance Tests

- Response time benchmarking
- Memory usage monitoring
- Concurrent operation testing
- Large file handling testing

## Core Test Modules

### File Operations Testing (test_files.py)

Tests all file-related SDK functionality:

**Test Categories:**

- **File Upload Tests**: Upload various file types and sizes
- **File Retrieval Tests**: Fetch file metadata and content
- **File Deletion Tests**: Remove files and verify cleanup
- **Task Management Tests**: Monitor async file processing
- **Error Handling Tests**: Invalid files, network errors, etc.

**Example Test Structure:**

```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from forge_cli.sdk.files import async_upload_file, async_fetch_file

class TestFileOperations:
    """Test suite for file operations."""
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """Test successful file upload."""
        # Mock API response
        mock_response = {
            'id': 'file_123',
            'filename': 'test.pdf',
            'status': 'uploaded',
            'task_id': 'task_456'
        }
        
        with patch('forge_cli.sdk.files.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = mock_response
            
            result = await async_upload_file('/path/to/test.pdf')
            
            assert result['id'] == 'file_123'
            assert result['filename'] == 'test.pdf'
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_path(self):
        """Test upload with invalid file path."""
        with pytest.raises(FileNotFoundError):
            await async_upload_file('/nonexistent/file.pdf')
    
    @pytest.mark.asyncio
    async def test_fetch_file_success(self):
        """Test successful file retrieval."""
        mock_response = {
            'id': 'file_123',
            'filename': 'test.pdf',
            'size': 1024000,
            'status': 'processed'
        }
        
        with patch('forge_cli.sdk.files.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value.json.return_value = mock_response
            
            result = await async_fetch_file('file_123')
            
            assert result['id'] == 'file_123'
            assert result['status'] == 'processed'
    
    @pytest.mark.asyncio
    async def test_file_processing_workflow(self):
        """Test complete file processing workflow."""
        # Upload file
        upload_result = await async_upload_file('/path/to/test.pdf')
        file_id = upload_result['id']
        task_id = upload_result['task_id']
        
        # Wait for processing
        if task_id:
            final_status = await async_wait_for_task_completion(task_id)
            assert final_status['status'] == 'completed'
        
        # Verify file is processed
        file_info = await async_fetch_file(file_id)
        assert file_info['status'] == 'processed'
```

### Vector Store Testing (test_vectorstore.py)

Tests vector store operations and semantic search:

**Test Categories:**

- **Vector Store Creation**: Create stores with various configurations
- **File Integration**: Add files to vector stores
- **Query Operations**: Semantic search and filtering
- **Metadata Management**: Store and retrieve metadata
- **Performance Testing**: Large-scale operations

**Example Test Structure:**

```python
import pytest
from forge_cli.sdk.vectorstore import (
    async_create_vectorstore,
    async_query_vectorstore,
    async_join_files_to_vectorstore
)

class TestVectorStoreOperations:
    """Test suite for vector store operations."""
    
    @pytest.mark.asyncio
    async def test_create_vectorstore_success(self):
        """Test successful vector store creation."""
        mock_response = {
            'id': 'vs_123',
            'name': 'Test Store',
            'file_count': 2,
            'status': 'ready'
        }
        
        with patch('forge_cli.sdk.vectorstore.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = mock_response
            
            result = await async_create_vectorstore(
                name="Test Store",
                file_ids=["file_123", "file_456"]
            )
            
            assert result['id'] == 'vs_123'
            assert result['file_count'] == 2
    
    @pytest.mark.asyncio
    async def test_query_vectorstore_success(self):
        """Test successful vector store querying."""
        mock_response = {
            'results': [
                {
                    'chunk_id': 'chunk_123',
                    'content': 'Relevant content...',
                    'score': 0.95,
                    'metadata': {'page': 1, 'file_id': 'file_123'}
                }
            ],
            'total_results': 1
        }
        
        with patch('forge_cli.sdk.vectorstore.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json.return_value = mock_response
            
            results = await async_query_vectorstore(
                vector_store_id="vs_123",
                query="test query",
                top_k=10
            )
            
            assert len(results['results']) == 1
            assert results['results'][0]['score'] == 0.95
    
    @pytest.mark.asyncio
    async def test_vectorstore_workflow(self):
        """Test complete vector store workflow."""
        # Create vector store
        vs_result = await async_create_vectorstore(
            name="Workflow Test",
            file_ids=["file_123"]
        )
        vs_id = vs_result['id']
        
        # Add more files
        await async_join_files_to_vectorstore(
            vector_store_id=vs_id,
            file_ids=["file_456", "file_789"]
        )
        
        # Query the store
        results = await async_query_vectorstore(
            vector_store_id=vs_id,
            query="test query"
        )
        
        assert len(results['results']) > 0
```

## Test Configuration

### pytest Configuration

```python
# conftest.py - Test configuration
import pytest
import asyncio
from unittest.mock import Mock
from forge_cli.sdk.config import BASE_URL

@pytest.fixture
def mock_api_response():
    """Mock API response fixture."""
    return {
        'id': 'test_123',
        'status': 'success',
        'data': {}
    }

@pytest.fixture
def mock_session():
    """Mock aiohttp session fixture."""
    session = Mock()
    session.__aenter__ = Mock(return_value=session)
    session.__aexit__ = Mock(return_value=None)
    return session

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Set test API URL
    import forge_cli.sdk.config as config
    config.BASE_URL = "http://test-api.example.com"
    
    yield
    
    # Cleanup after test
    config.BASE_URL = BASE_URL
```

### Test Utilities

```python
# test_utils.py - Test utilities
import tempfile
import os
from typing import Dict, Any

def create_test_file(content: str = "Test content", suffix: str = ".txt") -> str:
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

def cleanup_test_file(file_path: str) -> None:
    """Clean up test file."""
    if os.path.exists(file_path):
        os.unlink(file_path)

def assert_api_call(mock_session, method: str, url: str, **kwargs) -> None:
    """Assert that API call was made with correct parameters."""
    if method.upper() == 'POST':
        mock_session.post.assert_called_with(url, **kwargs)
    elif method.upper() == 'GET':
        mock_session.get.assert_called_with(url, **kwargs)
    else:
        raise ValueError(f"Unsupported method: {method}")

def create_mock_response(data: Dict[str, Any], status: int = 200) -> Mock:
    """Create mock HTTP response."""
    response = Mock()
    response.status = status
    response.json = Mock(return_value=data)
    response.__aenter__ = Mock(return_value=response)
    response.__aexit__ = Mock(return_value=None)
    return response
```

## Running Tests

### Test Execution Commands

```bash
# Run all SDK tests
python -m pytest src/forge_cli/sdk/tests/

# Run specific test file
python -m pytest src/forge_cli/sdk/tests/test_files.py

# Run with coverage
python -m pytest src/forge_cli/sdk/tests/ --cov=forge_cli.sdk --cov-report=html

# Run with verbose output
python -m pytest src/forge_cli/sdk/tests/ -v

# Run only async tests
python -m pytest src/forge_cli/sdk/tests/ -k "async"

# Run performance tests
python -m pytest src/forge_cli/sdk/tests/ -m "performance"
```

### Test Markers

```python
# Test markers for categorization
import pytest

# Mark slow tests
@pytest.mark.slow
def test_large_file_upload():
    """Test uploading large files."""
    pass

# Mark integration tests
@pytest.mark.integration
def test_api_integration():
    """Test real API integration."""
    pass

# Mark performance tests
@pytest.mark.performance
def test_concurrent_operations():
    """Test concurrent API operations."""
    pass
```

## Quality Assurance

### Test Quality Standards

1. **Clear Test Names**: Descriptive test function names
2. **Isolated Tests**: Tests don't depend on each other
3. **Comprehensive Mocking**: Mock external dependencies appropriately
4. **Error Testing**: Test both success and failure scenarios
5. **Performance Awareness**: Include performance-related tests

### Continuous Integration

Tests integrate with CI/CD pipeline:

1. **Automated Execution**: Run on every commit
2. **Coverage Reporting**: Track test coverage metrics
3. **Performance Monitoring**: Monitor test execution time
4. **Quality Gates**: Prevent merging if tests fail

## Related Components

- **SDK Implementation** (`../`) - Code being tested
- **Main Test Suite** (`../../../tests/`) - Additional integration tests
- **Documentation** (`../../../../docs/`) - Test documentation and examples
- **CI/CD** - Continuous integration configuration

## Best Practices

### Writing SDK Tests

1. **Test Real Scenarios**: Test actual use cases and workflows
2. **Mock Appropriately**: Mock external dependencies but test real logic
3. **Handle Async**: Properly test async functions and error handling
4. **Validate Types**: Test Pydantic model validation and type safety
5. **Performance Aware**: Include tests for performance-critical operations

### Maintaining Tests

1. **Keep Updated**: Update tests when SDK changes
2. **Monitor Coverage**: Maintain high test coverage
3. **Review Failures**: Investigate and fix failing tests promptly
4. **Refactor Tests**: Improve test quality over time
5. **Document Edge Cases**: Document and test edge cases and limitations

The SDK test suite ensures the reliability and correctness of all Knowledge Forge API interactions, providing confidence in the SDK's functionality and performance.
