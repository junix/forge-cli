# Multi-Tool Usage in Knowledge Forge

This directory contains examples demonstrating how to use multiple tools together in Knowledge Forge API requests.

## Overview

Knowledge Forge supports using multiple tools in a single request, enabling sophisticated workflows that combine different information sources:

- **File Search**: Search through documents stored in vector stores
- **Web Search**: Get current information from the internet

## Scripts

### 1. `hello-multi-tools.py` (Full Implementation)
A complete implementation with streaming support, rich formatting, and multiple usage modes.

**Features:**
- Multiple usage modes (research, fact-check, comprehensive)
- Real-time streaming with tool event tracking
- Rich terminal output with live updates
- Combined results from file and web searches

**Usage:**
```bash
# Research mode (default)
python hello-multi-tools.py -q "What are recent AI breakthroughs?" --vec-id vec123

# Fact checking mode
python hello-multi-tools.py --mode fact_check -q "Is GPT-4 really multimodal?" --vec-id vec123

# With location context
python hello-multi-tools.py -q "Local AI events" --country US --city "San Francisco"

# JSON output
python hello-multi-tools.py -q "AI safety research" --json --vec-id vec123
```

### 2. `demo-multi-tools-concept.py` (Conceptual Demo)
A standalone demonstration that shows the concepts without requiring SDK dependencies.

**Features:**
- Shows request structure for multi-tool usage
- Demonstrates different use cases
- Explains response handling patterns
- Provides best practices

**Usage:**
```bash
python demo-multi-tools-concept.py
```

## Use Cases

### 1. Research Assistant
Combines historical knowledge from documents with current information from the web:
```python
tools = [
    {
        "type": "file_search",
        "vector_store_ids": ["vec_research_papers"],
        "max_num_results": 10
    },
    {
        "type": "web_search"
    }
]
```

### 2. Fact Checking
Verifies information across multiple sources for accuracy:
```python
tools = [
    {
        "type": "file_search",
        "vector_store_ids": ["vec_trusted_sources", "vec_references"],
        "max_num_results": 20
    },
    {
        "type": "web_search",
        "search_context_size": "high"
    }
]
```

### 3. Location-Aware Search
Combines documents with location-specific web results:
```python
tools = [
    {
        "type": "file_search",
        "vector_store_ids": ["vec_local_info"]
    },
    {
        "type": "web_search",
        "user_location": {
            "type": "approximate",
            "country": "US",
            "city": "San Francisco"
        }
    }
]
```

## Response Handling

When using multiple tools, you'll receive tool-specific events in the response stream:

1. **Tool Execution Events**:
   - `response.file_search_call.searching`
   - `response.file_search_call.completed`
   - `response.web_search_call.searching`
   - `response.web_search_call.completed`

2. **Results Structure**:
   - File search: Returns document chunks with page citations
   - Web search: Returns web page snippets with URLs

3. **Combined Response**:
   - The AI synthesizes information from all tools
   - Provides proper attribution for each source
   - Can compare and contrast information

## Best Practices

1. **Tool Selection**:
   - Use file search for reference/historical information
   - Use web search for current events and real-time data
   - Combine both for comprehensive research

2. **Performance**:
   - Adjust `max_num_results` based on needs
   - Use appropriate `effort` levels
   - Consider `search_context_size` for web searches

3. **Query Design**:
   - Be specific about information needs
   - Include temporal context ("latest", "historical")
   - Ask comparative questions to leverage both tools

4. **Error Handling**:
   - Tools operate independently
   - If one tool fails, others continue
   - Always check tool completion status

## Configuration Options

### File Search Tool
```python
{
    "type": "file_search",
    "vector_store_ids": ["vec_id1", "vec_id2"],  # Required
    "max_num_results": 10  # Optional, per vector store
}
```

### Web Search Tool
```python
{
    "type": "web_search",
    "search_context_size": "medium",  # Optional: low, medium, high
    "user_location": {  # Optional
        "type": "approximate",
        "country": "US",
        "city": "San Francisco",
        "region": "California",
        "timezone": "America/Los_Angeles"
    }
}
```

## Dependencies

- **hello-multi-tools.py**: Requires the Knowledge Forge SDK and optional rich library
- **demo-multi-tools-concept.py**: No external dependencies

## See Also

- `hello-file-search.py`: File search only example
- `hello-web-search.py`: Web search only example
- `sdk.py`: SDK implementation details