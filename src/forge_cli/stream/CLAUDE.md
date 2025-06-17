# Stream Module - Event Stream Handling

## Overview

The stream module is the central nervous system of the Forge CLI, responsible for handling real-time event streams from the Knowledge Forge API. It orchestrates the flow of events from the API through processors to display strategies, maintaining state and ensuring smooth user experience during streaming operations. The module integrates seamlessly with the V3 snapshot-based display architecture.

## Directory Structure

```
stream/
├── __init__.py      # Module exports
└── handler.py       # Main stream processor and orchestrator
```

## Architecture & Design

### Core Responsibilities

1. **Event Stream Processing**: Handle Server-Sent Events (SSE) from the API
2. **Event Routing**: Direct events to appropriate processors
3. **State Management**: Maintain streaming session state
4. **Error Recovery**: Handle stream interruptions and errors gracefully
5. **Flow Control**: Manage backpressure and throttling

### Stream Processing Flow

```
API SSE Stream
    ↓
StreamHandler.handle_stream()
    ↓
Parse Event (type, data)
    ↓
Update StreamState
    ↓
Route to ProcessorRegistry
    ↓
Update Display Strategy
    ↓
Handle Completion/Error
```

## Component Details

### handler.py - Stream Handler

The `StreamHandler` class is the main orchestrator for event processing:

```python
class StreamHandler:
    """Handles streaming responses from the Knowledge Forge API."""

    def __init__(self,
                 display: BaseDisplay,
                 processor_registry: Optional[ProcessorRegistry] = None,
                 config: Optional[AppConfig] = None):
        self.display = display
        self.processor_registry = processor_registry or initialize_default_registry()
        self.config = config or AppConfig()
        self.state = StreamState()
```

### Key Methods

#### handle_stream()

Main entry point for processing an event stream:

```python
async def handle_stream(self, 
                       stream: AsyncIterator[Tuple[str, dict]], 
                       query: str) -> StreamState:
    """Process a complete event stream."""
    try:
        # Initialize
        self.display.handle_stream_start()
        
        # Process events
        async for event_type, event_data in stream:
            await self._process_event(event_type, event_data)
            
            # Apply throttling if configured
            if self.config.throttle_ms > 0:
                await asyncio.sleep(self.config.throttle_ms / 1000)
        
        # Finalize
        self.display.handle_stream_complete()
        return self.state
        
    except Exception as e:
        self.display.handle_error(str(e))
        raise
```

#### _process_event()

Routes individual events to appropriate handlers:

```python
async def _process_event(self, event_type: str, event_data: dict):
    """Process a single event based on its type."""
    
    # Update state timestamp
    self.state.last_event_time = time.time()
    
    # Handle based on event type
    if event_type == "response.output_item.added":
        await self._handle_output_item(event_data)
    
    elif event_type == "response.output_text.delta":
        await self._handle_text_delta(event_data)
    
    elif event_type.endswith(".searching"):
        await self._handle_tool_start(event_type, event_data)
    
    elif event_type.endswith(".completed"):
        await self._handle_tool_complete(event_type, event_data)
    
    elif event_type == "response.completed":
        await self._handle_response_complete(event_data)
    
    # Debug logging
    if self.config.debug:
        logger.debug(f"Event: {event_type}, Data: {event_data}")
```

### Event Type Handlers

#### Output Item Handler

Processes new output items (reasoning, messages, tool calls):

```python
async def _handle_output_item(self, event_data: dict):
    """Handle new output item events."""
    item = event_data.get("item", {})
    item_type = item.get("type")
    
    # Add to state
    self.state.add_output_item(item)
    
    # Route to processor
    processor = self.processor_registry.get_processor(item_type)
    if processor:
        processor.process(item, self.state, self.display)
    else:
        logger.warning(f"No processor for type: {item_type}")
```

#### Text Delta Handler

Handles streaming text updates:

