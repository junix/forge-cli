# Models Module - Data Structures and Type Definitions

## Overview

The models module defines all data structures and types used throughout the Forge CLI system. It provides a centralized location for type definitions, ensuring consistency across the codebase and enabling strong type checking.

## Directory Structure

```
models/
├── __init__.py           # Module exports
├── conversation.py       # Chat conversation management
├── events.py            # Event type definitions for streaming
├── output_types.py      # Response output type structures
└── state.py             # Stream state management
```

## Architecture & Design

### Design Principles

1. **Type Safety**: All data structures use Python dataclasses with type annotations
2. **Immutability**: Where appropriate, frozen dataclasses prevent accidental mutations
3. **Clear Naming**: Types follow descriptive naming patterns (e.g., `FileSearchCall`, `StreamState`)
4. **Minimal Dependencies**: Models are pure data structures with no business logic

### Key Components

#### conversation.py - Conversation Management

- **Conversation**: Manages multi-turn chat sessions
- **Message**: Individual message with role and content
- **ConversationHistory**: Persistent conversation storage

```python
from forge_cli.models import Conversation, Message

# Create a conversation
conv = Conversation()
conv.add_message(Message(role="user", content="Hello"))
conv.add_message(Message(role="assistant", content="Hi there!"))
```

#### events.py - Event Type System

- **EventType**: Enum of all possible event types from the API
- **Event**: Base event structure with type and data
- **EventData**: Type-safe event data structures

Event types include:

- Response lifecycle: `created`, `in_progress`, `completed`
- Output streaming: `output_text.delta`, `output_text.done`
- Tool execution: `file_search_call.searching`, `web_search_call.completed`

#### output_types.py - Response Output Types

Core response structures:

- **SummaryItem**: Brief response summaries
- **ReasoningItem**: Thinking/analysis blocks
- **MessageItem**: Final response messages
- **FileSearchCall**: File search tool invocations
- **WebSearchCall**: Web search tool invocations
- **FileReaderCall**: File reading operations
- **DocumentFinderCall**: Document discovery

Citation and annotation types:

- **Annotation**: Base annotation class
- **FileCitationAnnotation**: References to file content
- **UrlCitationAnnotation**: Web URL references

#### state.py - Stream State Management

- **StreamState**: Tracks current streaming session state
- **ToolState**: Individual tool execution state
- **ToolStatus**: Enum for tool states (pending, running, completed, failed)

```python
from forge_cli.models import StreamState, ToolState

# Stream state tracks all active operations
state = StreamState()
state.add_tool("file_search_123", ToolState(
    tool_type="file_search",
    status=ToolStatus.RUNNING
))
```

## Usage Guidelines

### For Language Models

When working with this module:

1. **Import from models package**: Use relative imports within models, absolute from outside

   ```python
   # From within models/
   from .conversation import Conversation
   
   # From outside models/
   from forge_cli.models import Conversation, Message
   ```

2. **Create instances with proper types**: Always provide required fields

   ```python
   from forge_cli.models import FileSearchCall, FileCitationAnnotation
   
   # Create a file search call
   search = FileSearchCall(
       query="machine learning",
       vector_store_ids=["vs_123", "vs_456"]
   )
   
   # Create a citation
   citation = FileCitationAnnotation(
       file_id="file_abc",
       file_name="research.pdf",
       quote="The key finding was...",
       page_number=42
   )
   ```

3. **Handle optional fields**: Many fields have sensible defaults

   ```python
   from forge_cli.models import StreamState
   
   # Minimal creation
   state = StreamState()  # Uses all defaults
   
   # With options
   state = StreamState(
       response_id="resp_123",
       model="gpt-4",
       is_complete=False
   )
   ```

## Development Guidelines

### Adding New Types

1. **Choose the right file**:
   - `conversation.py`: Chat-related structures
   - `events.py`: New event types from API
   - `output_types.py`: New output formats or tool types
   - `state.py`: State tracking structures

2. **Follow existing patterns**:

   ```python
   from dataclasses import dataclass, field
   from typing import Optional, List
   
   @dataclass
   class NewToolCall:
       """Description of what this tool does."""
       tool_id: str
       parameters: dict = field(default_factory=dict)
       status: Optional[str] = None
   ```

3. **Export from **init**.py**:

   ```python
   from .output_types import NewToolCall
   __all__.append("NewToolCall")
   ```

### Type Annotations

Always use specific types:

```python
# Good
vector_store_ids: List[str]
annotations: List[Annotation]
metadata: Dict[str, Any]

# Avoid
vector_store_ids: list
annotations: list
metadata: dict
```

## Dependencies & Interactions

### Internal Dependencies

- Models are self-contained with minimal cross-dependencies
- Only standard library imports (dataclasses, typing, enum)

### Used By

- **Processors**: Parse API events into model objects
- **Display**: Format model objects for output
- **Stream Handler**: Maintain state using these models
- **SDK**: Return these types from API calls
- **Chat Controller**: Manage conversations

### Integration Points

```python
# Processor creates model objects
annotation = FileCitationAnnotation(
    file_id=event_data["file_id"],
    quote=event_data["quote"]
)

# Display formats model objects
def format_citation(self, citation: FileCitationAnnotation) -> str:
    return f"[{citation.file_name}] {citation.quote}"

# Stream handler updates state
self.state.add_annotation(annotation)
```

## Common Patterns

### Factory Methods

Some models provide factory methods for common cases:

```python
# Create from API response
message = Message.from_api_response(response_data)

# Create with defaults
conv = Conversation.new_session()
```

### Serialization

Models support JSON serialization for persistence:

```python
# To JSON
data = conversation.to_dict()

# From JSON
conv = Conversation.from_dict(data)
```

## Best Practices

1. **Immutability**: Use frozen dataclasses for data that shouldn't change
2. **Defaults**: Provide sensible defaults for optional fields
3. **Validation**: Add validators in **post_init** when needed
4. **Documentation**: Include docstrings for all classes and complex fields
5. **Type Completeness**: Ensure all fields have type annotations

This module serves as the foundation for type safety throughout the Forge CLI system. When extending functionality, always define new types here first to maintain consistency and enable proper type checking across the codebase.
