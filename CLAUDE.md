# Forge CLI - Modern Command Line Tools for Knowledge Forge API

## Overview

This project provides modern, modular command-line tools and SDK for interacting with the Knowledge Forge API. Built with Python 3.8+ and structured as a proper Python package, it offers comprehensive functionality for file uploads, vector store management, AI-powered question answering, and streaming responses.

## Project Structure

```
forge-cli/
├── src/forge_cli/              # Top-level package (use absolute imports)
│   ├── main.py                 # Main CLI entry point with rich UI
│   ├── sdk.py                  # Official Python SDK for Knowledge Forge API
│   ├── config.py               # Configuration management with Pydantic models
│   ├── chat.py                 # Interactive chat mode
│   ├── models/                 # Pydantic data models and types (use relative imports)
│   │   ├── __init__.py         # Model exports
│   │   ├── api.py              # API request/response models with validation
│   │   ├── conversation.py     # Chat conversation models with validation
│   │   ├── events.py           # Event type definitions with Pydantic
│   │   ├── output_types.py     # Response output types with validation
│   │   ├── state.py            # Stream state management models
│   │   ├── config.py           # Configuration models with validation
│   │   └── files.py            # File and vector store models
│   ├── processors/             # Event processors (use relative imports)
│   │   ├── base.py             # Base processor interface
│   │   ├── registry.py         # Processor registry
│   │   ├── reasoning.py        # Reasoning/thinking processor
│   │   ├── message.py          # Message processor with citations
│   │   └── tool_calls/         # Tool-specific processors (use relative imports)
│   │       ├── file_search.py  # File search tool processor
│   │       ├── web_search.py   # Web search tool processor
│   │       ├── file_reader.py  # File reader tool processor
│   │       └── document_finder.py # Document finder processor
│   ├── display/                # Display strategies (use relative imports)
│   │   ├── registry.py         # Display factory with v2 architecture
│   │   └── v2/                 # V2 event-based display architecture
│   │       ├── base.py         # Base display interface
│   │       ├── events.py       # Display event definitions
│   │       └── renderers/      # Pluggable renderers
│   │           ├── rich.py     # Rich terminal UI
│   │           ├── plain.py    # Plain text output
│   │           └── json.py     # JSON format output
│   ├── stream/                 # Stream handling (use relative imports)
│   │   └── handler.py          # Main stream processor
│   ├── chat/                   # Chat mode functionality (use relative imports)
│   │   ├── controller.py       # Chat session controller
│   │   └── commands.py         # Chat command system
│   └── scripts/                # Example scripts (use absolute imports)
│       ├── hello-async.py      # Basic async SDK usage
│       ├── hello-file-search.py # File search examples
│       ├── hello-web-search.py # Web search examples
│       ├── simple-flow.py      # End-to-end workflows
│       └── ...                 # Additional utility scripts
├── docs/adr/                   # Architecture Decision Records
├── pyproject.toml              # Python project configuration
└── README.md                   # Project documentation
```

## Pydantic Models and Validation

This project extensively uses **Pydantic v2** for data validation, serialization, and type safety. All API interactions, configuration management, and internal data structures use Pydantic models to ensure data integrity and provide excellent developer experience with automatic validation and clear error messages.

### Model Organization and Benefits

All Pydantic models are organized in the `models/` directory with specific purposes:

- **models/api.py** - API request/response models with validation rules
- **models/config.py** - Configuration models using pydantic-settings for environment management  
- **models/files.py** - File upload and vector store models with format validation
- **models/conversation.py** - Chat conversation models with message validation
- **models/events.py** - Event type definitions for stream processing
- **models/state.py** - Stream state management with type safety

### Key Validation Features

1. **Automatic Type Conversion** - Input data is automatically converted to correct types
2. **Field Validation** - Custom validators ensure data integrity (e.g., vector store ID format)
3. **Environment Integration** - Configuration automatically loads from environment variables
4. **Error Messages** - Clear, descriptive error messages for debugging
5. **Serialization** - Automatic JSON serialization for API communication
6. **Documentation** - Self-documenting models with field descriptions

### Type Safety Best Practices

