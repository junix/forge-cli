# Hello File Search Refactored - Design and Implementation Guide

## Overview

This module is a complete refactoring of the monolithic `hello-file-search.py` script into a modular, maintainable architecture. It demonstrates best practices in Python software design while maintaining 100% backward compatibility with the original script.

## Architecture Philosophy

### Design Principles

1. **Single Responsibility Principle**: Each module has one clear purpose
2. **Open/Closed Principle**: Open for extension, closed for modification
3. **Dependency Inversion**: Depend on abstractions, not concretions
4. **Interface Segregation**: Small, focused interfaces
5. **Don't Repeat Yourself**: Shared logic is extracted and reused

### Key Architectural Decisions

#### 1. **Output-Centric Design**
The API returns responses with an `output` array containing different item types. Our architecture mirrors this structure:

```python
# Each output item type has a dedicated processor
OutputItem = Union[
    ReasoningItem,      # Thinking/analysis
    FileSearchCall,     # File search tool
    ListDocumentsCall, # List documents tool
    MessageItem,        # Final response with citations
]
```

#### 2. **Registry Pattern for Processors**
Instead of giant if/elif chains, we use a registry:

```python
# Registration
registry.register("reasoning", ReasoningProcessor())
registry.register("file_search_call", FileSearchProcessor())

# Usage
processor = registry.get_processor(item["type"])
if processor:
    result = processor.process(item)
```

#### 3. **Strategy Pattern for Display**
Different output formats are handled by swappable display strategies:

```python
# Interface
class BaseDisplay(ABC):
    async def update_content(self, content: str, metadata: Dict) -> None: ...

# Implementations
display = RichDisplay()    # Rich terminal UI
display = PlainDisplay()   # Plain text
display = JsonDisplay()    # JSON output
```

## Module Structure

### Core Modules

