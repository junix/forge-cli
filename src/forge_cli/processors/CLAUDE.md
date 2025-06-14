# Processors Module - Event Processing System

## Overview

The processors module implements the event processing pipeline for the Forge CLI. It transforms raw API events into structured data and coordinates with display strategies to present information to users. The module uses a registry pattern for dynamic processor selection based on event types.

## Directory Structure

```
processors/
├── __init__.py              # Module exports
├── base.py                  # Base processor interface
├── registry.py              # Dynamic processor registry
├── reasoning.py             # Reasoning/thinking block processor
├── message.py               # Final message processor with citations
└── tool_calls/              # Tool-specific processors
    ├── __init__.py          # Tool processor exports
    ├── base.py              # Base tool processor interface
    ├── file_search.py       # File search tool processor
    ├── web_search.py        # Web search tool processor
    ├── file_reader.py       # File reader tool processor
    └── document_finder.py   # Document finder processor
```

## Architecture & Design

### Core Design Patterns

1. **Registry Pattern**: Dynamic processor registration and lookup
2. **Strategy Pattern**: Different processors for different event types
3. **Chain of Responsibility**: Event flows through appropriate processors
4. **Observer Pattern**: Processors notify displays of state changes

### Event Processing Flow

```
API Event Stream
    ↓
StreamHandler (receives event)
    ↓
ProcessorRegistry (selects processor)
    ↓
Specific Processor (processes event)
    ↓
Display Strategy (presents to user)
```

### Key Components

#### base.py - Base Processor Interface

```python
class OutputProcessor(ABC):
    """Base interface for all processors."""
    
    @abstractmethod
    def can_process(self, output_type: str) -> bool:
        """Check if processor handles this output type."""
        pass
    
    @abstractmethod
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay) -> None:
        """Process the event and update display."""
        pass
```

#### registry.py - Processor Registry System

The registry manages processor registration and selection:

```python
class ProcessorRegistry:
    """Central registry for output processors."""
    
    def register(self, output_type: str, processor: OutputProcessor):
        """Register a processor for an output type."""
        
    def get_processor(self, output_type: str) -> Optional[OutputProcessor]:
        """Get processor for the output type."""
        
    def process(self, output_type: str, event_data: dict, state: StreamState, display: BaseDisplay):
        """Route event to appropriate processor."""
```

Default initialization:

```python
def initialize_default_registry() -> ProcessorRegistry:
    registry = ProcessorRegistry()
    
    # Register all processors
    registry.register("summary", ReasoningProcessor())
    registry.register("reasoning", ReasoningProcessor())
    registry.register("message", MessageProcessor())
    registry.register("file_search_call", FileSearchProcessor())
    registry.register("web_search_call", WebSearchProcessor())
    # ... more registrations
    
    return registry
```

#### reasoning.py - Reasoning/Thinking Processor

Handles reasoning blocks (thinking/analysis):

- Extracts reasoning content from events
- Tracks reasoning state
- Updates display with thinking indicators

```python
class ReasoningProcessor(OutputProcessor):
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        # Extract reasoning content
        content = event_data.get("content", "")
        
        # Update state
        state.add_reasoning(content)
        
        # Update display
        display.handle_reasoning_update(content)
```

#### message.py - Message Processor with Citations

Processes final response messages:

- Handles text deltas for streaming
- Processes annotations and citations
- Maintains citation registry
- Formats output with reference markers

Key features:

- Citation extraction and numbering
- Annotation parsing (file and URL citations)
- Integration with display for formatted output

## Tool Processors (tool_calls/)

### Base Tool Processor

```python
class BaseToolProcessor(OutputProcessor):
    """Base for all tool processors."""
    
    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        
    def format_tool_call(self, tool_data: dict) -> str:
        """Format tool call for display."""
```

### Specialized Tool Processors

#### file_search.py - File Search Processor

- Processes file search initiation and completion
- Extracts search parameters and results
- Formats file citations with metadata

#### web_search.py - Web Search Processor

- Handles web search execution
- Processes search results and snippets
- Formats URL citations

#### file_reader.py - File Reader Processor

- Manages file reading operations
- Tracks file access
- Handles content extraction

#### document_finder.py - Document Finder Processor

- Processes document discovery
- Manages document metadata
- Handles batch operations

## Usage Guidelines

### For Language Models

When working with processors:

1. **Creating a new processor**:

```python
from forge_cli.processors.base import OutputProcessor
from forge_cli.models import StreamState
from forge_cli.display.base import BaseDisplay

class CustomProcessor(OutputProcessor):
    def can_process(self, output_type: str) -> bool:
        return output_type == "custom_type"
    
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        # Extract data
        custom_data = event_data.get("data", {})
        
        # Update state
        state.add_custom_data(custom_data)
```

