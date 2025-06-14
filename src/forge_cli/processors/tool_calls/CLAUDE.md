# Tool Calls Processors - Tool-Specific Event Processing

## Overview

The tool_calls subdirectory contains specialized processors for handling tool-specific events from the Knowledge Forge API. Each processor is designed to handle a specific tool type (file search, web search, file reader, document finder) and manages the complete lifecycle of tool execution from initiation to completion.

## Directory Structure

```
tool_calls/
├── __init__.py          # Module exports
├── base.py              # Base tool processor interface
├── file_search.py       # File search tool processor
├── web_search.py        # Web search tool processor
├── file_reader.py       # File reader tool processor
└── document_finder.py   # Document finder processor
```

## Architecture & Design

### Design Principles

1. **Specialization**: Each processor handles one specific tool type
2. **Lifecycle Management**: Handle tool states from start to completion
3. **Result Processing**: Transform tool outputs into user-friendly formats
4. **Citation Tracking**: Manage references and citations from tools

### Tool Event Lifecycle

```
Tool Initiated → Tool Running → Tool Completed/Failed
      ↓               ↓                ↓
   Display         Update UI      Show Results
   Loading        Progress        Format Output
```

## Component Details

### base.py - Base Tool Processor Interface

```python
class BaseToolProcessor(OutputProcessor):
    """Base class for all tool-specific processors."""
    
    @abstractmethod
    def get_tool_type(self) -> str:
        """Return the tool type this processor handles."""
        pass
    
    def format_tool_call(self, tool_data: dict) -> str:
        """Format tool call information for display."""
        pass
    
    def process_tool_start(self, event_data: dict, state: StreamState, display: BaseDisplay):
        """Handle tool initiation."""
        pass
    
    def process_tool_complete(self, event_data: dict, state: StreamState, display: BaseDisplay):
        """Handle tool completion."""
        pass
```

### file_search.py - File Search Tool Processor

Handles file search operations across vector stores.

**Key Features:**

- Processes search queries across multiple vector stores
- Extracts and formats file citations
- Manages search progress and results
- Handles document chunks and relevance scores

**Event Types Handled:**

- `response.file_search_call.searching` - Search initiated
- `response.file_search_call.completed` - Search completed

**Processing Flow:**

```python
class FileSearchProcessor(BaseToolProcessor):
    def get_tool_type(self) -> str:
        return "file_search"
    
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        # Extract search parameters
        tool_id = event_data.get("id")
        query = event_data.get("query", "")
        vector_store_ids = event_data.get("vector_store_ids", [])
        
        # Update state
        state.add_tool(tool_id, ToolState(
            tool_type="file_search",
            status=ToolStatus.RUNNING,
            metadata={"query": query, "stores": vector_store_ids}
        ))
        
        # Notify display
        display.handle_file_search_start(
            tool_id=tool_id,
            query=query,
            vector_stores=vector_store_ids
        )
```

**Citation Processing:**

```python
def process_search_results(self, results: List[dict], state: StreamState):
    for result in results:
        # Create citation
        citation = FileCitationAnnotation(
            file_id=result["file_id"],
            file_name=result["file_name"],
            quote=result["content"],
            page_number=result.get("page")
        )
        
        # Register citation
        citation_num = state.add_citation(citation)
```

### web_search.py - Web Search Tool Processor

Manages web search operations and results.

**Key Features:**

- Handles location-aware searches
- Processes search results with snippets
- Manages URL citations
- Formats web content for display

**Event Types Handled:**

- `response.web_search_call.searching` - Search initiated
- `response.web_search_call.completed` - Search completed

**Search Parameters:**

```python
def extract_search_params(self, event_data: dict) -> dict:
    return {
        "query": event_data.get("query"),
        "country": event_data.get("country"),
        "city": event_data.get("city"),
        "max_results": event_data.get("max_results", 10)
    }
```

**Result Processing:**

```python
def process_web_results(self, results: List[dict], state: StreamState):
    for result in results:
        # Create URL citation
        citation = UrlCitationAnnotation(
            url=result["url"],
            title=result["title"],
            snippet=result["snippet"],
            domain=result.get("domain")
        )
        
        # Add to state
        state.add_web_result(citation)
```

### file_reader.py - File Reader Tool Processor

Handles file content reading operations.

**Key Features:**

- Manages file access requests
- Processes file content extraction
- Handles different file formats
- Manages reading progress

**Event Types Handled:**

- `response.file_reader_call.reading` - Reading started
- `response.file_reader_call.completed` - Reading completed

**File Processing:**

```python
class FileReaderProcessor(BaseToolProcessor):
    def process_file_read(self, event_data: dict, state: StreamState):
        file_id = event_data.get("file_id")
        file_name = event_data.get("file_name")
        content_type = event_data.get("content_type")
        
        # Track file access
        state.add_accessed_file(file_id, {
            "name": file_name,
            "type": content_type,
            "accessed_at": datetime.now()
        })
```

### document_finder.py - Document Finder Processor

Discovers and indexes documents.

**Key Features:**

- Document discovery across collections
- Metadata extraction
- Batch document processing
- Collection management

**Event Types Handled:**