#### `models/` - Data Types and State
- **response/_types/**: Comprehensive OpenAPI-generated type definitions
- **events.py**: Event type enumeration and helpers
- **state.py**: Centralized state management during streaming

#### `processors/` - Output Processing
- **base.py**: Abstract base class defining the processor interface
- **registry.py**: Central registry for all processors
- **reasoning.py**: Handles reasoning/thinking blocks
- **message.py**: Processes final messages with citations
- **tool_calls/**: Specialized processors for each tool type

#### `display/` - Presentation Layer
- **base.py**: Abstract display interface
- **rich_display.py**: Rich library implementation with live updates
- **plain_display.py**: Fallback plain text output
- **json_display.py**: Machine-readable JSON output

#### `stream/` - Event Stream Handling
- **handler.py**: Main stream processor that orchestrates everything

## Implementation Details

### Stream Processing Flow

```
API Event Stream
    ↓
StreamHandler
    ↓
Event Router (checks event type)
    ↓
Processor Registry (finds appropriate processor)
    ↓
Output Processor (processes the item)
    ↓
Display Strategy (renders to user)
```

### State Management

The `StreamState` class maintains all necessary state during streaming:

```python
@dataclass
class StreamState:
    output_items: List[Dict[str, Any]]      # Current snapshot
    tool_states: Dict[str, ToolState]       # Tool execution states
    file_id_to_name: Dict[str, str]         # File mappings
    citations: List[Dict[str, Any]]         # Extracted citations
    usage: Dict[str, int]                   # Token usage
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

### Adding a New Tool Type

1. Create a processor in `processors/tool_calls/`:
```python
# processors/tool_calls/new_tool.py
class NewToolProcessor(BaseToolCallProcessor):
    TOOL_TYPE = "new_tool"
    TOOL_CONFIG = {...}
```

2. Register it in `processors/registry.py`:
```python
registry.register("new_tool_call", NewToolProcessor())
```

### Adding a New Display Format

1. Create a display class implementing `BaseDisplay`:
```python
# display/html_display.py
class HtmlDisplay(BaseDisplay):
    async def update_content(self, content: str, metadata: Dict) -> None:
        # Generate HTML output
```

2. Add it to the display factory in `main.py`

### Adding a New Output Item Type

1. Define the type in `response/_types/` (for API types) or `models/` (for internal types)
2. Create a processor in `processors/`
3. Register the processor
4. The stream handler will automatically use it

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

### Unit Tests
Each component can be tested in isolation:
```python
def test_reasoning_processor():
    processor = ReasoningProcessor()
    item = {"type": "reasoning", "summary": [...]}
    result = processor.process(item)
    assert result["content"] == expected_text
```

### Integration Tests
Test the full pipeline with mock streams:
```python
async def test_stream_handling():
    display = MockDisplay()
    handler = StreamHandler(display)
    await handler.handle_stream(mock_events, "test query")
    assert display.final_content == expected
```

## Debugging

Enable debug mode to see detailed event information:
```bash
uv run -m hello_file_search_refactored --debug -q "query"
```

Debug output includes:
- All event types and data
- State transitions
- Processor selection
- Timing information

## Chat Mode Implementation

### Overview
The module now supports interactive multi-turn chat mode, enabling continuous conversations with context preservation.

### Architecture
Chat functionality is cleanly separated into:

1. **models/conversation.py**: Message and conversation state management
2. **chat/controller.py**: Main chat loop and message handling  
3. **chat/commands.py**: Command system with 13 built-in commands
4. **display enhancements**: Chat-specific methods added to displays

### Key Features
- Full conversation history maintained across turns
- Command system with aliases (/help, /save, /load, etc.)
- Auto-completion support for commands when prompt_toolkit is available
- Session persistence to JSON files
- Dynamic tool and model management
- Graceful error recovery
- Proper content preservation after streaming completes
- Quick enable/disable commands for web search and file search tools

### Display Handling
The Rich display implementation has special handling for chat mode to ensure assistant responses remain visible after streaming:
- During streaming, content is shown in a Live panel
- When streaming completes, the `finalize` method preserves the content by re-displaying it as static markdown
- This prevents the common issue where responses disappear when the Live display stops

### Recent Fixes
1. **Reasoning Processor**: Updated to handle both "summary_text" and "text" types in the API response
2. **Chat Mode Display**: Fixed issue where assistant responses weren't visible after streaming completed
3. **Event Handling**: Added support for "final_response" event type for better response capture
4. **Debug Logging**: Enhanced debug output to show content formatting details

### Usage
```bash
# Start chat mode
uv run -m hello_file_search_refactored --chat

# Chat with initial question
uv run -m hello_file_search_refactored --chat -q "Hello" -t web-search
```

## Future Enhancements

### Planned Features
1. **Plugin System**: Dynamic loading of custom processors
2. **Caching Layer**: Cache responses for repeated queries
3. **Metrics Collection**: Performance and usage analytics
4. **Configuration Files**: YAML/JSON config support
5. **Internationalization**: Multi-language support beyond Chinese
6. **Advanced Chat Features**: Conversation branching, undo/redo

### Architecture Readiness
The modular design makes these enhancements straightforward:
- Plugins: Add a dynamic loader to the registry
- Caching: Wrap the stream handler
- Metrics: Add observers to key points
- Config: Extend the `AppConfig` class
- i18n: Add translation layer to processors

## Best Practices

### When Modifying This Code

1. **Maintain Type Safety**: Always use type hints
2. **Follow the Patterns**: Use existing patterns for consistency
3. **Test in Isolation**: Write unit tests for new components
4. **Document Changes**: Update this file with significant changes
5. **Preserve Compatibility**: Don't break existing CLI arguments

### Code Style

- Use descriptive names over comments
- Keep functions small and focused
- Prefer composition over inheritance
- Handle edge cases explicitly
- Use async/await consistently

## Conclusion

This refactoring demonstrates how to transform legacy code into a modern, maintainable architecture while preserving functionality. The modular design enables easy extension and modification while maintaining code quality and readability.