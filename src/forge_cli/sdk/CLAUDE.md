# Knowledge Forge SDK - Python Client Library

## Overview

The SDK module provides a comprehensive Python client library for interacting with the Knowledge Forge API. It offers both legacy dict-based and modern typed APIs for file management, vector store operations, response generation, and streaming capabilities. The SDK is designed with type safety, async/await patterns, and comprehensive error handling.

## Directory Structure

```
sdk/
├── __init__.py                    # Main SDK exports and public API
├── config.py                      # Configuration and base URL settings
├── common_types.py                # Shared type definitions
├── files.py                       # File upload, management, and task operations
├── file_types.py                  # File-related type definitions
├── http_client.py                 # HTTP client utilities and helpers
├── response.py                    # Legacy dict-based response API
├── typed_api.py                   # Modern typed response API (recommended)
├── types.py                       # Core type definitions
├── task_types.py                  # Task management type definitions
├── utils.py                       # Utility functions for response processing
├── vectorstore.py                 # Vector store operations and management
├── vectorstore_types.py           # Vector store type definitions
├── vectorstore_query_types.py     # Vector store query type definitions
└── tests/                         # SDK test suite
    ├── test_files.py              # File operations tests
    └── test_vectorstore.py        # Vector store tests
```

## Architecture & Design

### Design Principles

1. **Type Safety**: Comprehensive type annotations and Pydantic models
2. **Async/Await**: Full async support for non-blocking operations
3. **Error Handling**: Robust error handling with detailed logging
4. **Streaming Support**: Real-time streaming for response generation
5. **Backward Compatibility**: Support for both legacy and modern APIs
6. **Modular Design**: Separate modules for different API domains

### Typed API Architecture

The SDK now exclusively uses typed APIs for type safety and better developer experience:

#### Typed API (typed_api.py) - Current Standard

```python
# Create typed request with validation
request = create_typed_request(
    input_messages="Your query",
    model="qwen-max-latest",
    tools=[create_file_search_tool(["vs_123"])]
)

# Get complete response
response = await async_create_typed_response(request)
print(response.output_text)

# Or stream responses with real-time updates
async for event_type, response_snapshot in astream_typed_response(request):
    if event_type == "response.output_text.delta" and response_snapshot:
        print(response_snapshot.output_text, end="", flush=True)
    elif event_type == "response.completed":
        break
```

## Core Modules

### Response Generation (typed_api.py)

**Core Typed API Functions:**

- `async_create_typed_response()` - Type-safe response creation
- `astream_typed_response()` - Typed streaming with Response snapshots
- `create_typed_request()` - Request object creation helper
- `create_file_search_tool()` - File search tool factory
- `create_web_search_tool()` - Web search tool factory

**Response Utilities (response.py):**

- `async_fetch_response()` - Retrieve existing responses by ID

### File Management (files.py)

**Core Functions:**

- `async_upload_file()` - Upload files with metadata and processing
- `async_fetch_file()` - Retrieve file content and metadata
- `async_delete_file()` - Remove files from the system
- `async_check_task_status()` - Monitor file processing tasks
- `async_wait_for_task_completion()` - Wait for async file processing

**Features:**

- Automatic file type detection
- Progress tracking for large uploads
- Task-based async processing
- Comprehensive error handling

### Vector Store Operations (vectorstore.py)

**Core Functions:**

- `async_create_vectorstore()` - Create new vector stores
- `async_query_vectorstore()` - Semantic search operations
- `async_get_vectorstore()` - Retrieve vector store metadata
- `async_delete_vectorstore()` - Remove vector stores
- `async_join_files_to_vectorstore()` - Add files to existing stores
- `async_get_vectorstore_summary()` - Get store statistics

**Features:**

- Semantic search with filtering
- Batch file operations
- Metadata management
- Query result ranking

### Utilities (utils.py)

**Helper Functions:**

- `get_response_text()` - Extract formatted text from responses
- `has_tool_calls()` - Check for tool usage in responses
- `get_tool_call_results()` - Extract tool execution results
- `get_citation_count()` - Count citations in responses
- `print_response_results()` - Formatted response display
- `example_response_usage()` - Usage examples and demos

## Usage Examples

### Basic Response Generation

```python
from forge_cli.sdk import async_create_typed_response, create_typed_request

# Simple text generation with typed API
request = create_typed_request(
    input_messages="Explain machine learning",
    model="qwen-max-latest",
    effort="medium",
    temperature=0.7
)

response = await async_create_typed_response(request)
if response:
    print(response.output_text)
    print(f"Citations: {len(response.collect_citable_items())}")
```

### Streaming Responses

```python
from forge_cli.sdk import astream_typed_response, create_typed_request

# Create typed request for streaming
request = create_typed_request(
    input_messages="Tell me about AI",
    model="qwen-max-latest"
)

# Stream response with real-time updates
async for event_type, response_snapshot in astream_typed_response(request, debug=False):
    if event_type == "response.output_text.delta" and response_snapshot:
        print(response_snapshot.output_text, end="", flush=True)
    elif event_type == "response.completed":
        print(f"\nFinal response: {response_snapshot.output_text}")
        break
```

### File Operations