```python
async def _handle_text_delta(self, event_data: dict):
    """Handle incremental text updates."""
    text = event_data.get("text", "")
    
    # Update state
    self.state.current_text += text
    
    # Update display
    self.display.handle_text_delta(text)
```

#### Tool Lifecycle Handlers

Manage tool execution states:

```python
async def _handle_tool_start(self, event_type: str, event_data: dict):
    """Handle tool start events."""
    # Extract tool info
    tool_type = self._extract_tool_type(event_type)
    tool_id = event_data.get("id")
    
    # Update state
    self.state.add_tool(tool_id, ToolState(
        tool_type=tool_type,
        status=ToolStatus.RUNNING,
        start_time=time.time()
    ))
    
    # Notify display
    self.display.handle_tool_start(
        tool_type=tool_type,
        tool_id=tool_id,
        **event_data
    )

async def _handle_tool_complete(self, event_type: str, event_data: dict):
    """Handle tool completion events."""
    tool_id = event_data.get("id")
    
    # Update state
    if tool_id in self.state.tools:
        tool_state = self.state.tools[tool_id]
        tool_state.status = ToolStatus.COMPLETED
        tool_state.end_time = time.time()
        tool_state.results = event_data.get("results", [])
    
    # Notify display
    results_count = len(event_data.get("results", []))
    self.display.handle_tool_complete(tool_id, results_count)
```

### State Management

The handler maintains comprehensive state throughout streaming:

```python
# State tracking includes:
- Current response ID
- Active output items
- Tool execution states  
- Citation registry
- File mappings
- Usage statistics
- Timing information
```

## Usage Guidelines

### For Language Models

When working with the stream handler:

1. **Basic usage**:

```python
from forge_cli.stream.handler import StreamHandler
from forge_cli.display.rich_display import RichDisplay
from forge_cli.sdk import astream_response

# Create handler
display = RichDisplay(config)
handler = StreamHandler(display)

# Process stream
stream = astream_response(query="Your question")
final_state = await handler.handle_stream(stream, query)
```

2. **Custom processor registry**:

```python
from forge_cli.processors.registry import ProcessorRegistry

# Create custom registry
registry = ProcessorRegistry()
registry.register("custom_type", CustomProcessor())

# Use with handler
handler = StreamHandler(display, processor_registry=registry)
```

3. **Error handling**:

```python
try:
    state = await handler.handle_stream(stream, query)
except StreamInterruptedError:
    # Handle interrupted stream
    pass
except Exception as e:
    # Handle other errors
    logger.error(f"Stream error: {e}")
```

## Event Processing Patterns

### Event Type Categories

1. **Lifecycle Events**:
   - `response.created` - Response initialized
   - `response.in_progress` - Processing started
   - `response.completed` - Response finished
   - `done` - Stream closed

2. **Content Events**:
   - `response.output_item.added` - New output item
   - `response.output_text.delta` - Text chunk
   - `response.output_text.done` - Text complete

3. **Tool Events**:
   - `response.<tool>_call.searching` - Tool started
   - `response.<tool>_call.completed` - Tool finished
   - `response.<tool>_call.failed` - Tool error

### Event Data Structures

Common event data patterns:

```python
# Output item event
{
    "item": {
        "type": "reasoning",
        "id": "item_123",
        "content": "..."
    }
}

# Text delta event
{
    "text": "chunk of text",
    "index": 0
}

# Tool completion event
{
    "id": "tool_123",
    "results": [...],
    "usage": {...}
}
```

## Development Guidelines

### Extending the Handler

1. **Adding new event types**:

```python
# In _process_event method
elif event_type == "response.new_feature":
    await self._handle_new_feature(event_data)

# Add handler method
async def _handle_new_feature(self, event_data: dict):
    # Process the new feature
    feature_data = event_data.get("feature")
    
    # Update state
    self.state.add_feature(feature_data)
    
    # Notify display
    self.display.handle_feature_update(feature_data)
```

2. **Custom state tracking**:

