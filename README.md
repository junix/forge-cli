# Forge CLI - Modern Command Line Tools for Knowledge Forge API

## Overview

This project provides modern, modular command-line tools and SDK for interacting with the Knowledge Forge API. Built with Python 3.8+ and structured as a proper Python package, it offers comprehensive functionality for:

- **Interactive Chat Mode**: Multi-turn conversations with context preservation
- **File Search**: Semantic search through uploaded documents with AI-powered responses
- **Web Search**: Real-time web search integration for current information
- **File Management**: Upload, process, and manage document files
- **Vector Store Operations**: Create and query vector stores for document search
- **Streaming Responses**: Real-time response streaming with rich terminal UI

The tools feature a modern event-based display architecture (v2) with multiple output formats (Rich UI, Plain text, JSON) and comprehensive chat functionality with command system.

## Installation & Quick Start

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd forge-cli

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Environment Configuration

```bash
export KNOWLEDGE_FORGE_URL=http://localhost:9999  # Default server URL
export OPENAI_API_KEY=your-api-key                # Optional, for some features
```

### Running Commands

**IMPORTANT**: All commands must be run from the `src` directory for Python to properly find the `forge_cli` package.

```bash
# Navigate to the src directory first
cd /path/to/forge-cli/src

# Then run commands using Python module syntax
python -m forge_cli --help

# Examples:
python -m forge_cli --chat                           # Start chat mode
python -m forge_cli -q "Your question" --vec-id vs_123  # File search
python -m forge_cli -t web-search -q "Latest AI news"   # Web search
```

### Common Usage Examples

```bash
# Interactive chat mode
python -m forge_cli --chat

# File search with vector store
python -m forge_cli -q "What information is in these documents?" --vec-id your-vector-store-id

# Web search  
python -m forge_cli -t web-search -q "Latest AI developments"

# Multiple tools combined
python -m forge_cli -t file-search -t web-search --vec-id vs_123 -q "Compare internal docs with industry trends"

# JSON output for scripting
python -m forge_cli --json -q "Your question"

# Debug mode for troubleshooting
python -m forge_cli --debug -q "Your question"
```

## Important Guidelines for Developers

### SDK-First Approach

1. **Use the SDK**: `sdk.py` is the official Python SDK for connecting to the Knowledge Forge server. All new scripts MUST use this SDK rather than making direct REST API calls.

2. **No Direct API Calls**: Do not create direct REST API calls to the server in new scripts. Always use the functions provided by the SDK.

3. **Async Pattern**: All SDK functions follow an async pattern. Your scripts should also use async/await when using the SDK.

### SDK Features

The `sdk.py` module provides:

- Async functions for all API operations
- Consistent error handling
- Environment variable support for configuration
- Type annotations and comprehensive documentation
- Utility functions for common operations

## Installation

### Prerequisites

- Python 3.8+
- `aiohttp` library for async HTTP communication
- `rich` library for terminal output formatting
- `loguru` library for logging

### Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd knowledge-forge-office
   ```

2. Set up your environment:

   ```bash
   # Set PYTHONPATH environment variable
   export PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge
   
   # Set Knowledge Forge URL (default is http://localhost:9999)
   export KNOWLEDGE_FORGE_URL=http://localhost:9999
   ```

3. Run commands using `uv`:

   ```bash
   # Example: Run the hello-async.py script
   cd /Users/junix/knowledge-forge-office/knowledge_forge
   uv run -m commands.hello-async
   ```

## SDK Usage Guide

The SDK is designed to be intuitive and easy to use, with a consistent async API pattern. Here's how to use the main components:

### Basic Example

```python
#!/usr/bin/env python3
import asyncio
import os
from sdk import async_create_response, async_fetch_response

async def main():
    # The SDK respects the KNOWLEDGE_FORGE_URL environment variable
    # or defaults to http://localhost:9999
    
    # Create a response
    response = await async_create_response(
        input_messages="Your query here",
        model="qwen-max-latest",
        effort="low"
    )
    
    if response:
        print(f"Response created with ID: {response.get('id')}")
        
        # Fetch the response by ID
        fetched = await async_fetch_response(response.get('id'))
        if fetched:
            print("Successfully retrieved response")

if __name__ == "__main__":
    asyncio.run(main())
