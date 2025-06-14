# Scripts Module - Example Scripts and Utilities

## Overview

The scripts module contains a comprehensive collection of example scripts, utilities, and test programs that demonstrate how to use the Forge CLI SDK and components. These scripts serve as both educational resources and practical tools for common tasks, showcasing best practices and various use cases.

## Directory Structure

```
scripts/
├── __init__.py                              # Module initialization
│
├── Core Examples (Basic SDK Usage)
│   ├── hello-async.py                       # Basic async API usage
│   ├── hello-file-search.py                 # File search demonstrations
│   ├── hello-web-search.py                  # Web search examples
│   ├── hello-multi-tools.py                 # Multi-tool combinations
│   ├── hello-file-reader.py                 # File reading operations
│   └── simple-flow.py                       # End-to-end workflows
│
├── Vector Store Management
│   ├── create-vectorstore.py                # Create vector stores
│   ├── query-vectorstore.py                 # Query vector stores
│   ├── join-file.py                         # Add files to stores
│   └── test-vectorstore-operations.py       # Comprehensive testing
│
├── Debug and Development Tools
│   ├── debug-all-events.py                  # Event stream debugging
│   ├── sse-json-viewer.py                   # SSE stream viewer
│   ├── mock_server.py                       # Mock API server
│   └── event-type-analyzer.py               # Analyze event patterns
│
├── Testing and Validation
│   ├── rag-test-simple.py                   # Simple RAG tests
│   ├── rag-test-multi-vectorstores.py       # Multi-store tests
│   ├── rag-test-citations.py                # Citation testing
│   ├── test_chat_mode.py                    # Chat mode tests
│   └── test-dataset.py                      # Dataset validation
│
└── Advanced Examples
    ├── streaming-with-callbacks.py          # Custom callbacks
    ├── parallel-processing.py               # Concurrent operations
    └── custom-processor-example.py          # Custom processors
```

## Script Categories

### Core Examples - Basic SDK Usage

#### hello-async.py

**Purpose**: Demonstrates basic async SDK usage and streaming responses.

**Key Features**:

- Async/await patterns
- Stream handling basics
- Error handling
- Token usage tracking

**Usage**:

```bash
python -m forge_cli.scripts.hello-async -q "What is machine learning?"
```

**Code Structure**:

```python
async def main():
    # Basic streaming
    async for event_type, event_data in astream_response(
        input_messages="Your question",
        model="gpt-4"
    ):
        if event_type == "response.output_text.delta":
            print(event_data["text"], end="", flush=True)
```

#### hello-file-search.py

**Purpose**: Complete file search implementation with citations.

**Key Features**:

- Vector store integration
- Citation formatting
- Rich display options
- Multi-store queries

**Usage**:

```bash
python -m forge_cli.scripts.hello-file-search \
    --vec-id vs_123 \
    -q "What information is available?"
```

**Advanced Options**:

```bash
# Multiple vector stores
--vec-id vs_123 vs_456

# Debug mode
--debug

# JSON output
--json
```

#### hello-web-search.py

**Purpose**: Web search integration with location awareness.

**Key Features**:

- Location-based search
- Result formatting
- URL citation handling
- Search filters

**Usage**:

```bash
python -m forge_cli.scripts.hello-web-search \
    -q "Latest AI news" \
    --country US \
    --city "San Francisco"
```

#### hello-multi-tools.py

**Purpose**: Demonstrates using multiple tools together.

**Key Features**:

- Tool combination strategies
- Unified result handling
- Citation merging
- Performance optimization

**Usage**:

```bash
python -m forge_cli.scripts.hello-multi-tools \
    -t file-search \
    -t web-search \
    --vec-id vs_123 \
    -q "Compare internal docs with industry trends"
```

#### simple-flow.py

**Purpose**: End-to-end workflow from file upload to query.

**Workflow**:

1. Upload file
2. Create vector store
3. Add file to store
4. Query the store
5. Display results

**Usage**:

```bash
python -m forge_cli.scripts.simple-flow \
    -f document.pdf \
    -n "My Knowledge Base" \
    -q "Summarize this document"
```

### Vector Store Management Scripts

#### create-vectorstore.py

**Purpose**: Create and configure vector stores.

**Features**:

- Custom metadata
- File initialization
- Batch operations
- Status monitoring

**Usage**:

```bash
python -m forge_cli.scripts.create-vectorstore \
    --name "Research Papers" \
    --description "ML research collection" \
    --files file_123 file_456 \
    --custom-id "research_v1"
```

#### query-vectorstore.py

**Purpose**: Advanced vector store querying.

