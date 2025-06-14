# Debug Script - Multi-Tool Support Examples

The updated `debug.py` script now supports multi-tool requests, custom queries, and flexible task combinations.

## New Features

### 1. Custom Query Support (`--query` / `-q`)
You can now pass custom queries instead of using the default messages:

```bash
# Single tool with custom query
python debug.py --task file-search -q "Find information about neural networks"

# Web search with custom query
python debug.py --task web-search -q "What happened in AI today?"

# Plain chat with custom query
python debug.py -q "Explain quantum computing in simple terms"
```

### 2. Multi-Tool Support (`--task` accepts multiple values)
You can now combine multiple tools in a single request:

```bash
# Combine file search and web search
python debug.py --task file-search web-search -q "Compare historical research with current developments in AI"

# Use all three tools together
python debug.py --task file-search web-search file-reader -q "Analyze this document and find related information"

# File search + web search with custom vector store
python debug.py --task file-search web-search --vector-store-id my-vec-123 -q "What are transformers in machine learning?"
```

### 3. Default Queries for Multi-Tool Combinations
When using multiple tools without a custom query, smart defaults are used:

- **file-search + web-search**: "Compare information from the documents with current web information on artificial intelligence advancements."
- **file-reader + file-search**: "Analyze the uploaded file and search for related information in the vector store."
- **Other combinations**: "Provide comprehensive analysis using all available tools."

## Usage Examples

### Basic Examples

```bash
# Plain chat with custom query
python debug.py -q "Hello, how are you?"

# Single tool usage
python debug.py --task file-search
python debug.py --task web-search
python debug.py --task file-reader

# With custom parameters
python debug.py --task file-search --vector-store-id vec_abc123 -q "Find policy documents"
python debug.py --task file-reader --file-id file_xyz789 -q "Summarize this document"
```

### Multi-Tool Examples

```bash
# Research mode: combine document search with web search
python debug.py --task file-search web-search \
  -q "What are the latest developments in LLMs and how do they compare to foundational research?"

# Analysis mode: read file and search for related info
python debug.py --task file-reader file-search \
  --file-id file_123 \
  --vector-store-id vec_456 \
  -q "Analyze this document and find similar content in our knowledge base"

# Comprehensive mode: use all available tools
python debug.py --task file-reader file-search web-search \
  -q "Analyze the uploaded document, search for related information, and compare with current web data"
```

### Advanced Options

```bash
# With effort level and model selection
python debug.py --task file-search web-search \
  --effort high \
  --model qwen-max-latest \
  -q "Comprehensive analysis of transformer architectures"

# With tool choice constraints
python debug.py --task file-search web-search \
  --tool-choice required \
  -q "Must use tools to answer: What is RAG?"

# Specific tool choice
python debug.py --task file-search \
  --tool-choice '{"type": "file_search"}' \
  -q "Search for deployment procedures"
```

## Multi-Tool Request Structure

When multiple tasks are specified, the debug script creates a request with multiple tools:

```json
{
  "model": "qwen3-235b-a22b",
  "effort": "low",
  "store": true,
  "input": [
    {
      "role": "user",
      "id": "debug_message_1",
      "content": "Your custom query here"
    }
  ],
  "tools": [
    {
      "type": "file_search",
      "vector_store_ids": ["vec_id"],
      "max_num_results": 5
    },
    {
      "type": "web_search",
      "search_context_size": "medium",
      "user_location": {
        "type": "approximate",
        "country": "US",
        "city": "San Francisco"
      }
    }
  ]
}
```

## Event Handling

The debug script now properly handles events from multiple tools:

- `response.file_search_call.searching` - File search started
- `response.file_search_call.completed` - File search completed with results
- `response.web_search_call.searching` - Web search started
- `response.web_search_call.completed` - Web search completed with results

## Tips

1. **Order doesn't matter**: `--task file-search web-search` is the same as `--task web-search file-search`
2. **File reader is special**: When included, it adds file content to the input rather than as a tool
3. **Custom queries**: Always use `-q` when you want specific information
4. **Debugging**: The script shows detailed event information to help understand the API flow