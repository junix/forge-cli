# Knowledge Forge Commands - SDK and Command Line Tools

## Overview

This directory contains the official command-line tools and SDK for interacting with the Knowledge Forge API. These tools provide a comprehensive interface for file uploads, vector store management, AI-powered question answering, and streaming responses.

## Import Conventions

**IMPORTANT: All scripts in this directory should use relative imports to import the local `sdk.py` module.**

```python
# Correct - relative import from local directory
from sdk import async_create_response, astream_response

# WRONG - absolute imports (causes import conflicts)  
from commands.sdk import async_create_response
```

## Architecture

### SDK-First Design (ADR-001)

All command-line tools follow a **SDK-first approach**:

- **No Direct API Calls**: All tools MUST use the centralized SDK (`sdk.py`) 
- **Async/Await Pattern**: All API operations use Python's async/await for optimal performance
- **Module Execution**: Commands run as `uv run -m commands.<command_name>`
- **Environment Variables**: Configuration via `KNOWLEDGE_FORGE_URL` and `OPENAI_API_KEY`

### Core Components

```
commands/
├── sdk.py                      # Official Python SDK for Knowledge Forge API
├── cli.py                      # Simple CLI with rich formatting  
├── cli_refactored.py           # Refactored CLI with markdown support
├── hello-async.py              # Basic async SDK usage example
├── hello-file-search.py        # Advanced file search with citations
├── hello-web-search.py         # Web search capabilities
├── hello-file-reader.py        # File reading and analysis
├── simple-flow.py              # End-to-end workflow demonstration
├── create-vectorstore.py       # Vector store management
├── create-files.py             # File upload and management
└── ADR-*.md                    # Architecture Decision Records
```

## SDK API Reference

The `sdk.py` module provides a comprehensive async API for all Knowledge Forge operations:

### Response API

```python
from sdk import async_create_response, astream_response, async_fetch_response

# Create a response
response = await async_create_response(
    input_messages="Your query here",
    model="qwen-max-latest", 
    effort="low",  # "low", "medium", "high"
    temperature=0.7,
    max_output_tokens=1000
)

# Stream a response  
async for event_type, event_data in astream_response(
    input_messages="Tell me about Knowledge Forge",
    model="qwen-max-latest"
):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="", flush=True)
    elif event_type == "done":
        break

# Fetch by ID
response = await async_fetch_response(response_id)
```

### File API

```python
from sdk import async_upload_file, async_fetch_file, async_delete_file

# Upload file
result = await async_upload_file(
    path="/path/to/file.pdf",
    purpose="general",  # or "qa"
    custom_id="my-file-id",  # optional
    skip_exists=False
)

# Wait for processing
if result.get("task_id"):
    final_status = await async_wait_for_task_completion(
        result["task_id"],
        poll_interval=2,
        max_attempts=60
    )

# Fetch file content
document = await async_fetch_file(file_id)

# Delete file
success = await async_delete_file(file_id)
```

### Vector Store API

```python
from sdk import (
    async_create_vectorstore, 
    async_query_vectorstore,
    async_join_files_to_vectorstore
)

# Create vector store
result = await async_create_vectorstore(
    name="My Knowledge Base",
    description="Research papers collection",
    file_ids=["file_123", "file_456"],  # optional
    custom_id="my-kb-id",  # optional
    metadata={"domain": "research"}  # optional
)

# Query vector store  
results = await async_query_vectorstore(
    vector_store_id="vs_12345",
    query="machine learning techniques", 
    top_k=5,
    filters={"domain": "research"}  # optional
)

# Add files to existing vector store
result = await async_join_files_to_vectorstore(
    vector_store_id="vs_12345",
    file_ids=["file_789", "file_012"]
)
```

## Command Line Tools

### Basic Usage Examples

```bash
# Set environment
export KNOWLEDGE_FORGE_URL=http://localhost:9999
export PYTHONPATH=/path/to/knowledge-forge-office/knowledge_forge

# Basic async example
uv run -m commands.hello-async

# File search with citations (ADR-003)
uv run -m commands.hello-file-search -q "What information is in these documents?"
uv run -m commands.hello-file-search --vec-id vec_123 vec_456 -q "Your question"

# Web search
uv run -m commands.hello-web-search -q "What was positive news today?"
uv run -m commands.hello-web-search --country US --city "San Francisco" -q "local weather"

# File analysis
uv run -m commands.hello-file-reader --file-id file_123 -q "Summarize this document"

# End-to-end workflow  
uv run -m commands.simple-flow -f document.pdf -n "My Collection" -q "What is this about?"
```

### Advanced Features

#### File Search with Citations (ADR-003)

The file search tool implements a sophisticated citation system:

```bash
# Rich mode with live display
uv run -m commands.hello-file-search --vec-id vs_123 -q "云学堂的报销流程是什么？"

# Debug mode for troubleshooting
uv run -m commands.hello-file-search --debug -q "search query"

# JSON output for programmatic use
uv run -m commands.hello-file-search --json -q "query" --vec-id vs_123
```

**Features:**
- **Real-time citation display**: Shows source references as [1], [2], etc.
- **Tabular reference format**: Markdown table with Citation | Document | Page | File ID
- **Snapshot-based processing**: Handles complete response snapshots efficiently
- **Rich terminal support**: Live updating display with progress indicators