**Features**:

- Filter support
- Relevance scoring
- Result pagination
- Export options

**Usage**:

```bash
python -m forge_cli.scripts.query-vectorstore \
    --vec-id vs_123 \
    --query "neural networks" \
    --top-k 10 \
    --filters '{"category": "research"}'
```

#### join-file.py

**Purpose**: Add files to existing vector stores.

**Features**:

- Batch file addition
- Progress tracking
- Error handling
- Verification

**Usage**:

```bash
python -m forge_cli.scripts.join-file \
    --vec-id vs_123 \
    --file-ids file_789 file_012 \
    --wait  # Wait for processing
```

### Debug and Development Tools

#### debug-all-events.py

**Purpose**: Comprehensive event stream debugging.

**Features**:

- All event capture
- Event filtering
- Timing analysis
- State tracking

**Usage**:

```bash
python -m forge_cli.scripts.debug-all-events \
    -q "Test query" \
    --filter "file_search" \
    --save-events events.json
```

**Output Example**:

```
[0.001s] response.created {"id": "resp_123"}
[0.102s] response.output_item.added {"type": "reasoning"}
[0.203s] response.file_search_call.searching {"query": "test"}
[1.234s] response.file_search_call.completed {"results": 5}
```

#### sse-json-viewer.py

**Purpose**: Real-time SSE stream visualization.

**Features**:

- Raw event display
- JSON formatting
- Event statistics
- Performance metrics

**Usage**:

```bash
python -m forge_cli.scripts.sse-json-viewer \
    --url "http://localhost:9999/v1/response" \
    --pretty  # Pretty print JSON
```

#### mock_server.py

**Purpose**: Mock Knowledge Forge API server for testing.

**Features**:

- Configurable responses
- Event simulation
- Error injection
- Performance testing

**Usage**:

```bash
# Start mock server
python -m forge_cli.scripts.mock_server \
    --port 9999 \
    --scenario "file_search_success"

# Use with scripts
KNOWLEDGE_FORGE_URL=http://localhost:9999 \
python -m forge_cli.scripts.hello-file-search -q "test"
```

### Testing and Validation Scripts

#### rag-test-simple.py

**Purpose**: Basic RAG (Retrieval-Augmented Generation) testing.

**Test Cases**:

- Document retrieval accuracy
- Citation correctness
- Response relevance
- Performance benchmarks

**Usage**:

```bash
python -m forge_cli.scripts.rag-test-simple \
    --vec-id vs_test \
    --test-file tests/rag_cases.json
```

#### rag-test-multi-vectorstores.py

**Purpose**: Test queries across multiple vector stores.

**Features**:

- Cross-store queries
- Result deduplication
- Performance comparison
- Citation tracking

**Usage**:

```bash
python -m forge_cli.scripts.rag-test-multi-vectorstores \
    --vec-ids vs_123 vs_456 vs_789 \
    --queries "machine learning" "data science"
```

#### test_chat_mode.py

**Purpose**: Automated chat mode testing.

**Test Scenarios**:

- Command execution
- Conversation flow
- Error handling
- Session management

**Usage**:

```bash
python -m forge_cli.scripts.test_chat_mode \
    --test-script chat_test_script.txt \
    --validate-output
```

## Development Guidelines

### Creating New Scripts

#### Script Template

```python
#!/usr/bin/env python3
"""
Script Name: example-script.py
Purpose: Brief description of what the script does
Author: Your name
Date: Creation date
"""

import argparse
import asyncio
from typing import Optional

from forge_cli.sdk import async_create_response, astream_response
from forge_cli.config import SearchConfig
from forge_cli.logger import logger


async def main(args: argparse.Namespace) -> None:
    """Main script logic."""
    try:
        # Configure
        config = SearchConfig(
            model=args.model,
            debug=args.debug
        )
        
        # Execute
        result = await perform_operation(
            query=args.query,
            config=config
        )
        
        # Display
        print(f"Result: {result}")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        if args.debug:
            raise
        return 1
    
    return 0


async def perform_operation(query: str, config: SearchConfig) -> dict:
    """Perform the main operation."""
    # Implementation
    pass


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="Query to process"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model to use"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = asyncio.run(main(args))
    exit(exit_code or 0)
```

### Best Practices

1. **Imports**:
   - Use absolute imports from forge_cli
   - Group imports: stdlib, third-party, local

2. **Error Handling**:
   - Graceful error messages for users
   - Debug mode for full tracebacks
   - Return appropriate exit codes

3. **Documentation**:
   - Clear docstrings
   - Usage examples in comments
   - Help text for all arguments