**IMPORTANT**: Avoid using `Any` as type hints - it defeats the purpose of type safety and validation. Instead:

- Use specific types: `str`, `int`, `float`, `bool`, `datetime`
- Use generic types: `List[str]`, `Dict[str, int]`, `Optional[str]`
- Use Literal types: `Literal["low", "medium", "high"]` for enums
- Use Union types: `Union[str, int]` for multiple allowed types
- Create custom models: Define Pydantic models for complex nested data
- Use TypedDict: For dictionary structures with known keys

The `Any` type provides no validation, no IDE support, and no runtime type checking. It should only be used as a last resort when dealing with truly unknown external data that will be validated elsewhere.

### Error Handling Philosophy

**IMPORTANT**: Avoid defensive programming patterns that silently ignore or mask errors. This project follows a "fail-fast" approach:

- **Don't catch and ignore exceptions** - Let errors bubble up to reveal real issues
- **Don't use default fallbacks** for critical data - Invalid data should cause immediate failure
- **Don't suppress validation errors** - Pydantic validation failures indicate real problems
- **Don't use try/except blocks** to hide configuration or data issues
- **Prefer explicit validation** over implicit assumptions about data correctness

**Examples of what NOT to do:**
```python
# BAD: Defensive programming that hides errors
try:
    config = SearchConfig(**user_data)
except ValidationError:
    config = SearchConfig()  # Silent fallback masks the real issue

# BAD: Ignoring validation failures
def process_file(file_data):
    try:
        file_info = FileInfo(**file_data)
    except:
        return None  # Swallows all errors, including real bugs
```

**Examples of preferred approach:**
```python
# GOOD: Let validation errors bubble up
config = SearchConfig(**user_data)  # Will raise ValidationError if invalid

# GOOD: Explicit error handling with user feedback
try:
    file_info = FileInfo(**file_data)
except ValidationError as e:
    raise ValueError(f"Invalid file data: {e}") from e
```

Fast failure reveals problems early in development and prevents silent corruption of program state. Use Pydantic's validation to catch issues immediately rather than masking them with defensive code.

## Import Conventions

**IMPORTANT: Follow these import patterns based on directory level:**

### Top-Level Directory (`src/forge_cli/`)
Files at the top level use **absolute imports**:

```python
# In src/forge_cli/main.py
from forge_cli.sdk import astream_response, async_get_vectorstore
from forge_cli.config import SearchConfig
from forge_cli.display.base import BaseDisplay
from forge_cli.display.rich_display import RichDisplay
from forge_cli.stream.handler import StreamHandler
from forge_cli.processors.registry import initialize_default_registry
```

### Subdirectories (`models/`, `processors/`, `display/`, etc.)
Files in subdirectories use **relative imports**:

```python
# In src/forge_cli/processors/registry.py
from .base import BaseProcessor
from .reasoning import ReasoningProcessor
from .tool_calls.file_search import FileSearchProcessor

# In src/forge_cli/display/rich_display.py
from .base import BaseDisplay

# In src/forge_cli/processors/tool_calls/file_search.py
from ..base import BaseProcessor
from ...models.state import StreamState
```

### Scripts Directory (`scripts/`)
Scripts use **absolute imports** since they are standalone utilities:

```python
# In src/forge_cli/scripts/hello-async.py
from forge_cli.sdk import async_create_response, astream_response
from forge_cli.config import SearchConfig
```

## Installation & Setup

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

## Usage

### Command Line Interface

The main CLI provides a rich, interactive interface with multiple tools:

```bash
# Run the main CLI
forge-cli

# Or using Python module
python -m forge_cli

# Basic file search
forge-cli -q "What information is in these documents?" --vec-id your-vector-store-id

# Web search
forge-cli -t web-search -q "Latest AI news"

# Interactive chat mode
forge-cli --chat

# Multiple tools with location context
forge-cli -t file-search -t web-search --vec-id vs_123 --country US --city "San Francisco"
```

### SDK API Reference

The `sdk.py` module provides a comprehensive async API for all Knowledge Forge operations:

```python
from forge_cli.sdk import async_create_response, astream_response, async_fetch_response

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

#### File API

```python
from forge_cli.sdk import async_upload_file, async_fetch_file, async_delete_file

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

#### Vector Store API

```python
from forge_cli.sdk import (
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

## Architecture

### Modular Design Philosophy

The project follows modern software engineering principles:

1. **Single Responsibility**: Each module has one clear purpose
2. **Strategy Pattern**: Multiple display and processing strategies
3. **Registry Pattern**: Dynamic processor selection
4. **Stream Processing**: Event-driven architecture for real-time responses
5. **Type Safety**: Comprehensive type annotations throughout

### Key Components

#### Stream Processing
Events from the Knowledge Forge API are processed through a modular pipeline:
```
API Event Stream → StreamHandler → Event Router → Processor Registry → Display Strategy
```

#### Processor System
Each output type has a dedicated processor:
- `ReasoningProcessor`: Handles thinking/analysis blocks
- `FileSearchProcessor`: Processes file search tool calls
- `WebSearchProcessor`: Handles web search operations
- `MessageProcessor`: Manages final responses with citations

#### Display Strategies
Multiple output formats are supported:
- `RichDisplay`: Rich terminal UI with live updates
- `PlainDisplay`: Simple text output
- `JsonDisplay`: Machine-readable JSON format

## Example Scripts

The `scripts/` directory contains practical examples:

```bash
# Basic async SDK usage
python -m forge_cli.scripts.hello-async

# File search with citations
python -m forge_cli.scripts.hello-file-search -q "What information is in these documents?"

# Web search capabilities
python -m forge_cli.scripts.hello-web-search -q "Latest AI developments"

# File reading and analysis
python -m forge_cli.scripts.hello-file-reader --file-id file_123 -q "Summarize this document"

# End-to-end workflow
python -m forge_cli.scripts.simple-flow -f document.pdf -n "My Collection" -q "What is this about?"
```

### Advanced Features

#### Interactive Chat Mode
The CLI supports full conversational mode with context preservation:

```bash
# Start interactive chat
forge-cli --chat

# Chat with specific tools enabled
forge-cli --chat -t file-search --vec-id vs_123

# Available chat commands:
# /help - Show available commands
# /save - Save conversation to file
# /load - Load previous conversation
# /tools - Manage enabled tools
# /model - Change AI model
# /clear - Clear conversation history
```

#### File Search with Citations
Advanced file search with sophisticated citation tracking:

```bash
# File search with rich UI
forge-cli --vec-id vs_123 -q "What information is in these documents?"

# Multiple vector stores
forge-cli --vec-id vs_123 vs_456 -q "Your question"

# Debug mode for troubleshooting
forge-cli --debug -q "search query"
```

**Features:**
- Real-time citation display as [1], [2], etc.
- Markdown table format: Citation | Document | Page | File ID
- Live updating display with progress indicators
- Support for multiple vector stores

#### Web Search Integration
Location-aware web search capabilities:

```bash
# Basic web search
forge-cli -t web-search -q "Latest AI news"

# Location-specific search
forge-cli -t web-search --country US --city "San Francisco" -q "local weather"
```

#### Multi-Tool Support
Combine multiple tools in a single query:

```bash
# File search + Web search
forge-cli -t file-search -t web-search --vec-id vs_123 -q "Compare internal docs with latest industry trends"
```

### Configuration Options

All commands support these common options:

```bash
--debug, -d          # Show detailed event information  
--no-color           # Disable colored output
--json               # JSON output for machine parsing
--quiet, -Q          # Minimal output
--throttle N         # Add N ms delay between tokens
--server URL         # Override server URL
--chat, -i           # Start interactive chat mode
--effort LEVEL       # Set effort level (low/medium/high)
--model MODEL        # Specify AI model to use
```

## Development

### Creating New Tools

When extending the CLI with new functionality:

1. **Add processors** for new output types in `processors/` (use relative imports)
2. **Register processors** in `processors/registry.py` (use relative imports within processors)
3. **Add display methods** if needed in `display/` modules (use relative imports)
4. **Update configuration** in `config.py` for new options (use absolute imports from top-level)
5. **Create example scripts** in `scripts/` directory (use absolute imports)

### Import Guidelines for Development

- **Top-level files** (`main.py`, `sdk.py`, `config.py`): Use absolute imports (`from forge_cli.module import ...`)
- **Subdirectory files** (`processors/`, `display/`, `models/`): Use relative imports (`.module`, `..parent.module`)
- **Scripts**: Use absolute imports since they're standalone utilities
- **Cross-package imports**: Always use absolute imports when importing from other top-level modules

### Testing

```bash
# Run example scripts
python -m forge_cli.scripts.hello-async

