# Forge CLI - Modern Command Line Tools for Knowledge Forge API

## Overview

This project provides modern, modular command-line tools and SDK for interacting with the Knowledge Forge API. Built with Python 3.8+ and structured as a proper Python package, it offers comprehensive functionality for file uploads, vector store management, AI-powered question answering, code analysis, and streaming responses.

## ✅ Migration to Typed-Only Architecture (Complete)

The project has completed its migration to a fully typed architecture with comprehensive type safety. See [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) for details. The system now uses:

```python
# Typed API (primary interface)
from forge_cli.sdk.typed_api import astream_typed_response, create_typed_request
from forge_cli.response.type_guards.output_items import is_file_search_call

request = create_typed_request(
    input_messages="Your query",
    tools=[{"type": "file_search", "vector_store_ids": ["vs_123"]}]
)

async for event_type, response in astream_typed_response(request):
    # Type-safe access with full IDE support
    if hasattr(response, 'output'):
        for item in response.output:
            if is_file_search_call(item):
                print(f"Searching: {item.queries}")
```

## 🏗️ V3 Response-Snapshot Display Architecture

The display system uses a V3 architecture based on response snapshots rather than event streaming, providing better consistency and easier testing. Key features:

- **Snapshot-based rendering**: Displays render complete response states
- **Pluggable renderers**: Easy to add new output formats
- **Type-safe styling**: Citation and content styling with type checking
- **Unified interface**: All renderers implement the same base interface

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
│   │   ├── code_analysis.py    # Models for code analysis results
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
│   │   │   ├── code_analyzer.py # Code analyzer tool processor
│   │       └── list_documents.py # List documents processor
│   ├── response/               # Response handling and type definitions
│   │   ├── __init__.py         # Response module exports
│   │   ├── _types/             # OpenAPI-generated types (do not edit manually)
│   │   │   ├── __init__.py     # Type exports
│   │   │   ├── response.py     # Response model definitions
│   │   │   ├── request.py      # Request model definitions
│   │   │   └── ...             # Additional generated types
│   │   ├── type_guards/        # Type guard functions for safe type narrowing
│   │   │   ├── __init__.py     # Type guard exports
│   │   │   ├── output_items.py # Output item type guards
│   │   │   ├── annotations.py  # Annotation type guards
│   │   │   └── events.py       # Event type guards
│   │   ├── utils.py            # Response utility functions
│   │   └── processor.py        # Response processing logic
│   ├── display/                # Display strategies (use relative imports)
│   │   ├── registry.py         # Display factory with v3 architecture
│   │   ├── v2/                 # V2 legacy event-based display (deprecated)
│   │   └── v3/                 # V3 snapshot-based display architecture (current)
│   │       ├── base.py         # Base display interface
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

### TypeGuard Functions for Type-Safe Code

The project uses **TypeGuard functions** (Python 3.10+) to enable proper type narrowing and eliminate defensive programming patterns. TypeGuards are located in `response/type_guards.py` and provide type-safe access to Response API objects.

**Benefits of TypeGuards:**

- **Type Safety**: Proper type narrowing ensures compile-time and runtime safety
- **IDE Support**: Full autocomplete and type hints within conditional blocks
- **Code Clarity**: Intent is clear - checking type, not defensive programming
- **Performance**: Simple string comparison, no runtime overhead

**Example Usage:**

```python
# GOOD: Using TypeGuard functions
from forge_cli.response.type_guards import is_file_search_call, is_message_item

# Type narrowing with full IDE support
if is_file_search_call(item):
    # Type checker knows item is ResponseFileSearchToolCall
    for query in item.queries:  # Full autocomplete!
        process_query(query)
    
    # Results are accessed through response methods
    # results = response.get_file_search_results(item.id)

# BAD: Defensive programming patterns to avoid
if hasattr(item, "queries") and item.queries:  # No type information
    for query in item.queries:  # No autocomplete
        process_query(query)

# BAD: Using cast without verification
from typing import cast
file_search = cast(ResponseFileSearchToolCall, item)  # Unsafe assertion
```

**Available TypeGuards:**

- Output item guards: `is_message_item()`, `is_reasoning_item()`, `is_file_search_call()`, etc.
- Annotation guards: `is_file_citation()`, `is_url_citation()`, `is_file_path()`
- Content guards: `is_output_text()`, `is_output_refusal()`
- Event guards: `is_text_delta_event()`, `is_response_completed_event()`
- Helper functions: `get_tool_queries()`, `get_tool_results()`, `get_tool_content()`