```

### Response API Usage

#### Creating a Response

```python
# Simple string input
response = await async_create_response(
    input_messages="Tell me about Knowledge Forge",
    model="qwen-max-latest",
    effort="low",  # Options: "low", "medium", "high"
    temperature=0.7,
    max_output_tokens=1000
)

# Or with structured messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me about Knowledge Forge"}
]
response = await async_create_response(
    input_messages=messages,
    model="qwen-max-latest"
)
```

#### Fetching a Response by ID

```python
response_id = "resp_12345"
response = await async_fetch_response(response_id)
```

#### Streaming a Response

```python
# Using astream_response for streaming
async for event_type, event_data in astream_response(
    input_messages="Tell me about Knowledge Forge",
    model="qwen-max-latest",
    effort="low"
):
    # Process delta text events
    if event_type == "response.output_text.delta" and event_data and "text" in event_data:
        text_content = event_data["text"]
        print(text_content, end="", flush=True)
    
    # Process completed event
    elif event_type == "response.completed":
        print("\nResponse completed!")
        
    # Handle done event
    elif event_type == "done":
        print("\nStream finished.")
        break
```

### File API Usage

#### Uploading a File

```python
result = await async_upload_file(
    path="/path/to/your/file.pdf",
    purpose="general",  # or "qa" for question-answering
    custom_id="my-custom-file-id",  # optional
    skip_exists=False  # whether to skip if file with same MD5 exists
)

if result:
    file_id = result.get("id")
    task_id = result.get("task_id")
    
    # Wait for processing to complete if there's a task
    if task_id:
        final_status = await async_wait_for_task_completion(
            task_id,
            poll_interval=2,  # seconds between checks
            max_attempts=60   # maximum number of status checks
        )
```

#### Fetching File Content

```python
file_id = "file_12345"
document = await async_fetch_file(file_id)
```

#### Deleting a File

```python
file_id = "file_12345"
success = await async_delete_file(file_id)
```

### Vector Store API Usage

#### Creating a Vector Store

```python
result = await async_create_vectorstore(
    name="My Knowledge Base",
    description="Collection of research papers",
    file_ids=["file_12345", "file_67890"],  # optional
    custom_id="my-kb-id",  # optional
    metadata={"domain": "research", "project": "AI study"}  # optional
)
```

#### Querying a Vector Store

```python
results = await async_query_vectorstore(
    vector_store_id="vs_12345",
    query="machine learning techniques",
    top_k=5,  # number of results to return
    filters={"domain": "research"}  # optional filters
)
```

#### Adding Files to a Vector Store

```python
result = await async_join_files_to_vectorstore(
    vector_store_id="vs_12345",
    file_ids=["file_12345", "file_67890"]
)
```

## Available Example Scripts

- `hello-async.py`: Demonstrates basic interaction with the API using SDK
- `create-files.py`: Upload, manage, and delete files using SDK
- `create-vectorstore.py`: Create and manage vector stores using SDK
- `hello-sse-stream.py`: Stream responses with server-sent events using SDK
- `hello-sse-json.py`: Display JSON events from stream in a formatted view

## API Functions (SDK-Based)

### Response API

The SDK provides these key functions for the Response API:

- `async_create_response()`: Create a new response asynchronously
- `async_fetch_response()`: Fetch a response by ID
- `astream_response()`: Stream a response with server-sent events

### Vector Store API

For vector stores, the SDK provides:

- `async_create_vectorstore()`: Create a new vector store
- `async_get_vectorstore()`: Get details of a vector store
- `async_query_vectorstore()`: Search a vector store
- `async_join_files_to_vectorstore()`: Add files to a vector store
- `async_delete_vectorstore()`: Delete a vector store

### File API

For file operations, the SDK provides:

- `async_upload_file()`: Upload a file to the server
- `async_fetch_file()`: Get file details
- `async_delete_file()`: Delete a file
- `async_wait_for_task_completion()`: Wait for a file processing task to complete

## Server Configuration

All scripts support the following server configuration methods:

1. Set via environment variable:

   ```bash
   export KNOWLEDGE_FORGE_URL="http://server:port"
   ```

2. Specify via command-line argument:

   ```bash
   ./script.py --server http://server:port
   ```

3. Default (if not specified): `http://localhost:9999`

## Troubleshooting

### Common Issues and Solutions

#### Module Import Errors

**Problem**: `python -m forge_cli` fails with "No module named forge_cli"

**Solution**: Ensure you're running the command from the correct directory:

