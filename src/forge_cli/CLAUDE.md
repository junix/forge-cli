# Forge CLI - Modern Command Line Tools for Knowledge Forge API

## Overview

The Forge CLI is a modern, modular command-line tool and SDK for interacting with the Knowledge Forge API. Built with Python 3.8+ and structured as a proper Python package, it provides comprehensive functionality for file uploads, vector store management, AI-powered question answering, and streaming responses with a type-safe architecture.

## Architecture Philosophy

### Design Principles

1. **Type Safety First**: Comprehensive type annotations and Pydantic models throughout
2. **Snapshot-Based Streaming**: V3 display architecture using response snapshots
3. **Modular Design**: Clear separation of concerns with pluggable components
4. **SDK-First Approach**: All API interactions use the typed SDK
5. **Fail-Fast Validation**: Pydantic models ensure data integrity

### Key Architectural Decisions

#### 1. **V3 Snapshot-Based Display Architecture**
The current display system uses response snapshots rather than event streaming:

```python
# V3 - Simple response rendering
def render_response(self, response: Response):
    # Everything is in the response object!
    # No state tracking, no event synchronization
    # Resilient to missed events (snapshot-based)
```

#### 2. **Typed API with TypeGuards**
Type-safe access to API responses using TypeGuard functions:

```python
from forge_cli.response.type_guards.output_items import is_file_search_call

if is_file_search_call(item):
    # Type checker knows item is ResponseFileSearchToolCall
    for query in item.queries:  # Full autocomplete!
        process_query(query)
```

#### 3. **Pydantic Models Throughout**
All data structures use Pydantic models for validation and type safety:

```python
class AppConfig(BaseModel):
    model: str = "qwen-max-latest"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    tools: set[str] = Field(default_factory=set)

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
```

## Module Structure

### Core Modules

#### `models/` - Data Types and State

- **conversation.py**: Chat conversation management with Pydantic models
- **state.py**: Stream state management with type safety

#### `response/` - Response Handling and Type Definitions