# Test with debug mode
forge-cli --debug -t file-search --vec-id vs_123 -q "test query"

# Test chat mode
forge-cli --chat --debug
```

### Extending the SDK

The SDK is designed for extension. Add new API endpoints by:

1. Adding async functions following the `async_<action>_<resource>` pattern
2. Using consistent error handling and return types
3. Adding comprehensive docstrings and type annotations

## Dependencies

Core dependencies (automatically managed by `uv` or `pip`):

- `aiohttp>=3.8.0` - Async HTTP client for API communication
- `rich>=12.0.0` - Rich terminal UI components
- `loguru>=0.6.0` - Advanced logging capabilities
- `prompt-toolkit>=3.0.0` - Interactive command line features

Optional dependencies for enhanced functionality:
- `requests>=2.25.0` - Fallback HTTP client
- Development tools: `pytest`, `black`, `flake8`, `mypy`

## Streaming and Event Handling

The system processes real-time events from the Knowledge Forge API:

### Key Event Types

```python
# Response lifecycle
"response.created"              # Response initialized
"response.in_progress"          # Processing started
"response.output_text.delta"    # Text content streaming
"response.output_text.done"     # Text complete
"response.completed"            # Response finished
"done"                          # Stream closed

# Tool execution events  
"response.file_search_call.searching"    # File search started
"response.file_search_call.completed"    # File search finished
"response.web_search_call.searching"     # Web search started
"response.web_search_call.completed"     # Web search finished

# Reasoning/thinking events
"response.output_item.added"             # Reasoning content
```

### Streaming Implementation

```python
# Async iterator pattern (recommended)
async for event_type, event_data in astream_response(
    input_messages="Your query",
    model="qwen-max-latest"
):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="", flush=True)
    elif event_type == "done":
        break

# The stream handler automatically routes events to appropriate processors
```

## Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# CLI debug mode
forge-cli --debug -q "test query"

# Script debug mode  
python -m forge_cli.scripts.hello-async --debug
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Ensure proper package installation with `uv sync` or `pip install -e .` |
| Connection refused | Verify Knowledge Forge server is running at correct URL |
| No response received | Check server logs and API endpoint accessibility |
| JSON decode errors | Enable `--debug` to see raw API responses |
| Missing API key | Set `OPENAI_API_KEY` environment variable if required |

### Environment Verification

```bash
# Check installation
forge-cli --version

# Test basic functionality
forge-cli -q "Hello, world!" --debug

# Verify SDK import
python -c "from forge_cli.sdk import async_create_response; print('SDK OK')"
```

## Architecture Decision Records

The project includes comprehensive ADRs documenting design decisions:

- **[CLAUDE-001](docs/adr/CLAUDE-001-commandline-design.md)**: Command-line interface design principles
- **[CLAUDE-002](docs/adr/CLAUDE-002-reasoning-event-handling.md)**: Reasoning event handling in streaming
- **[CLAUDE-003](docs/adr/CLAUDE-003-file-search-annotation-display.md)**: File search citation display architecture
- **[CLAUDE-004](docs/adr/CLAUDE-004-snapshot-based-streaming-design.md)**: Snapshot-based streaming approach

## Contributing

This project serves as both a practical tool and reference implementation for the Knowledge Forge API. When contributing:

1. Follow the established modular architecture
2. Maintain comprehensive type annotations
3. Add tests for new functionality
4. Update documentation and ADRs as needed
5. Use the SDK for all API interactions

The codebase demonstrates modern Python practices and can serve as a template for building applications with the Knowledge Forge API.