See [ADR-010](docs/adr/CLAUDE-010-response-type-guards.md) for detailed design rationale and migration guide.

### Tool Call and Tool Call Result Classes

The system implements a two-tier architecture separating **Tool Definitions** (input configuration) from **Tool Call Results** (execution state and results). See [ADR-011](docs/adr/CLAUDE-011-tool-call-architecture.md) for comprehensive design details.

#### Tool Definition Classes (Input Configuration)

These classes specify what tools are available and how to configure them:

1. **FileSearchTool** - Vector store document search configuration
   - `type: "file_search"`
   - `vector_store_ids: list[str]`
   - `max_num_results: int | None`
   - `ranking_options: RankingOptions | None`

2. **WebSearchTool** - Web search configuration with location context
   - `type: "web_search_preview" | "web_search_preview_2025_03_11" | "web_search"`
   - `search_context_size: "low" | "medium" | "high" | None`
   - `user_location: UserLocation | None`

3. **FunctionTool** - Custom function execution configuration
   - `type: "function"`
   - `name: str`
   - `parameters: dict[str, object] | None`
   - `description: str | None`

4. **ComputerTool** - Computer interface automation configuration
   - `type: "computer_use_preview"`
   - `display_width: int`
   - `display_height: int`
   - `environment: "windows" | "mac" | "linux" | "ubuntu" | "browser"`

5. **ListDocumentsTool** - Advanced document listing configuration
   - `type: "list_documents"`
   - `vector_store_ids: list[str]`
   - `max_num_results: int | None`
   - `filters: dict[str, str | float | bool | int] | None`

6. **FileReaderTool** - Direct document reading configuration
   - `type: "file_reader"`

7. **PageReaderTool** - Page-specific document reading configuration
   - `type: "page_reader" | "page_reader_preview"`

#### Tool Call Result Classes (Execution State & Results)

These classes represent execution state and results after tools are invoked:

1. **ResponseFileSearchToolCall** - File search execution results
   - `type: "file_search_call"`
   - `id: str`
   - `status: "in_progress" | "searching" | "completed" | "incomplete" | "failed"`
   - `queries: list[str]`

2. **ResponseFunctionWebSearch** - Web search execution results
   - `type: "web_search_call"`
   - `id: str`
   - `status: "in_progress" | "searching" | "completed" | "failed"`
   - `queries: list[str]`

3. **ResponseFunctionToolCall** - Function call execution results
   - `type: "function_call"`
   - `id: str`
   - `call_id: str`
   - `name: str`
   - `arguments: str`
   - `status: "in_progress" | "completed" | "incomplete" | None`

4. **ResponseComputerToolCall** - Computer tool execution results
   - `type: "computer_call"`
   - `id: str`
   - `action: Action`
   - `call_id: str`
   - `status: "in_progress" | "completed" | "incomplete"`

5. **ResponseListDocumentsToolCall** - List documents execution results
   - `type: "list_documents_call"`
   - `id: str`
   - `queries: list[str]`
   - `count: int`
   - `status: "in_progress" | "searching" | "completed" | "incomplete"`

6. **ResponseFunctionFileReader** - File reader execution results (extends TraceableToolCall)
   - `type: "file_reader_call"`
   - `id: str`
   - `status: "in_progress" | "searching" | "completed" | "incomplete"`
   - `doc_ids: list[str]`
   - `query: str`
   - `progress: float | None` (inherited from TraceableToolCall)
   - `execution_trace: str | None` (inherited from TraceableToolCall)
   - Results are accessed through separate mechanisms

7. **ResponseFunctionPageReader** - Page reader execution results (extends TraceableToolCall)
   - `type: "page_reader_call"`
   - `id: str`
   - `status: "in_progress" | "searching" | "completed" | "incomplete"`
   - `document_id: str`
   - `start_page: int`
   - `end_page: int | None`
   - `progress: float | None` (inherited from TraceableToolCall)
   - `execution_trace: str | None` (inherited from TraceableToolCall)
   - Results are accessed through separate mechanisms

7. **ResponseCodeInterpreterToolCall** - Code execution results
   - `type: "code_interpreter_call"`
   - `id: str`
   - `code: str`
   - `results: list[Result]`
   - `status: "in_progress" | "interpreting" | "completed"`

#### Supporting Classes

- **TraceableToolCall** - Base class for progress tracking and execution logging
- **Chunk** - File search result data structure
- **AnnotationFileCitation** - File citation references
- **AnnotationURLCitation** - Web content citations
- **AnnotationFilePath** - File path references