- **_types/**: OpenAPI-generated types (do not edit manually)
- **type_guards/**: TypeGuard functions for safe type narrowing
- **utils.py**: Response utility functions
- **processor.py**: Response processing logic

#### `processors/` - Output Processing (Legacy)

- **base.py**: Abstract base class defining the processor interface
- **registry.py**: Central registry for all processors
- **reasoning.py**: Handles reasoning/thinking blocks
- **message.py**: Processes final messages with citations
- **tool_calls/**: Specialized processors for each tool type

#### `display/` - Presentation Layer

- **v3/**: Current snapshot-based display architecture
  - **base.py**: Display coordinator and renderer protocol
  - **renderers/**: Pluggable renderers (Rich, Plain, JSON)
- **v2/**: Legacy event-based display (deprecated)

#### `stream/` - Event Stream Handling

- **handler.py**: Main stream processor that orchestrates everything

#### `chat/` - Interactive Chat Mode

- **controller.py**: Chat session controller with conversation management
- **commands.py**: Chat command system with 13+ built-in commands

#### `sdk/` - Python SDK for Knowledge Forge API

- **typed_api.py**: Modern typed response API (recommended)
- **files.py**: File upload, management, and task operations
- **config.py**: Configuration and base URL settings

## Data Modeling Philosophy

### Type Safety with Pydantic Models

**IMPORTANT**: This project uses **Pydantic v2 models** throughout for comprehensive type safety and validation. This is a core architectural decision that provides significant benefits:

#### Why Pydantic Models Are Essential

1. **Comprehensive Validation**: Automatic input validation with clear, user-friendly error messages
2. **Type Safety**: Runtime type checking and conversion with proper error handling
3. **Field Configuration**: Advanced field options like aliases, constraints, and custom validators
4. **Environment Integration**: Seamless loading from environment variables and configuration files
5. **Serialization**: Built-in JSON serialization/deserialization with proper type handling
6. **Developer Experience**: Better IDE support, autocomplete, and documentation generation
7. **TypeGuard Integration**: Works seamlessly with TypeGuard functions for type narrowing

#### Current Implementation Examples

```python
# ✅ CURRENT: Pydantic v2 models with comprehensive validation
class AppConfig(BaseModel):
    model: str = "qwen-max-latest"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    tools: set[str] = Field(default_factory=set)
    vector_store_ids: list[str] = Field(default_factory=list)

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

# ✅ CURRENT: Response types with TypeGuards
from forge_cli.response.type_guards.output_items import is_file_search_call

def process_output_item(item: ResponseOutputItem) -> None:
    if is_file_search_call(item):
        # Type checker knows item is ResponseFileSearchToolCall
        print(f"File search queries: {item.queries}")
        print(f"Status: {item.status}")
```

#### Use Validators Extensively

Always prefer Pydantic validators over manual validation:

```python
# ✅ PREFERRED: Pydantic validators
class ServerConfig(BaseModel):
    url: str
    timeout: int = Field(default=30, gt=0)
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip('/')
    
    @model_validator(mode='after')
    def validate_consistency(self) -> 'ServerConfig':
        # Cross-field validation
        if self.timeout > 300 and 'localhost' not in self.url:
            raise ValueError("Long timeouts should only be used with localhost")
        return self

# ❌ AVOID: Manual validation
class ManualConfig:
    def __init__(self, url: str, timeout: int = 30):
        # Manual validation scattered throughout code
        if not url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL")
        self.url = url.rstrip('/')
        if timeout <= 0:
            raise ValueError("Invalid timeout")
        self.timeout = timeout
```

#### Migration Guidelines

When encountering dataclasses in the codebase:

1. **Convert to Pydantic models** following the patterns above
2. **Add appropriate validators** for data integrity
3. **Use Field() for advanced options** like aliases and constraints
4. **Update imports** from `dataclasses` to `pydantic`
5. **Update documentation** and examples to reflect the change

This architectural choice ensures data integrity, improves developer experience, and provides a foundation for robust, maintainable code throughout the system.

## Implementation Details

### V3 Display Architecture Flow

```text
API Response Stream → StreamHandler → Response Snapshots → Display Coordinator → Renderer → Output
```

The V3 architecture simplifies the flow by using response snapshots instead of complex event handling.

### Current State Management

The `StreamState` class maintains all necessary state during streaming:

```python
class StreamState(BaseModel):
    response_id: str | None = None
    turn: int = 0
    usage: dict[str, int] = Field(default_factory=dict)
    vector_store_ids: list[str] = Field(default_factory=list)

    def update_from_response(self, response: Response) -> "StreamState":
        """Update state from a response snapshot."""
        return self.model_copy(update={
            "response_id": response.id,
            "usage": response.usage.model_dump() if response.usage else {},
        })
```

### Response Processing with TypeGuards

```python
from forge_cli.response.type_guards.output_items import (
    is_file_search_call, is_message_item, is_reasoning_item
)

def process_response(response: Response) -> None:
    for item in response.output:
        if is_file_search_call(item):
            print(f"File search: {item.queries}")
        elif is_message_item(item):
            print(f"Message: {item.content}")
        elif is_reasoning_item(item):
            print(f"Reasoning: {item.content}")
```

### Citation Processing

Citations are extracted from message annotations and formatted as markdown tables:

```python
# Unicode citation markers in text: ⟦⟦1⟧⟧
# Converted to markdown table:
| Citation | Document | Page | File ID |
|----------|----------|------|---------|
| [1]      | doc.pdf  | 5    | file_123 |
```

### Tool Call Processing

Each tool type has its own processor with Chinese localization:

```python
class FileSearchProcessor(BaseToolCallProcessor):
    TOOL_CONFIG = {
        "emoji": "📄",
        "action": "搜索文档",
        "status_searching": "正在搜索文档...",
        "status_completed": "搜索已完成",
    }
```

## Extension Points

### Adding a New Renderer (V3 Architecture)

1. Create a renderer implementing the `Renderer` protocol:

```python
# display/v3/renderers/html.py
from forge_cli.display.v3.base import BaseRenderer
from forge_cli.response._types.response import Response

class HtmlRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Extract content from response
        text = response.output_text
        citations = self._extract_citations(response)

        # Generate HTML output
        html = self._generate_html(text, citations)
        print(html)

    def finalize(self) -> None:
        print("</body></html>")
```

2. Register it in the display registry:

```python
from forge_cli.display.registry import DisplayRegistry

registry = DisplayRegistry()
registry.register("html", lambda: Display(HtmlRenderer()))
```

### Adding TypeGuard Functions

1. Create TypeGuard functions for new response types:

```python
# response/type_guards/output_items.py
from typing import TypeGuard
from forge_cli.response._types.response import ResponseOutputItem

def is_new_tool_call(item: ResponseOutputItem) -> TypeGuard[ResponseNewToolCall]:
    """Check if item is a new tool call."""
    return hasattr(item, 'type') and item.type == "new_tool_call"
```

2. Use TypeGuards for type-safe processing:

```python
if is_new_tool_call(item):
    # Type checker knows item is ResponseNewToolCall
    process_new_tool(item)
```

## Error Handling

- **Graceful Degradation**: Missing processors don't crash the app
- **Type Safety**: Invalid data structures are handled safely
- **User Feedback**: Errors are displayed appropriately per display mode

## Performance Considerations

1. **Streaming**: Events are processed as they arrive, not buffered
2. **Lazy Processing**: Only active output items are processed
3. **Efficient State Updates**: Minimal copying of data structures
4. **Display Throttling**: Updates are batched for performance

## Testing Strategy

### Unit Tests with Pydantic Models

Test components using Pydantic model validation:

```python
def test_app_config_validation():
    # Valid config
    config = AppConfig(model="gpt-4", temperature=0.5)
    assert config.temperature == 0.5

    # Invalid config should raise ValidationError
    with pytest.raises(ValidationError):
        AppConfig(temperature=3.0)  # Out of range

def test_type_guards():
    from forge_cli.response.type_guards.output_items import is_file_search_call

    # Mock response item
    item = ResponseFileSearchToolCall(
        type="file_search_call",
        id="search_123",
        queries=["test query"],
        status="completed"
    )

    assert is_file_search_call(item)
```

### Integration Tests with V3 Display

Test the V3 display architecture:

```python
async def test_v3_display():
    from forge_cli.display.v3.base import Display
    from forge_cli.display.v3.renderers.plain import PlainRenderer

    renderer = PlainRenderer()
    display = Display(renderer)

    # Mock response
    response = Response(id="resp_123", output=[...])
    display.handle_response(response)
    display.complete()
```

## Usage Examples

### Basic CLI Usage

```bash
# Interactive chat mode
python -m forge_cli --chat

# File search with vector store
python -m forge_cli -q "What's in these documents?" --vec-id vs_123

# Web search
python -m forge_cli -t web-search -q "Latest AI news"

# Debug mode
python -m forge_cli --debug -q "test query"
```

### SDK Usage

```python
from forge_cli.sdk.typed_api import astream_typed_response, create_typed_request

# Create typed request
request = create_typed_request(
    input_messages="Your query",
    tools=[{"type": "file_search", "vector_store_ids": ["vs_123"]}]
)

# Stream responses
async for event_type, response in astream_typed_response(request):
    if hasattr(response, 'output'):
        for item in response.output:
            if is_file_search_call(item):
                print(f"Searching: {item.queries}")
```

## Chat Mode Implementation

### Overview

The Forge CLI supports comprehensive interactive multi-turn chat mode with persistent conversations and advanced command system.

### Architecture

Chat functionality is implemented with:

1. **models/conversation.py**: Pydantic models for conversation state management
2. **chat/controller.py**: Main chat loop with conversation handling
3. **chat/commands.py**: Command system with 13+ built-in commands
4. **V3 display integration**: Seamless chat mode support in renderers

### Key Features

- **Persistent Conversations**: Save/load chat sessions to JSON files
- **Command System**: 13+ built-in commands with auto-completion
- **Dynamic Tool Management**: Enable/disable tools during conversation
- **Model Switching**: Change AI models mid-conversation
- **Session Management**: Clear history, view statistics, export conversations
- **Error Recovery**: Graceful handling of API errors and reconnection
- **Type-Safe State**: All conversation state uses Pydantic models

### V3 Display Integration

The V3 display architecture provides excellent chat mode support:

- **Snapshot-Based Rendering**: Each response is rendered as a complete snapshot
- **Consistent Display**: No issues with disappearing content after streaming
- **Rich Formatting**: Full markdown support with citations and tool results
- **Multiple Renderers**: Chat works with Rich, Plain, and JSON renderers

### Usage Examples

```bash
# Start interactive chat
python -m forge_cli --chat

# Chat with initial configuration
python -m forge_cli --chat -t file-search --vec-id vs_123

# Available commands: /help, /save, /load, /tools, /model, /clear, etc.
```

### Chat Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show available commands | `/help` |
| `/save` | Save conversation | `/save my-session.json` |
| `/load` | Load conversation | `/load my-session.json` |
| `/tools` | Show active tools | `/tools` |
| `/model` | Change AI model | `/model gpt-4` |
| `/clear` | Clear conversation | `/clear` |

## Future Enhancements

### Planned Features

1. **Enhanced TypeGuards**: More comprehensive type narrowing functions
2. **Plugin System**: Dynamic loading of custom renderers and processors
3. **Caching Layer**: Response caching for improved performance
4. **Configuration Files**: YAML/JSON config support with validation
5. **Advanced Chat Features**: Conversation branching, export formats
6. **Performance Monitoring**: Built-in metrics and profiling

### Architecture Readiness

The V3 architecture and type-safe design make enhancements straightforward:

- **New Renderers**: Implement the `Renderer` protocol
- **Enhanced TypeGuards**: Add functions to `response/type_guards/`
- **Caching**: Wrap the SDK functions with caching logic
- **Config**: Extend Pydantic models in `models/`
- **Monitoring**: Add observers to key components

## Best Practices

### Development Guidelines

1. **Type Safety First**: Use Pydantic models and TypeGuards throughout
2. **V3 Display**: Use snapshot-based rendering for new features
3. **SDK Usage**: Always use the typed SDK for API interactions
4. **Validation**: Let Pydantic handle data validation, don't use defensive programming
5. **Testing**: Write tests using Pydantic model validation

### Code Style

- Use comprehensive type annotations with Pydantic models
- Prefer TypeGuards over hasattr() checks
- Use the V3 display architecture for new renderers
- Follow the SDK-first approach for API interactions
- Implement proper error handling with clear error messages

## Conclusion

The Forge CLI demonstrates modern Python development practices with comprehensive type safety, modular architecture, and excellent developer experience. The V3 display architecture, Pydantic models, and TypeGuard functions provide a solid foundation for building robust, maintainable applications with the Knowledge Forge API.