### Update Display

2. **Registering a processor**:

```python
from forge_cli.processors.registry import ProcessorRegistry

registry = ProcessorRegistry()
registry.register("custom_type", CustomProcessor())
```

3. **Using the registry**:

```python
# Process an event
registry.process(
    output_type="file_search_call",
    event_data={"query": "machine learning"},
    state=stream_state,
    display=rich_display
)
```

## Development Guidelines

### Adding New Processors

1. **Determine processor location**:
   - General processors: Add to `processors/` root
   - Tool processors: Add to `processors/tool_calls/`

2. **Implement the interface**:

   ```python
   # For general processor
   from .base import OutputProcessor
   
   # For tool processor
   from .tool_calls.base import BaseToolProcessor
   ```

3. **Register in registry.py**:

   ```python
   # In initialize_default_registry()
   registry.register("new_output_type", NewProcessor())
   ```

4. **Handle state updates**:
   - Always update StreamState appropriately
   - Maintain consistency with other processors

5. **Coordinate with display**:
   - Call appropriate display methods
   - Pass formatted data, not raw events

### Processing Best Practices

1. **Error Handling**:

```python
def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
    try:
        data = event_data.get("required_field")
        if not data:
            logger.warning(f"Missing required field in {self.__class__.__name__}")
            return
        # Process data
    except Exception as e:
        logger.error(f"Error in {self.__class__.__name__}: {e}")
        display.handle_error(str(e))
```

2. **State Management**:

```python
# Always check state before updating
if not state.has_tool(tool_id):
    state.add_tool(tool_id, ToolState(...))

# Update existing state
tool_state = state.get_tool(tool_id)
tool_state.status = ToolStatus.COMPLETED
```

3. **Display Coordination**:

```python
# Provide rich context to display
display.handle_tool_update(
    tool_type="file_search",
    tool_id=tool_id,
    status="searching",
    metadata={"query": query, "stores": vector_stores}
)
```

## Dependencies & Interactions

### Imports

- Uses relative imports within processors/
- Imports models from forge_cli.models
- Imports display base from forge_cli.display.base

### Integration Points

1. **With StreamHandler**:
   - StreamHandler routes events to registry
   - Registry selects and executes processors

2. **With Display Strategies**:
   - Processors call display methods
   - Display strategies format processor output

3. **With Models**:
   - Processors create model instances
   - Update StreamState and tool states

### Event Type Mapping

Common event types and their processors:

```python
EVENT_PROCESSOR_MAP = {
    "reasoning": ReasoningProcessor,
    "message": MessageProcessor,
    "file_search_call": FileSearchProcessor,
    "web_search_call": WebSearchProcessor,
    "file_reader_call": FileReaderProcessor,
    "document_finder_call": DocumentFinderProcessor,
}
```

## Common Patterns

### Tool Processing Pattern

```python
class ToolProcessor(BaseToolProcessor):
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        # 1. Extract tool data
        tool_id = event_data.get("id")
        tool_params = event_data.get("parameters", {})
        
        # 2. Update tool state
        state.add_tool(tool_id, ToolState(
            tool_type=self.get_tool_type(),
            status=ToolStatus.RUNNING
        ))
        
        # 3. Notify display
        display.handle_tool_start(
            tool_type=self.get_tool_type(),
            tool_id=tool_id,
            parameters=tool_params
        )
```

### Citation Processing Pattern

```python
def process_citations(self, annotations: List[dict], state: StreamState):
    for annotation in annotations:
        if annotation["type"] == "file_citation":
            citation = FileCitationAnnotation(**annotation)
            citation_num = state.add_citation(citation)
            # Process citation with number
```

## Testing Processors

When testing processors:

1. **Mock dependencies**:

```python
mock_state = Mock(spec=StreamState)
mock_display = Mock(spec=BaseDisplay)
```

2. **Test event processing**:

```python
processor = FileSearchProcessor()
processor.process(
    event_data={"query": "test"},
    state=mock_state,
    display=mock_display
)
assert mock_display.handle_tool_start.called
```

3. **Verify state updates**:

```python
assert mock_state.add_tool.called_with(
    "tool_123",
    ToolState(tool_type="file_search", status=ToolStatus.RUNNING)
)
```

## Performance Considerations

1. **Lightweight Processing**: Keep processors focused on data transformation
2. **Avoid Blocking**: Use async operations when needed
3. **Efficient State Updates**: Batch updates when possible
4. **Memory Management**: Don't store large data in processors

The processors module serves as the brain of the event processing system, transforming raw API events into meaningful user presentations while maintaining system state and coordinating with display strategies.