4. **Async Patterns**:
   - Use async/await consistently
   - Handle cancellation properly
   - Clean up resources

### Testing Scripts

#### Unit Testing

```python
# tests/test_scripts.py
import pytest
from unittest.mock import patch, AsyncMock

from forge_cli.scripts.hello_async import main, parse_args


@pytest.mark.asyncio
async def test_hello_async_basic():
    # Mock arguments
    args = parse_args(["-q", "test query"])
    
    # Mock SDK
    with patch("forge_cli.sdk.astream_response") as mock_stream:
        mock_stream.return_value = async_generator([
            ("response.output_text.delta", {"text": "Hello"}),
            ("done", {})
        ])
        
        # Run script
        result = await main(args)
        
        # Verify
        assert result == 0
        mock_stream.assert_called_once()
```

#### Integration Testing

```bash
# Test script with real API
python -m forge_cli.scripts.hello-async \
    -q "test" \
    --model "gpt-3.5-turbo" \
    --debug

# Test with mock server
python -m forge_cli.scripts.mock_server &
SERVER_PID=$!

KNOWLEDGE_FORGE_URL=http://localhost:9999 \
python -m forge_cli.scripts.hello-file-search \
    -q "test" \
    --vec-id vs_mock

kill $SERVER_PID
```

## Common Patterns

### Configuration Handling

```python
def build_config(args: argparse.Namespace) -> SearchConfig:
    """Build configuration from arguments."""
    config = SearchConfig()
    
    # Apply arguments
    if args.model:
        config.model = args.model
    
    if args.debug:
        config.debug = True
        logger.setLevel("DEBUG")
    
    if args.json:
        config.json_output = True
    
    return config
```

### Stream Processing

```python
async def process_stream(stream, handler):
    """Generic stream processor."""
    try:
        async for event_type, event_data in stream:
            # Process based on type
            if event_type.startswith("response."):
                await handler.handle_response_event(
                    event_type, event_data
                )
            elif event_type == "done":
                break
                
    except asyncio.CancelledError:
        logger.info("Stream cancelled")
        raise
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise
```

### Result Formatting

```python
def format_results(results: List[dict], format_type: str) -> str:
    """Format results based on output type."""
    if format_type == "json":
        return json.dumps(results, indent=2)
    
    elif format_type == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(
            output, 
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()
    
    else:  # Plain text
        lines = []
        for i, result in enumerate(results, 1):
            lines.append(f"{i}. {result['title']}")
            lines.append(f"   {result['snippet']}")
        return "\n".join(lines)
```

## Performance Optimization

### Concurrent Operations

```python
async def parallel_queries(queries: List[str], config: SearchConfig):
    """Execute queries in parallel."""
    tasks = [
        process_query(query, config) 
        for query in queries
    ]
    
    results = await asyncio.gather(
        *tasks, 
        return_exceptions=True
    )
    
    # Handle results and errors
    for query, result in zip(queries, results):
        if isinstance(result, Exception):
            logger.error(f"Query '{query}' failed: {result}")
        else:
            yield query, result
```

### Batch Processing

```python
async def batch_process_files(file_ids: List[str], batch_size: int = 10):
    """Process files in batches."""
    for i in range(0, len(file_ids), batch_size):
        batch = file_ids[i:i + batch_size]
        
        # Process batch
        results = await process_file_batch(batch)
        
        # Yield results
        for file_id, result in zip(batch, results):
            yield file_id, result
        
        # Rate limiting
        await asyncio.sleep(1)
```

## Troubleshooting Guide

### Common Issues

1. **Import Errors**:

   ```bash
   # Ensure package is installed
   pip install -e .
   
   # Run as module
   python -m forge_cli.scripts.script_name
   ```

2. **Async Errors**:

   ```python
   # Always use asyncio.run() for main
   if __name__ == "__main__":
       asyncio.run(main())
   ```

3. **API Connection**:

   ```bash
   # Check server URL
   echo $KNOWLEDGE_FORGE_URL
   
   # Test connection
   curl $KNOWLEDGE_FORGE_URL/health
   ```

## Future Scripts

Planned additions:

1. **Benchmark Suite**: Performance testing scripts
2. **Migration Tools**: Data migration utilities
3. **Analytics Scripts**: Usage analysis and reporting
4. **Batch Processors**: Large-scale operations
5. **Integration Examples**: Third-party integrations

The scripts module serves as both a learning resource and a practical toolkit, demonstrating the full capabilities of the Forge CLI while providing ready-to-use utilities for common tasks.
