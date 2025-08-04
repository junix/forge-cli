# Response Types - OpenAPI-Generated Type Definitions

## Overview

The `_types` directory contains OpenAPI-generated type definitions for the Knowledge Forge API. These types provide comprehensive, type-safe access to all API request and response structures. The types are automatically generated from the OpenAPI specification and should not be manually edited.

## Directory Structure

```
_types/
├── CLAUDE.md                                    # This documentation file
├── __init__.py                                  # Type exports and public API
├── _models.py                                   # Base model definitions
├── annotations.py                               # Citation and annotation types
├── chunk.py                                     # Document chunk types
├── request.py                                   # Request type definitions
├── response.py                                  # Core response types
├── tool.py                                      # Tool definition types
├── tool_param.py                               # Tool parameter types
├── [100+ generated type files]                 # Individual type definitions
└── [Event types, tool types, etc.]             # Categorized type files
```

## Type Categories

### Core Response Types

#### response.py - Main Response Structure
- **Response**: Primary response object containing all output
- **ResponseStatus**: Response status enumeration
- **ResponseUsage**: Token usage and billing information

#### response_output_*.py - Output Types
- **ResponseOutputMessage**: Final assistant messages
- **ResponseOutputText**: Text content with formatting
- **ResponseOutputRefusal**: Refusal responses
- **ResponseOutputItem**: Union of all output types

#### response_reasoning_*.py - Reasoning Types
- **ResponseReasoningItem**: AI reasoning and thinking blocks
- **ResponseReasoningSummary**: Reasoning summaries

### Tool Call Types

#### File Search Tools
- **ResponseFileSearchToolCall**: File search execution results
- **FileSearchTool**: File search tool configuration
- **FileSearchToolParam**: File search parameters

#### Web Search Tools
- **ResponseFunctionWebSearch**: Web search execution results
- **WebSearchTool**: Web search tool configuration
- **WebSearchToolParam**: Web search parameters

#### Function Tools
- **ResponseFunctionToolCall**: Custom function execution
- **FunctionTool**: Function tool definitions
- **FunctionDefinition**: Function schemas

#### Computer Tools
- **ResponseComputerToolCall**: Computer automation results
- **ComputerTool**: Computer tool configuration

#### Document Tools
- **ResponseFunctionFileReader**: File reader results
- **ResponseFunctionPageReader**: Page reader results
- **ResponseListDocumentsToolCall**: Document listing results

### Event Types

#### Streaming Events
- **ResponseStreamEvent**: Base streaming event type
- **ResponseTextDeltaEvent**: Text delta updates
- **ResponseCompletedEvent**: Response completion
- **ResponseErrorEvent**: Error events

#### Tool Events
- **ResponseFileSearchCallCompletedEvent**: File search completion
- **ResponseWebSearchCallSearchingEvent**: Web search progress
- **ResponseFunctionCallArgumentsDeltaEvent**: Function call updates

### Request Types

#### request.py - Request Structures
- **ResponseCreateParams**: Response creation parameters
- **ResponseRetrieveParams**: Response retrieval parameters
- **InputMessage**: Input message structures
- **InputContent**: Input content types

#### Tool Configuration
- **Tool**: Union of all tool types
- **ToolParam**: Tool parameter union
- **ToolChoice**: Tool selection options

### Annotation Types

#### annotations.py - Citation Types
- **Annotation**: Base annotation type
- **AnnotationFileCitation**: File citations with quotes
- **AnnotationURLCitation**: Web URL citations
- **AnnotationFilePath**: File path references

## Usage Guidelines

### Importing Types

Always import from the centralized location:

```python
# Core response types
from forge_cli.response._types.response import Response, ResponseStatus
from forge_cli.response._types.response_output_message import ResponseOutputMessage
from forge_cli.response._types.response_reasoning_item import ResponseReasoningItem

# Tool call types
from forge_cli.response._types.response_file_search_tool_call import ResponseFileSearchToolCall
from forge_cli.response._types.response_function_web_search import ResponseFunctionWebSearch

# Request types
from forge_cli.response._types.request import ResponseCreateParams
from forge_cli.response._types.tool import Tool, FileSearchTool, WebSearchTool

# Annotation types
from forge_cli.response._types.annotations import AnnotationFileCitation, AnnotationURLCitation
```