```bash
# WRONG - running from project root
cd /path/to/forge-cli
python -m forge_cli --chat  # ❌ This will fail

# CORRECT - running from src directory  
cd /path/to/forge-cli/src
python -m forge_cli --chat  # ✅ This works
```

#### Chat Mode Response Issues  

**Problem**: Messages appear twice or responses disappear

**Solution**: This was fixed in the v2 display system. Ensure you're using the latest version. If issues persist, try debug mode:

```bash
python -m forge_cli --chat --debug
```

#### Connection Issues

**Problem**: "Connection refused" or timeout errors

**Solutions**:

1. Verify the Knowledge Forge server is running:

   ```bash
   curl http://localhost:9999/health  # or your server URL
   ```

2. Check your server URL setting:

   ```bash
   python -m forge_cli --server http://your-server:port --chat
   ```

3. Set environment variable:

   ```bash
   export KNOWLEDGE_FORGE_URL=http://your-server:port
   ```

#### Vector Store Not Found

**Problem**: "Vector store not found" errors

**Solution**: Verify your vector store ID exists:

```bash
# Use debug mode to see detailed error information
python -m forge_cli --debug --vec-id your-vec-id -q "test"
```

#### Missing Rich UI Features

**Problem**: Plain text output instead of rich formatting

**Solutions**:

1. Install rich library:

   ```bash
   pip install rich
   ```

2. Force rich mode if terminal detection fails:

   ```bash
   python -m forge_cli --debug --chat  # Debug shows which display is selected
   ```

### Debug Mode

Enable debug mode for detailed troubleshooting information:

```bash
python -m forge_cli --debug [other-options]
```

Debug mode shows:

- Event types and data during streaming
- Display strategy selection
- API request/response details
- Error stack traces

### Getting Help

For additional help:

- Use the built-in help: `python -m forge_cli --help`
- In chat mode, type `/help` for available commands
- Check the server logs for API-related issues

## Development Guidelines

When creating new command-line tools:

1. **Always use the SDK** for all API interactions
2. Use the subcommand pattern for scripts with multiple operations
3. Follow consistent error handling patterns
4. Use type annotations and provide comprehensive documentation
5. Include helpful usage examples in script docstrings
6. Make scripts executable with proper shebang lines
7. Prefer environment variables for configuration where possible
8. Always use the async functions from the SDK

## Streaming Support

For streaming responses, the SDK provides:

1. `astream_response()`: Yields events as they arrive from the server
2. `async_create_response()` with callback: For processing events with a callback function

See `hello-sse-stream.py` and `hello-sse-advanced.py` for examples.

## Authentication

The Knowledge Forge API may require OpenAI API key authentication for some functionalities. The commands handle this by:

1. Looking for an API key in the environment variable `OPENAI_API_KEY`
2. If not found, trying to load it from `~/.openai-api-key` file
3. Warning the user if no API key is found

## Running Command Examples

All commands should be run with the following pattern:

```bash
# Set the Python path
PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge

# Run the command with uv
uv run -m commands.<command_name> [arguments]
```

For example:

```bash
PYTHONPATH=/Users/junix/knowledge-forge-office/knowledge_forge uv run -m commands.hello-async
```

Alternatively, you can run the scripts directly:

```bash
cd /Users/junix/knowledge-forge-office/commands
./hello-async.py
```

## Search Functionality Testing

This section covers how to test the main search functionalities provided by the Knowledge Forge API.

### File Search (`hello-file-search.py`)

Search through vectorstores using semantic search with AI-powered responses.

**Features**:

- Searches through vectorstores using semantic search
- Displays search annotations/citations with file references
- Shows search query timing and results count
- Supports both streaming and snapshot-based event processing

**Testing**:

```bash
# Basic file search
uv run commands/hello-file-search.py -q "What information is in these documents?"

# With specific vectorstore IDs
uv run commands/hello-file-search.py --vec-id vec_id1 vec_id2 -q "Your question"

# With debug mode for detailed output
uv run commands/hello-file-search.py --debug -q "Search query"

# Example with real vectorstore ID
uv run commands/hello-file-search.py --vec-id a1b2c3d4-e5f6-7890-abcd-ef1234567890 -q '云学堂的报销流程是什么？'
```

### Web Search (`hello-web-search.py`)

Integrate web search capabilities into AI responses for current information.

**Features**:

- Integrates web search capabilities into AI responses
- Supports location-based search customization
- Configurable search context size (low, medium, high)
- Server-Sent Events (SSE) streaming for real-time results

**Testing**:

```bash
# Basic web search
uv run commands/hello-web-search.py -q "What was positive news today?"

# With location settings
uv run commands/hello-web-search.py --country US --city "San Francisco" -q "local weather"

# With search context size
uv run commands/hello-web-search.py --search-context high -q "detailed analysis query"

# With debug mode
uv run commands/hello-web-search.py --debug -q "current events"
```

### File Reader (`hello-file-reader.py`)

Read and analyze uploaded files by file ID with AI processing.

**Features**:

- Reads content from uploaded files using file IDs
- Supports multiple file IDs in a single query
- Two streaming methods: callback-based and async iterator-based
- Displays detailed file information (title, filename, size, type)
- Rich terminal output with markdown support

**Testing**:

```bash
# Basic file reading
uv run commands/hello-file-reader.py -q "Summarize this document"

# Multiple files with specific model
uv run commands/hello-file-reader.py --file-id file1 file2 --model qwen-max -q "Compare these documents"

# Info mode (show file details only)
uv run commands/hello-file-reader.py --info --file-id file_id

# Using callback streaming method
uv run commands/hello-file-reader.py --method callback -q "Extract key points"

# With debug mode
uv run commands/hello-file-reader.py --debug --file-id file_id -q "Analyze this file"
```

### Vector Store Search (`query-vectorstore.py`)

Direct vector store querying without AI model processing for raw search results.

**Features**:

- Direct vector store querying without AI model
- Returns ranked search results with scores
- Supports result filtering
- Rich terminal display with formatted output

**Testing**:

```bash
# Query existing vectorstore
uv run commands/query-vectorstore.py -q "search query" --vec-id vec_store_id

# With custom parameters
uv run commands/query-vectorstore.py -q "query" --top-k 5 --vec-id custom_id

# With debug output
uv run commands/query-vectorstore.py --debug -q "search terms" --vec-id vec_store_id
```

### Complete File Search Flow (`simple-flow-filesearch.py`)

End-to-end workflow: upload file → create vectorstore → join file → query with AI.

**Features**:

- Complete end-to-end workflow
- Uploads file → Creates vectorstore → Joins file → Queries with AI
- Supports streaming responses
- Integrates file search tool for AI-powered answers

**Testing**:

```bash
# Complete flow with question
uv run commands/simple-flow-filesearch.py -f document.pdf -n "My Collection" -q "What is this about?"

# Without question (just setup)
uv run commands/simple-flow-filesearch.py -f document.pdf -n "My Collection"

# With custom effort level
uv run commands/simple-flow-filesearch.py -f doc.pdf -n "Collection" -q "Query" --effort high

# With debug mode
uv run commands/simple-flow-filesearch.py --debug -f document.pdf -n "Test Collection" -q "Analyze this document"
```

### Create and Query Workflow (`create-and-query-vectorstore.py`)

Complete workflow for creating vectorstore and querying it.

**Testing**:

```bash
# Full workflow: create store, upload file, join, query
uv run commands/create-and-query-vectorstore.py -f document.pdf -q "search query"

# With custom collection name
uv run commands/create-and-query-vectorstore.py -f document.pdf -n "Research Papers" -q "machine learning"
```

### Common Testing Options

All search tools support these common options:

- `--debug` or `-d`: Shows detailed event information and API responses
- `--json`: JSON output for programmatic use (where available)
- `--no-color`: Disable colored output
- `--quiet`: Minimal output
- `--throttle N`: Add N milliseconds delay between tokens (for streaming)

### Environment Setup for Testing

Before running any search commands, ensure:

1. **Server is running**: The Knowledge Forge server should be running at `http://localhost:9999` (or set `KNOWLEDGE_FORGE_URL`)
2. **Dependencies installed**: Use `uv` to manage dependencies
3. **Environment variables** (optional):

   ```bash
   export KNOWLEDGE_FORGE_URL=http://localhost:9999
   export OPENAI_API_KEY=your-api-key  # for some functionalities
   ```

### Prerequisites for File-based Searches

- **File Search**: Requires existing vectorstore IDs with indexed documents
- **File Reader**: Requires uploaded file IDs
- **Simple Flow**: Requires PDF/document files to upload
- **Web Search**: Requires internet connectivity and may need API keys