#### Reasoning Display (ADR-002)

All tools support reasoning/thinking display:

```python
# Reasoning events are handled automatically
# Shows "🤔 Thinking:" process in real-time
# Supports multiple event formats for compatibility
```

### Configuration Options

All commands support these common options:

```bash
--debug, -d          # Show detailed event information  
--no-color          # Disable colored output
--json              # JSON output for machine parsing
--quiet, -Q         # Minimal output
--throttle N        # Add N ms delay between tokens
--server URL        # Override server URL
```

## Environment Setup

### Prerequisites

```bash
# Install dependencies
pip install aiohttp rich loguru colorama

# Set required environment variables
export PYTHONPATH=/path/to/knowledge-forge-office/knowledge_forge
export KNOWLEDGE_FORGE_URL=http://localhost:9999  # optional, defaults to localhost
export OPENAI_API_KEY=your-api-key  # optional, for some functionalities
```

### Running Commands

Two execution patterns are supported:

```bash
# Method 1: Module execution (recommended)
cd /path/to/knowledge-forge-office/knowledge_forge
uv run -m commands.hello-async

# Method 2: Direct execution
cd /path/to/knowledge-forge-office/commands  
./hello-async.py
```

## Development Guidelines

### Creating New Commands

When creating new command-line tools:

1. **Always use the SDK** for all API interactions
2. **Follow async patterns** for all I/O operations
3. **Use consistent error handling** via SDK functions
4. **Include comprehensive argument parsing** with help text
5. **Support common options** (--debug, --json, --no-color)
6. **Provide usage examples** in docstrings
7. **Add proper shebang** lines for direct execution

### Example Command Template

```python
#!/usr/bin/env python3
"""
Example command demonstrating best practices.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add current directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from sdk import async_create_response

async def main():
    parser = argparse.ArgumentParser(description="Example command")
    parser.add_argument("--query", "-q", required=True, help="Query to process")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    try:
        response = await async_create_response(
            input_messages=args.query,
            model="qwen-max-latest"
        )
        
        if response:
            print(f"Response: {response.get('id')}")
        else:
            print("No response received")
            
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Streaming and Event Handling

### Event Types

Common event types in the streaming API:

```python
# Response lifecycle
"response.created"              # Response initialized
"response.in_progress"          # Processing started
"response.output_text.delta"    # Text content streaming
"response.output_text.done"     # Text complete
"response.completed"            # Response finished
"done"                          # Stream closed

# File search events  
"response.file_search_call.searching"    # Search started
"response.file_search_call.completed"    # Search finished

# Reasoning events (ADR-002)
"response.output_item.added"             # Reasoning/thinking content
```

### Streaming Patterns

Two streaming approaches are supported:

```python
# Method 1: Async iterator (recommended)
async for event_type, event_data in astream_response(messages):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="", flush=True)

# Method 2: Callback-based
async def stream_callback(event):
    if event["type"] == "response.output_text.delta":
        print(event["data"]["text"], end="", flush=True)

response = await async_create_response(
    input_messages=messages,
    callback=stream_callback
)
```

## Testing and Debugging

### Debug Tools

```bash
# Event debugging
uv run -m commands.debug-event-logger  # Log all events with timestamps

# Multi-tool testing  
uv run -m commands.demo-multi-tools-concept  # Test multiple tools

# API debugging
uv run -m commands.hello-async --debug  # Show detailed API calls
```

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` is set correctly
2. **Connection Errors**: Verify `KNOWLEDGE_FORGE_URL` points to running server
3. **Missing Dependencies**: Install required packages with `pip install`
4. **API Key Issues**: Set `OPENAI_API_KEY` if required by specific models

## Architecture Decision Records

This directory includes comprehensive ADRs documenting design decisions:

- **[ADR-001](ADR-001-commandline-design.md)**: Command-line interface design principles
- **[ADR-002](ADR-002-reasoning-event-handling.md)**: Reasoning event handling in streaming
- **[ADR-003](ADR-003-file-search-annotation-display.md)**: File search citation display architecture
- **[ADR-004](ADR-004-snapshot-based-streaming-design.md)**: Snapshot-based streaming approach

## Integration with Knowledge Forge

These command-line tools serve as:

1. **Reference Implementations**: Show best practices for using the Knowledge Forge API
2. **Development Tools**: Enable rapid testing and prototyping
3. **User Interface**: Provide accessible command-line access to Knowledge Forge features  
4. **SDK Examples**: Demonstrate proper usage of the async SDK

The tools integrate seamlessly with the broader Knowledge Forge ecosystem while maintaining independence for standalone usage.

## Support and Troubleshooting

### Getting Help

```bash
# Command-specific help
uv run -m commands.<command_name> --help

# Version information
uv run -m commands.hello-file-search --version
```

### Common Error Resolution

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'sdk'` | Set `PYTHONPATH` correctly and use relative imports |
| `Connection refused` | Ensure Knowledge Forge server is running |
| `No response received` | Check server logs and API endpoint |
| `JSON decode error` | Enable `--debug` to see raw API responses |

For additional support, refer to the Knowledge Forge documentation and the ADR files in this directory.