### Type Safety with TypeGuards

Use TypeGuard functions for safe type narrowing:

```python
from forge_cli.response.type_guards.output_items import (
    is_file_search_call, is_message_item, is_reasoning_item
)

def process_output_item(item: ResponseOutputItem) -> None:
    if is_file_search_call(item):
        # Type checker knows item is ResponseFileSearchToolCall
        print(f"File search queries: {item.queries}")
        print(f"Status: {item.status}")
    elif is_message_item(item):
        # Type checker knows item is ResponseOutputMessage
        print(f"Message content: {item.content}")
    elif is_reasoning_item(item):
        # Type checker knows item is ResponseReasoningItem
        print(f"Reasoning: {item.content}")
```

### Working with Responses

```python
from forge_cli.response._types.response import Response

def process_response(response: Response) -> None:
    """Process a complete response with type safety."""
    # Access response metadata
    print(f"Response ID: {response.id}")
    print(f"Status: {response.status}")
    
    # Access output text (if available)
    if response.output_text:
        print(f"Output: {response.output_text}")
    
    # Process output items
    for item in response.output:
        if is_message_item(item):
            print(f"Message: {item.content}")
        elif is_file_search_call(item):
            print(f"File search: {item.queries}")
    
    # Access usage information
    if response.usage:
        print(f"Tokens used: {response.usage.total_tokens}")
```

### Creating Requests

```python
from forge_cli.response._types.request import ResponseCreateParams
from forge_cli.response._types.tool import FileSearchTool, WebSearchTool

def create_typed_request(query: str, vector_store_ids: list[str]) -> ResponseCreateParams:
    """Create a typed request with tools."""
    return ResponseCreateParams(
        input_messages=[{
            "role": "user",
            "content": query
        }],
        model="qwen-max-latest",
        tools=[
            FileSearchTool(
                type="file_search",
                vector_store_ids=vector_store_ids
            ),
            WebSearchTool(
                type="web_search"
            )
        ]
    )
```

## Code Generation

### OpenAPI Source

These types are generated from the Knowledge Forge OpenAPI specification:

- **Source**: OpenAPI 3.0 specification
- **Generator**: Custom Python type generator
- **Validation**: Pydantic v2 models with comprehensive validation
- **Updates**: Automatically updated when API changes

### Generation Process

1. **OpenAPI Parsing**: Parse the OpenAPI specification
2. **Type Generation**: Generate Pydantic models for all schemas
3. **Validation**: Add field validators and constraints
4. **Documentation**: Include docstrings and field descriptions
5. **Export**: Update `__init__.py` with public exports

### Maintenance

**DO NOT EDIT MANUALLY**: These files are automatically generated and will be overwritten.

For type modifications:
1. Update the OpenAPI specification
2. Regenerate types using the generation tool
3. Update TypeGuard functions if needed
4. Update documentation and examples

## Related Components

- **TypeGuards** (`../type_guards/`) - Safe type narrowing functions
- **SDK** (`../../sdk/`) - Uses these types for API communication
- **Display** (`../../display/`) - Renders these types for output
- **Models** (`../../models/`) - Internal models that complement these types

## Best Practices

### Type Usage

1. **Import from _types**: Always import from the centralized location
2. **Use TypeGuards**: Use TypeGuard functions for type narrowing
3. **Validate Input**: Let Pydantic handle validation automatically
4. **Handle Optionals**: Check for None values on optional fields
5. **Use Union Types**: Work with union types using TypeGuards

### Performance

1. **Lazy Imports**: Use TYPE_CHECKING for type-only imports
2. **Efficient Validation**: Pydantic provides optimized validation
3. **Memory Usage**: Types are memory-efficient with proper field definitions
4. **Serialization**: Built-in JSON serialization is optimized

### Error Handling

1. **Validation Errors**: Handle Pydantic ValidationError appropriately
2. **Type Errors**: Use TypeGuards to avoid runtime type errors
3. **Missing Fields**: Handle optional fields gracefully
4. **API Changes**: Update types when API specification changes

The `_types` directory provides the foundation for type-safe interaction with the Knowledge Forge API, ensuring that all API communication is properly typed and validated.