#### Unified Type Aliases

```python
# Tool definitions union
Tool: TypeAlias = Annotated[
    FileSearchTool | FunctionTool | WebSearchTool | ComputerTool |
    ListDocumentsTool | FileReaderTool | PageReaderTool,
    PropertyInfo(discriminator="type"),
]

# Tool call results union
ResponseOutputItem: TypeAlias = Annotated[
    ResponseOutputMessage | ResponseFileSearchToolCall | ResponseFunctionToolCall |
    ResponseFunctionWebSearch | ResponseListDocumentsToolCall |
    ResponseFunctionFileReader | ResponseFunctionPageReader | ResponseComputerToolCall | ResponseReasoningItem,
    PropertyInfo(discriminator="type"),
]
```

### Advanced Type System Design

#### Using TYPE_CHECKING for Import Optimization

The `TYPE_CHECKING` constant prevents circular imports and reduces runtime overhead:

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # These imports are only for type checking, not runtime
    from forge_cli.response._types.response import Response
    from forge_cli.models.state import StreamState

class Processor:
    def process(self, response: "Response", state: "StreamState") -> None:
        # Forward references with quotes avoid runtime import
        pass
```

**Benefits:**

- Prevents circular import errors
- Reduces module loading time
- Keeps type information for static analysis

#### Using cast() Safely

While we prefer TypeGuards, `cast()` has legitimate uses when you have verified the type through other means:

```python
from typing import cast, Dict, Any
from pydantic import BaseModel

# GOOD: Cast after validation
def parse_config(data: Dict[str, Any]) -> AppConfig:
    # Pydantic validates the data
    validated = AppConfig.model_validate(data)
    # Cast is safe here because model_validate ensures correct type
    return cast(AppConfig, validated)

# GOOD: Cast with runtime check
def get_tool_name(item: Any) -> str:
    if not isinstance(item, dict) or "name" not in item:
        raise ValueError("Invalid tool item")
    # We've verified the structure, cast is acceptable
    return cast(str, item["name"])

# BAD: Blind cast without verification
def unsafe_cast(item: Any) -> FileSearchCall:
    return cast(FileSearchCall, item)  # DANGER: No verification!
```

#### Protocol Classes for Duck Typing

Use Protocol classes to define interfaces without inheritance:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Searchable(Protocol):
    """Any object that can be searched."""
    queries: list[str]
    max_results: int
    
    def search(self) -> list[dict]: ...

# Works with any class that matches the protocol
def process_search(searchable: Searchable) -> None:
    results = searchable.search()
    print(f"Found {len(results)} results for {searchable.queries}")

# Runtime checking
if isinstance(obj, Searchable):
    process_search(obj)
```

#### Generic Types for Reusable Components

Create flexible, type-safe components with generics:

```python
from typing import Generic, TypeVar, Optional

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Registry(Generic[K, V]):
    """Type-safe registry pattern."""
    def __init__(self) -> None:
        self._items: dict[K, V] = {}
    
    def register(self, key: K, value: V) -> None:
        self._items[key] = value
    
    def get(self, key: K) -> Optional[V]:
        return self._items.get(key)

# Usage with full type safety
processor_registry: Registry[str, BaseProcessor] = Registry()
processor_registry.register("file_search", FileSearchProcessor())
```

#### Literal Types for Exhaustive Matching

Use Literal types for exhaustive pattern matching:

```python
from typing import Literal, Union, assert_never

ToolType = Literal["file_search", "web_search", "code_analyzer"]

def get_tool_icon(tool_type: ToolType) -> str:
    if tool_type == "file_search":
        return "📁"
    elif tool_type == "web_search":
        return "🌐"
    elif tool_type == "code_analyzer":
        return "🔍"
    else:
        # Type checker ensures all cases are handled
        assert_never(tool_type)
```

#### Type Aliases for Complex Types

Simplify complex type annotations with aliases:

```python
from typing import TypeAlias, Union, Dict, List

# Define complex types once
CitationMap: TypeAlias = Dict[str, List[Annotation]]
ToolResult: TypeAlias = Union[FileSearchResult, WebSearchResult, CodeAnalysisResult]
EventHandler: TypeAlias = Callable[[str, Dict[str, Any]], Awaitable[None]]

# Use simple aliases throughout code
class CitationProcessor:
    def __init__(self) -> None:
        self.citations: CitationMap = {}
    
    def process_result(self, result: ToolResult) -> None:
        # Clean, readable type annotations
        pass
```