```python
# Extend StreamState in models/state.py
class StreamState(BaseModel):
    # Existing fields...
    custom_data: dict[str, Any] = Field(default_factory=dict)
    
    def add_custom_data(self, key: str, value: Any) -> "StreamState":
        return self.model_copy(update={"custom_data": {**self.custom_data, key: value}})
```

3. **Event filtering**:

```python
def should_process_event(self, event_type: str) -> bool:
    """Filter events based on configuration."""
    if self.config.quiet and event_type.startswith("debug."):
        return False
    return True
```

### Error Handling Strategies

1. **Graceful degradation**:

```python
async def _process_event_safe(self, event_type: str, event_data: dict):
    try:
        await self._process_event(event_type, event_data)
    except Exception as e:
        logger.error(f"Error processing {event_type}: {e}")
        # Continue processing other events
```

2. **Recovery mechanisms**:

```python
async def handle_stream_with_retry(self, stream, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self.handle_stream(stream, query)
        except StreamInterruptedError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

## Performance Optimization

### Throttling

Control event processing rate:

```python
if self.config.throttle_ms > 0:
    await asyncio.sleep(self.config.throttle_ms / 1000)
```

### Batch Processing

Group related events:

```python
# Collect text deltas
text_buffer = []
async for event_type, event_data in stream:
    if event_type == "response.output_text.delta":
        text_buffer.append(event_data["text"])
        if len(text_buffer) >= 10:  # Batch size
            self.display.handle_text_delta("".join(text_buffer))
            text_buffer.clear()
```

### Memory Management

Clean up completed tools:

```python
def cleanup_completed_tools(self):
    """Remove completed tools older than threshold."""
    threshold = time.time() - 300  # 5 minutes
    self.state.tools = {
        tid: tool for tid, tool in self.state.tools.items()
        if tool.status != ToolStatus.COMPLETED or tool.end_time > threshold
    }
```

## Testing the Stream Handler

```python
import pytest
from unittest.mock import Mock, AsyncMock

async def test_stream_handler():
    # Mock dependencies
    mock_display = Mock(spec=BaseDisplay)
    mock_registry = Mock(spec=ProcessorRegistry)
    
    # Create handler
    handler = StreamHandler(mock_display, mock_registry)
    
    # Create mock stream
    async def mock_stream():
        yield "response.created", {"id": "resp_123"}
        yield "response.output_text.delta", {"text": "Hello"}
        yield "response.completed", {"usage": {"tokens": 10}}
    
    # Process stream
    state = await handler.handle_stream(mock_stream(), "test query")
    
    # Verify
    assert mock_display.handle_stream_start.called
    assert mock_display.handle_text_delta.called_with("Hello")
    assert state.usage["tokens"] == 10
```

## Integration Points

### With SDK

The stream handler consumes streams from the SDK:

```python
from forge_cli.sdk import astream_response

stream = astream_response(
    input_messages="Query",
    model="gpt-4"
)
await handler.handle_stream(stream, "Query")
```

### With Processors

Routes events to processor registry:

```python
# Handler calls registry
processor = self.processor_registry.get_processor(item_type)
processor.process(item, self.state, self.display)
```

### With Display (V3 Architecture)

Updates display throughout streaming using the V3 snapshot-based architecture:

```python
# V3 Display integration - response snapshots
from forge_cli.display.v3.base import Display

# Handler works with V3 displays
self.display.handle_response(response_snapshot)
self.display.complete()

# Legacy V2 event-based display (deprecated)
self.display.handle_stream_start()
self.display.handle_text_delta(text)
self.display.handle_tool_start(...)
self.display.handle_stream_complete()
```

## Best Practices

1. **Always maintain state consistency**
2. **Handle events idempotently when possible**
3. **Log errors but don't crash on unknown events**
4. **Clean up resources in finally blocks**
5. **Use type hints for all event data**
6. **Test with various event sequences**
7. **Consider memory usage for long streams**

The stream module provides robust, extensible handling of real-time event streams, serving as the core orchestrator that brings together all other components of the system.