- `response.document_finder_call.searching` - Discovery started
- `response.document_finder_call.completed` - Discovery completed

**Discovery Process:**

```python
def process_discovery(self, event_data: dict, state: StreamState):
    collection_id = event_data.get("collection_id")
    filters = event_data.get("filters", {})
    
    # Track discovery operation
    state.add_discovery_operation({
        "collection": collection_id,
        "filters": filters,
        "status": "running"
    })
```

## Usage Guidelines

### For Language Models

When implementing or extending tool processors:

1. **Creating a new tool processor**:

```python
from ..base import BaseToolProcessor
from ...models import ToolState, ToolStatus

class NewToolProcessor(BaseToolProcessor):
    def get_tool_type(self) -> str:
        return "new_tool"
    
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        tool_id = event_data.get("id")
        
        # Always update state first
        state.add_tool(tool_id, ToolState(
            tool_type=self.get_tool_type(),
            status=ToolStatus.RUNNING
        ))
        
        # Then notify display
        display.handle_tool_update(
            tool_type=self.get_tool_type(),
            tool_id=tool_id,
            event_data=event_data
        )
```

2. **Handling tool completion**:

```python
def handle_completion(self, event_data: dict, state: StreamState, display: BaseDisplay):
    tool_id = event_data.get("id")
    results = event_data.get("results", [])
    
    # Update tool state
    tool_state = state.get_tool(tool_id)
    tool_state.status = ToolStatus.COMPLETED
    tool_state.results = results
    
    # Process results
    for result in results:
        self.process_result(result, state, display)
    
    # Notify completion
    display.handle_tool_complete(tool_id, len(results))
```

3. **Error handling**:

```python
def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
    try:
        # Process normally
        self._process_internal(event_data, state, display)
    except Exception as e:
        tool_id = event_data.get("id", "unknown")
        
        # Update state to failed
        if state.has_tool(tool_id):
            tool_state = state.get_tool(tool_id)
            tool_state.status = ToolStatus.FAILED
            tool_state.error = str(e)
        
        # Notify display
        display.handle_tool_error(tool_id, str(e))
```

## Development Guidelines

### Adding New Tool Processors

1. **Create processor file**:

```python
# In new_tool.py
from ..base import BaseToolProcessor
from ...models import ToolState, ToolStatus

class NewToolProcessor(BaseToolProcessor):
    """Processor for new_tool operations."""
    
    def get_tool_type(self) -> str:
        return "new_tool"
```

2. **Export from **init**.py**:

```python
# In __init__.py
from .new_tool import NewToolProcessor

__all__ = [..., "NewToolProcessor"]
```

3. **Register in parent registry**:

```python
# In processors/registry.py
from .tool_calls.new_tool import NewToolProcessor

registry.register("new_tool_call", NewToolProcessor())
```

### Common Patterns

#### Progress Updates

```python
def handle_progress(self, event_data: dict, state: StreamState, display: BaseDisplay):
    tool_id = event_data.get("id")
    progress = event_data.get("progress", 0)
    total = event_data.get("total", 100)
    
    # Update state
    tool_state = state.get_tool(tool_id)
    tool_state.progress = progress / total
    
    # Update display
    display.handle_tool_progress(
        tool_id=tool_id,
        progress=progress,
        total=total,
        message=f"Processing {progress}/{total} items"
    )
```

#### Result Formatting

```python
def format_results(self, results: List[dict]) -> List[str]:
    formatted = []
    for idx, result in enumerate(results, 1):
        formatted.append(
            f"{idx}. {result['title']}\n"
            f"   {result['snippet']}\n"
            f"   Source: {result['source']}"
        )
    return formatted
```

## Best Practices

1. **State Management**:
   - Always update state before display
   - Use appropriate tool status values
   - Track metadata for debugging

2. **Display Coordination**:
   - Provide rich context to display
   - Use consistent formatting
   - Handle both start and completion events

3. **Error Resilience**:
   - Handle missing fields gracefully
   - Log warnings for unexpected data
   - Fail gracefully with user-friendly messages

4. **Performance**:
   - Process results incrementally when possible
   - Avoid storing large data in state
   - Use streaming for large result sets

## Testing Tool Processors

```python
import pytest
from unittest.mock import Mock
from forge_cli.processors.tool_calls.file_search import FileSearchProcessor

def test_file_search_processor():
    processor = FileSearchProcessor()
    mock_state = Mock()
    mock_display = Mock()
    
    # Test search start
    event_data = {
        "id": "search_123",
        "query": "machine learning",
        "vector_store_ids": ["vs_123"]
    }
    
    processor.process(event_data, mock_state, mock_display)
    
    # Verify state update
    mock_state.add_tool.assert_called_once()
    
    # Verify display notification
    mock_display.handle_file_search_start.assert_called_once()
```

## Integration with Main System

Tool processors integrate seamlessly with:

1. **Stream Handler**: Receives tool events and routes to processors
2. **Display Strategies**: Format tool outputs for different UIs
3. **State Management**: Track tool execution and results
4. **Citation System**: Manage references from tool outputs

The tool_calls processors provide specialized handling for each tool type, ensuring consistent user experience and proper state management throughout tool execution lifecycles.