#### Overloading for Better Type Inference

Use `@overload` to provide precise type information for different call patterns:

```python
from typing import overload, Union, Literal

@overload
def get_config(key: Literal["model"]) -> str: ...

@overload
def get_config(key: Literal["temperature"]) -> float: ...

@overload
def get_config(key: Literal["tools"]) -> list[str]: ...

@overload
def get_config(key: str) -> Any: ...

def get_config(key: str) -> Any:
    """Get configuration value with correct type."""
    config = load_config()
    return config.get(key)

# Type checker knows the return type
model: str = get_config("model")  # ✓ Correct
temp: float = get_config("temperature")  # ✓ Correct
```

#### NewType for Domain Modeling

Create distinct types for domain concepts:

```python
from typing import NewType

# Create distinct types for IDs
FileId = NewType("FileId", str)
UserId = NewType("UserId", str)
VectorStoreId = NewType("VectorStoreId", str)

def process_file(file_id: FileId, user_id: UserId) -> None:
    # Type system prevents mixing up IDs
    pass

# Must explicitly create the new type
file_id = FileId("file_123")
user_id = UserId("user_456")

# This would be a type error:
# process_file(user_id, file_id)  # ✗ Wrong order!
```

#### Type Narrowing Best Practices

Combine multiple techniques for robust type narrowing:

```python
from typing import Union, Optional

def process_item(item: Union[Dict[str, Any], BaseModel, None]) -> str:
    # Guard against None
    if item is None:
        return "No item"
    
    # Narrow to BaseModel
    if isinstance(item, BaseModel):
        # Type checker knows item is BaseModel
        return item.model_dump_json()
    
    # Must be Dict[str, Any] now
    if "type" in item and item["type"] == "file_search":
        # Use TypeGuard for further narrowing
        if is_file_search_call(item):
            return f"File search: {item.queries}"
    
    return str(item)
```

#### Const and Final for Immutability

Use `Final` and `Literal` for constants:

```python
from typing import Final, Literal

# Runtime constant
MAX_RETRIES: Final[int] = 3
API_VERSION: Final[Literal["v1"]] = "v1"

class APIClient:
    # Class-level constant
    BASE_URL: Final[str] = "https://api.example.com"
    
    def __init__(self) -> None:
        # Instance constant (can't be reassigned)
        self.session_id: Final[str] = generate_session_id()
```

These advanced typing techniques work together to create a robust, maintainable type system that catches errors at development time while providing excellent IDE support and documentation.

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
    config = AppConfig(**user_data)
except ValidationError:
    config = AppConfig()  # Silent fallback masks the real issue

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
config = AppConfig(**user_data)  # Will raise ValidationError if invalid

# GOOD: Explicit error handling with user feedback
try:
    file_info = FileInfo(**file_data)
except ValidationError as e:
    raise ValueError(f"Invalid file data: {e}") from e
```

Fast failure reveals problems early in development and prevents silent corruption of program state. Use Pydantic's validation to catch issues immediately rather than masking them with defensive code.

## Import Conventions

**IMPORTANT: Follow these import patterns based on directory level and API design:**

### Response Types and Type Guards

Always import response types from the centralized location:

```python
# Response types
from forge_cli.response._types.response import ResponseFileSearchToolCall, ResponseOutputMessage
from forge_cli.response._types.annotations import AnnotationFileCitation

# Type guards for safe type narrowing
from forge_cli.response.type_guards.output_items import is_file_search_call
from forge_cli.response.type_guards.annotations import is_file_citation
```

### Top-Level Directory (`src/forge_cli/`)

Files at the top level use **absolute imports**:

```python
# In src/forge_cli/main.py
from forge_cli.sdk import astream_response, async_get_vectorstore
from forge_cli.config import AppConfig
from forge_cli.display.base import BaseDisplay
from forge_cli.display.rich_display import RichDisplay
from forge_cli.stream.handler import StreamHandler
from forge_cli.processors.registry import initialize_default_registry
```

### Subdirectories (`models/`, `response/`, `display/`, `sdk/`, etc.)

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
from forge_cli.config import AppConfig
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

Required environment variables:

```bash
# Knowledge Forge API server (required)
export KNOWLEDGE_FORGE_URL=http://localhost:9999

# OpenAI API key (optional, for certain features)
export OPENAI_API_KEY=your-api-key