```python
from forge_cli.sdk import async_upload_file, async_wait_for_task_completion

# Upload and process file
result = await async_upload_file(
    path="/path/to/document.pdf",
    purpose="qa",
    custom_id="my-doc-001"
)

# Wait for processing completion
if result.task_id:
    final_status = await async_wait_for_task_completion(
        result.task_id,
        poll_interval=2,
        max_attempts=60
    )
    print(f"Processing completed: {final_status}")
```

### Vector Store Operations

```python
from forge_cli.sdk import (
    async_create_vectorstore,
    async_query_vectorstore,
    async_join_files_to_vectorstore
)

# Create vector store
vs_result = await async_create_vectorstore(
    name="Research Papers",
    description="AI and ML research collection",
    file_ids=["file_123", "file_456"],
    metadata={"domain": "research", "year": "2024"}
)

# Query vector store
results = await async_query_vectorstore(
    vector_store_id=vs_result["id"],
    query="transformer architecture",
    top_k=10,
    filters={"domain": "research"}
)

# Add more files
await async_join_files_to_vectorstore(
    vector_store_id=vs_result["id"],
    file_ids=["file_789"]
)
```

### Complete Typed API Workflow

```python
from forge_cli.sdk import (
    create_typed_request,
    async_create_typed_response,
    astream_typed_response,
    create_file_search_tool,
    create_web_search_tool
)

# Create typed request with multiple tools
request = create_typed_request(
    input_messages="What information is in my documents, and what are the latest industry trends?",
    model="qwen-max-latest",
    tools=[
        create_file_search_tool(["vs_123", "vs_456"], max_search_results=10),
        create_web_search_tool()
    ],
    effort="high",
    temperature=0.3
)

# Non-streaming typed response
response = await async_create_typed_response(request)
print(f"Response: {response.output_text}")
print(f"Citations: {len(response.collect_citable_items())}")

# Or streaming typed response with real-time updates
async for event_type, response_snapshot in astream_typed_response(request):
    if event_type == "response.output_text.delta" and response_snapshot:
        print(response_snapshot.output_text, end="", flush=True)
    elif event_type == "response.completed":
        print(f"\nCompleted! Citations: {len(response_snapshot.collect_citable_items())}")
        break
```

## Configuration

### Environment Variables

```bash
# Required: Knowledge Forge API base URL
export KNOWLEDGE_FORGE_URL=http://localhost:9999

# Optional: API authentication (if required)
export KNOWLEDGE_FORGE_API_KEY=your-api-key

# Optional: Default model selection
export KNOWLEDGE_FORGE_DEFAULT_MODEL=qwen-max-latest
```

### Programmatic Configuration

```python
from forge_cli.sdk.config import BASE_URL

# Override base URL programmatically
import forge_cli.sdk.config as sdk_config
sdk_config.BASE_URL = "https://your-custom-endpoint.com"
```

## Error Handling

The SDK provides comprehensive error handling with detailed logging:

```python
from forge_cli.sdk import async_create_typed_response, create_typed_request
from loguru import logger

try:
    request = create_typed_request(
        input_messages="Your query",
        model="qwen-max-latest"
    )
    response = await async_create_typed_response(request, debug=True)
    if response is None:
        logger.error("Response creation failed")
except Exception as e:
    logger.error(f"SDK error: {e}")
```

## Testing

The SDK includes comprehensive tests for all major functionality:

```bash
# Run SDK tests
python -m pytest src/forge_cli/sdk/tests/

# Run specific test modules
python -m pytest src/forge_cli/sdk/tests/test_files.py
python -m pytest src/forge_cli/sdk/tests/test_vectorstore.py
```

## Import Guidelines

The SDK follows the project's import conventions:

```python
# Use relative imports within SDK modules
from .config import BASE_URL
from .types import Response
from .utils import get_response_text

# Use absolute imports from outside the SDK
from forge_cli.sdk import async_create_typed_response, create_typed_request, async_upload_file
```

## Current API Design

The SDK now uses exclusively typed APIs for all operations:

**Response Creation:**

```python
# Create request with type validation
request = create_typed_request(
    input_messages="Your query",
    model="qwen-max-latest",
    tools=[create_file_search_tool(["vs_123"])],
    effort="medium"
)

# Get response
response = await async_create_typed_response(request)
text = response.output_text  # Type-safe access with IDE autocomplete
```

**Streaming:**

```python
# Stream with real-time snapshots
async for event_type, response_snapshot in astream_typed_response(request):
    if event_type == "response.output_text.delta":
        # Process incremental updates
        pass
    elif event_type == "response.completed":
        # Final response ready
        break
```

## Related Components

- **Main CLI** (`src/forge_cli/main.py`) - Uses SDK for all API interactions
- **Response Types** (`src/forge_cli/response/`) - Response data models used by SDK
- **Stream Handler** (`src/forge_cli/stream/`) - Processes SDK streaming responses
- **Configuration** (`src/forge_cli/config.py`) - CLI configuration that extends SDK config

The SDK serves as the foundation for all Knowledge Forge API interactions, providing a robust, type-safe, and feature-complete Python client library with comprehensive Pydantic validation and modern async patterns.
