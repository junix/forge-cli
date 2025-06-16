# Models Module - Data Structures and Type Definitions

## Overview

The models module defines core internal data structures for the Forge CLI system, focusing on conversation management and stream state tracking. API response and request types are centralized in `response/_types/` for consistency with the OpenAPI-generated type system.

## Directory Structure

```
models/
├── __init__.py           # Module exports
├── conversation.py       # Chat conversation management
└── state.py             # Stream state management
```

**Note:** Output types and event definitions are now centralized in `response/_types/` for consistency with the OpenAPI-generated type system.

## Architecture & Design

### Design Principles

1. **Type Safety**: All data structures use Pydantic models with comprehensive validation
2. **Immutability**: Where appropriate, Pydantic's frozen models prevent accidental mutations
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

**Note:** Output types and event definitions have been migrated to `response/_types/` directory. For response structures and event types, import from:

```python
from forge_cli.response._types import (
    ResponseReasoningItem,     # Thinking/analysis blocks
    ResponseOutputMessage,     # Final response messages  
    ResponseFileSearchToolCall, # File search tool calls
    ResponseWebSearchToolCall,  # Web search tool calls
    Annotation,               # Citation annotations
    # ... and many more comprehensive types
)
```

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

2. **Use proper response types**: Import types from `response/_types` for API structures

   ```python
   from forge_cli.response._types import ResponseFileSearchToolCall, Annotation
   
   # Work with file search results from API responses
   if isinstance(item, ResponseFileSearchToolCall):
       # Results are accessed through response methods
       # results = response.get_file_search_results(item.id)
   
   # Handle annotations in responses
   if isinstance(annotation, Annotation):
       print(f"Citation: {annotation.text}")
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

1. **Choose the right location**:
   - `conversation.py`: Chat-related structures
   - `state.py`: State tracking structures
   - `response/_types/`: API response and request types (preferred for most new types)

2. **For new API types**: Add to `response/_types` directory following OpenAPI patterns

3. **For internal types**: Follow existing patterns in this module:

   ```python
   from pydantic import BaseModel, Field
   from typing import Optional, Any
   
   class NewStateType(BaseModel):
       """Description of what this tracks."""
       identifier: str
       metadata: dict[str, Any] = Field(default_factory=dict)
       status: Optional[str] = None
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
- Pydantic and standard library imports (pydantic, typing, enum)

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

1. **Immutability**: Use Pydantic's frozen models for data that shouldn't change
2. **Defaults**: Provide sensible defaults using Field() for optional fields
3. **Validation**: Add field validators and model validators when needed
4. **Documentation**: Include docstrings for all classes and complex fields
5. **Type Completeness**: Ensure all fields have type annotations

This module serves as the foundation for type safety throughout the Forge CLI system. When extending functionality, always define new types here first to maintain consistency and enable proper type checking across the codebase.