# Optional: Custom configuration
export FORGE_CLI_CONFIG_FILE=/path/to/config.json
```

### Configuration File

Create a configuration file for persistent settings:

```json
{
  "default_model": "qwen-max-latest",
  "default_effort": "medium",
  "default_tools": ["file_search"],
  "default_vector_store_ids": ["vs_123"],
  "chat_settings": {
    "auto_save": true,
    "save_directory": "./chat_sessions"
  }
}
```

## Usage

### Quick Start

```bash
# Basic usage
forge-cli -q "Your question here"

# With file search
forge-cli -q "What's in these docs?" --vec-id vs_123

# With web search
forge-cli -t web-search -q "Latest AI news"

# Interactive chat
forge-cli --chat

# Multiple tools
forge-cli -t file-search -t web-search --vec-id vs_123 -q "Compare docs with web"
```

### SDK API

```python
from forge_cli.sdk import async_create_response, astream_response

# Stream response
async for event_type, event_data in astream_response(
    input_messages="Your query",
    model="qwen-max-latest"
):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="")
    elif event_type == "done":
        break

# File operations
from forge_cli.sdk import async_upload_file, async_create_vectorstore

file_result = await async_upload_file("/path/to/file.pdf")
vs_result = await async_create_vectorstore("My KB", file_ids=[file_result["id"]])
```

### Common Options

```bash
--debug, -d          # Show detailed information
--chat, -i           # Interactive mode
--render FORMAT      # Output format: json/rich/plaintext (default: rich)
--effort LEVEL       # low/medium/high
--model MODEL        # AI model to use
```

## Architecture

### Modular Design Philosophy

The project follows modern software engineering principles:

1. **Single Responsibility**: Each module has one clear purpose
2. **Type Safety First**: Comprehensive type annotations and TypeGuards throughout
3. **Layered Architecture**: Clear separation between SDK, response handling, and display
4. **Pluggable Components**: Swappable renderers and configurable displays
5. **Response-Centric Design**: Architecture mirrors the API's response structure

### Key Components

#### Response Processing

Responses from the Knowledge Forge API are processed through a typed pipeline:

```
API Response Stream → TypedStreamHandler → Response Snapshots → Renderer Selection → Display Output
```

#### Processor System

Each output type has a dedicated processor:

- `ReasoningProcessor`: Handles thinking/analysis blocks
- `FileSearchProcessor`: Processes file search tool calls
- `WebSearchProcessor`: Handles web search operations
- `CodeAnalyzerProcessor`: Handles code analysis tool calls
- `MessageProcessor`: Manages final responses with citations

#### Display Strategies (V3 Architecture)

The V3 display system uses snapshot-based rendering with pluggable renderers:

- `RichRenderer`: Rich terminal UI with live updates and beautiful formatting
- `PlainRenderer`: Simple text output for basic terminals
- `JsonRenderer`: Machine-readable JSON format for automation
- `Display`: Coordinator that manages renderer lifecycle and response routing

## Example Scripts

```bash
# Basic examples
python -m forge_cli.scripts.hello-async
python -m forge_cli.scripts.hello-file-search -q "What's in these docs?"
python -m forge_cli.scripts.simple-flow -f document.pdf -q "Summarize this"
```

### Interactive Chat Mode

The CLI supports a comprehensive chat mode with persistent conversations:

```bash
# Start interactive chat
forge-cli --chat

# Chat with initial configuration
forge-cli --chat -t file-search --vec-id vs_123 -q "Hello"

# Available chat commands:
# /help, /save, /load, /tools, /model, /clear, /info, /config
# /enable-web-search, /disable-web-search, /enable-file-search, /disable-file-search
# /enable-page-reader, /disable-page-reader
```

#### Chat Features

- **Persistent Conversations**: Save/load chat sessions to JSON files
- **Command System**: 13+ built-in commands with auto-completion
- **Dynamic Tool Management**: Enable/disable tools during conversation
- **Model Switching**: Change AI models mid-conversation
- **Session Management**: Clear history, view statistics, export conversations
- **Error Recovery**: Graceful handling of API errors and reconnection

#### Chat Commands

| Command | Description | Example |
|---------|-------------|--------|
| `/help` | Show available commands | `/help` |
| `/save` | Save conversation | `/save my-session.json` |
| `/load` | Load conversation | `/load my-session.json` |
| `/tools` | Show active tools | `/tools` |
| `/model` | Change AI model | `/model gpt-4` |
| `/clear` | Clear conversation | `/clear` |
| `/info` | Show session info | `/info` |
| `/config` | Show configuration | `/config` |
| `/enable-web-search` | Enable web search | `/enable-web-search` |
| `/disable-web-search` | Disable web search | `/disable-web-search` |
| `/enable-file-search` | Enable file search | `/enable-file-search` |
| `/disable-file-search` | Disable file search | `/disable-file-search` |
| `/enable-page-reader` | Enable page reader | `/enable-page-reader` |
| `/disable-page-reader` | Disable page reader | `/disable-page-reader` |

## Development

### Quick Testing

```bash
# Test basic functionality
forge-cli --debug -q "test query"

# Test scripts
python scripts/debug.py --test-api
python scripts/create-vectorstore.py
```

### Extending

1. Add processors in `processors/` (relative imports)
2. Register in `processors/registry.py`
3. Update `config.py` for new options
4. Follow `async_<action>_<resource>` pattern for SDK functions

## Dependencies

### Core Dependencies

Automatically managed by `uv` or `pip`:

- **aiohttp>=3.8.0** - Async HTTP client for API communication
- **rich>=12.0.0** - Rich terminal UI components with live updates
- **pydantic>=2.0.0** - Data validation and serialization
- **loguru>=0.6.0** - Advanced logging with structured output

### Optional Dependencies

For enhanced functionality:

- **prompt-toolkit>=3.0.0** - Interactive command line with auto-completion
- **requests>=2.25.0** - Fallback HTTP client for compatibility
- **pytest, black, flake8, mypy** - Development and testing tools

### Installation Notes

- **Python 3.10+** required for TypeGuard support and modern typing features
- **uv** package manager recommended for faster dependency resolution
- All dependencies include proper type stubs for IDE support

## Streaming Events

Key event types: `response.output_text.delta`, `response.completed`, `response.file_search_call.completed`, `done`

```python
# Stream processing
async for event_type, event_data in astream_response(input_messages="query"):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="")
    elif event_type == "done":
        break
```

## Troubleshooting

```bash
# Debug mode
forge-cli --debug -q "test query"

# Check installation
forge-cli --version

# Verify SDK
python -c "from forge_cli.sdk.typed_api import create_typed_request; print('OK')"
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Import errors | Run `uv sync` to install dependencies |
| Connection refused | Check `KNOWLEDGE_FORGE_URL` environment variable |
| Missing API key | Set `OPENAI_API_KEY` environment variable |
| Type errors in IDE | Ensure Python 3.10+ and proper type stub installation |
| Chat mode not working | Install `prompt-toolkit` for enhanced features |
| Display issues | Try `--render plaintext` or `--render json` |
| Performance issues | Use `--debug` to identify bottlenecks |

## Architecture Decision Records

The project includes comprehensive ADRs documenting design decisions:

- **[ADR-001](docs/adr/ADR-001-commandline-design.md)**: Command-line interface design principles
- **[ADR-002](docs/adr/ADR-002-reasoning-event-handling.md)**: Reasoning event handling in streaming
- **[ADR-003](docs/adr/ADR-003-file-search-annotation-display.md)**: File search citation display architecture
- **[ADR-004](docs/adr/ADR-004-snapshot-based-streaming-design.md)**: Snapshot-based streaming approach
- **[ADR-005](docs/adr/ADR-005-interactive-chat-mode.md)**: Interactive chat mode implementation
- **[ADR-006](docs/adr/ADR-006-v2-event-based-display-architecture.md)**: V2 event-based display architecture (legacy)
- **[ADR-007](docs/adr/ADR-007-typed-only-architecture-migration.md)**: Migration to typed-only architecture
- **[ADR-008](docs/adr/ADR-008-v3-response-snapshot-display-architecture.md)**: V3 response-snapshot display architecture (current)
- **[ADR-009](docs/adr/ADR-009-code-analyzer-tool.md)**: Code Analyzer tool design and integration
- **[ADR-010](docs/adr/ADR-010-response-type-guards.md)**: TypeGuard functions for Response types
- **[ADR-011](docs/adr/ADR-011-tool-call-architecture.md)**: Tool call architecture design

## Contributing

This project serves as both a practical tool and reference implementation for the Knowledge Forge API. When contributing:

1. Follow the established modular architecture
2. Maintain comprehensive type annotations
3. Add tests for new functionality
4. Update documentation and ADRs as needed
5. Use the SDK for all API interactions

The codebase demonstrates modern Python practices and can serve as a template for building applications with the Knowledge Forge API.
