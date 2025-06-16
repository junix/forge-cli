# Tools Integration API Reference

This document provides a comprehensive guide for integrating and utilizing tools with the Knowledge Forge Response API. The Response API enables advanced RAG (Retrieval-Augmented Generation) capabilities with built-in tool execution and streaming events.

## Overview

Knowledge Forge implements a **Response API**, not a Chat Completions API. The key differences:

- **Request Object**: Single `Request` object with comprehensive parameters
- **Response Object**: Structured `Response` object with status tracking
- **Tool Execution**: Built-in tools execute automatically; external tools return for client execution
- **Streaming**: Rich Server-Sent Events (SSE) with detailed progress tracking
- **Citations**: Automatic citation management with Unicode formatting

## Request Structure

### Basic Request Format

```json
{
  "model": "kf-alpha",
  "user": "user-123",
  "input": [
    {"type": "input_text", "text": "What is the company's refund policy?"}
  ],
  "tools": [
    {
      "type": "file_search",
      "vector_store_ids": ["vs_company_docs"],
      "max_num_results": 8
    }
  ],
  "effort": "high",
  "stream": true
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | ✓ | Model ID (e.g., "kf-alpha") |
| `user` | string | ✓ | Unique user identifier |
| `input` | string \| array | ✓ | Text or array of input items |
| `tools` | array | - | Available tools for the request |
| `effort` | string | - | "low", "medium", "high", "dev" (default: "low") |
| `instructions` | string | - | System instructions |
| `stream` | boolean | - | Enable streaming (default: false) |
| `temperature` | number | - | Sampling temperature (0-2) |
| `max_output_tokens` | integer | - | Maximum tokens to generate |

## Tool Definitions

### Tool Structure

All tools follow this pattern:

```json
{
  "type": "<tool_type>",
  "<tool_type>": {
    // Tool-specific configuration
  }
}
```

### 1. File Search Tool

Search documents in vector stores for relevant chunks.

```json
{
  "type": "file_search",
  "vector_store_ids": ["vs_123", "vs_456"],
  "max_num_results": 10,
  "filters": {
    "category": "technical",
    "status": "published"
  },
  "ranking_options": {
    "score_threshold": 0.7,
    "ranker": "default-2024-11-15"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vector_store_ids` | array\<string\> | ✓ | Vector store IDs to search |
| `max_num_results` | integer | - | Max results (1-50, default: 10) |
| `filters` | object | - | Metadata filters |
| `ranking_options` | object | - | Advanced ranking configuration |

### 2. Web Search Tool

Search the web for current information.

```json
{
  "type": "web_search",
  "search_context_size": "medium",
  "user_location": {
    "type": "approximate",
    "city": "San Francisco",
    "country": "US"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `search_context_size` | string | - | "low", "medium", "high" (default: "medium") |
| `user_location` | object | - | User location for localized results |

### 3. List Documents Tool

List documents across vector stores.

```json
{
  "type": "list_documents",
  "vector_store_ids": ["vs_123"],
  "max_num_results": 20,
  "score_threshold": 0.8,
  "deduplicate": true,
  "filters": {
    "document_type": "manual"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vector_store_ids` | array\<string\> | ✓ | Vector stores to search |
| `max_num_results` | integer | - | Max results (1-50, default: 20) |
| `score_threshold` | number | - | Min relevance score (0-1) |
| `deduplicate` | boolean | - | Remove duplicates (default: true) |
| `filters` | object | - | Metadata filters |

### 4. Function Tool

Custom user-defined functions.

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Get current weather for a location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g. San Francisco, CA"
      }
    },
    "required": ["location"]
  }
}
```

## Response Structure

### Response Object

```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1699564800.123,
  "status": "completed",
  "model": "kf-alpha",
  "output": [
    {
      "type": "file_search_call",
      "id": "call_def456",
      "status": "completed",
      "queries": ["refund policy"],
      "results": [
        {
          "file_id": "file_789",
          "filename": "policy.pdf",
          "text": "Our refund policy allows...",
          "score": 0.95,
          "attributes": {
            "segment_index": 42,
            "citation_id": "1"
          }
        }
      ]
    },
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Based on the company documentation¹, the refund policy states...",
          "annotations": [
            {
              "type": "file_citation",
              "file_id": "file_789",
              "index": 42,
              "snippet": "Our refund policy allows..."
            }
          ]
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 150,
    "output_tokens": 200,
    "total_tokens": 350
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique response identifier |
| `object` | string | Always "response" |
| `created_at` | number | Unix timestamp |
| `status` | string | "in_progress", "completed", "failed", "incomplete" |
| `output` | array | Array of output items (tool calls, messages) |
| `usage` | object | Token usage statistics |

### Output Item Types

#### Tool Call Items

1. **File Search Tool Call**

   ```json
   {
     "type": "file_search_call",
     "id": "call_123",
     "status": "completed",
     "queries": ["search terms"],
     "results": [...]
   }
   ```

2. **Web Search Tool Call**

   ```json
   {
     "type": "web_search_call",
     "id": "call_456",
     "status": "completed", 
     "queries": ["search terms"],
     "results": [...]
   }
   ```

3. **Function Tool Call**

   ```json
   {
     "type": "function_call",
     "id": "call_789",
     "name": "get_weather",
     "arguments": "{\"location\": \"San Francisco\"}",
     "status": "completed"
   }
   ```

#### Message Items

```json
{
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "output_text",
      "text": "Response with citations¹",
      "annotations": [...]
    }
  ]
}
```

## Hybrid Streaming Events (混合流式方法)

Knowledge Forge implements a **unique hybrid streaming architecture** that combines the benefits of snapshot-based and delta-based approaches. This is fundamentally different from standard Chat API streaming.

### 🔥 What Makes Knowledge Forge Streaming Special

**Traditional Chat API Streaming** (what most APIs do):

- Pure delta-based: only sends incremental changes
- Client must reconstruct full state from deltas
- Complex state management and potential synchronization issues

**Knowledge Forge Hybrid Streaming** (混合流式方法):

- **Snapshot Events**: Complete Response objects at key lifecycle points
- **Delta Events**: Efficient incremental updates for content streaming
- **Progress Events**: Rich tool execution status without full payloads
- **Best of Both**: Full state snapshots + efficient deltas + detailed progress

### Three Event Categories

When `stream: true`, Knowledge Forge uses **Server-Sent Events (SSE)** with this hybrid approach:

### 📡 SSE Event Structure

All events use standard **Server-Sent Events (SSE)** format:

```
event: <event_type>
data: <json_data>

```

**Key Point**: Unlike Chat API streaming, the `data` field contains different payload types based on the event category (snapshot/delta/progress).

### Event Categories

#### 1. 📸 Snapshot Events (完整状态快照)

**Contains complete Response objects** - Client gets full current state:

- `response.created` - Response initialized with complete Response object
- `response.in_progress` - Response updated with current complete state  
- `response.completed` - Final complete Response object
- `response.failed` - Error Response with complete error details

**Benefit**: Client always has full context, no state reconstruction needed.

#### 2. ⚡ Delta Events (增量更新)

**Efficient incremental updates** for streaming content:

- `response.output_text.delta` - Text content streaming in chunks
- `response.output_text.done` - Text output completed
- `response.function_call_arguments.delta` - Function arguments streaming
- `response.reasoning_summary_text.delta` - Reasoning content streaming

**Benefit**: Real-time content delivery without redundant full payloads.

#### 3. 🔄 Progress Events (工具执行进度)

**Rich tool execution status** without full Response objects:

- `response.file_search_call.in_progress` - File search started
- `response.file_search_call.searching` - File search executing
- `response.file_search_call.completed` - File search finished
- `response.web_search_call.in_progress` - Web search started
- `response.web_search_call.searching` - Web search executing
- `response.web_search_call.completed` - Web search finished
- `response.output_item.added` - New output item added
- `response.output_item.done` - Output item completed

**Benefit**: Detailed progress tracking without overwhelming bandwidth.

### 🎯 Hybrid Advantage

This three-tier approach provides:

- **Reliability**: Full snapshots prevent state drift
- **Efficiency**: Deltas minimize bandwidth for content
- **Visibility**: Progress events give detailed tool execution feedback
- **Simplicity**: Client can choose to only process snapshots for simpler integration

### Event Data Formats

#### 📸 Snapshot Event Example (完整Response对象)

**Notice**: Data contains the **complete Response object** with all current state:

```
event: response.created
data: {
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1699564800.123,
  "status": "in_progress",
  "model": "kf-alpha",
  "output": [],
  "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
  "tools": [...],
  "parallel_tool_calls": true
}

```

**Client Action**: Replace entire Response state with this data.

#### ⚡ Delta Event Example (增量内容)

**Notice**: Data contains only the **incremental change**, not full state:

```
event: response.output_text.delta
data: {
  "item_id": "msg_789",
  "output_index": 1,
  "content_index": 0,
  "delta": "Based on the company documentation"
}

```

**Client Action**: Append `delta` to existing text content at specified indices.

#### 🔄 Progress Event Example (工具状态)

**Notice**: Data contains **status information only**, no Response or content data:

```
event: response.file_search_call.in_progress
data: {
  "item_id": "call_def456",
  "output_index": 0
}

```

**Client Action**: Update UI progress indicators, no content changes needed.

### 🌊 Complete Hybrid Streaming Flow

**This example demonstrates the hybrid approach in action**:

```
event: response.created
data: {"id": "resp_abc123", "status": "in_progress", "output": [], ...}

event: response.file_search_call.in_progress
data: {"item_id": "call_def456", "output_index": 0}

event: response.output_item.added
data: {"item": {"type": "file_search_call", "id": "call_def456", "status": "searching", ...}, "output_index": 0}

event: response.file_search_call.completed
data: {"item_id": "call_def456", "output_index": 0}

event: response.output_item.added
data: {"item": {"type": "message", "role": "assistant", ...}, "output_index": 1}

event: response.output_text.delta
data: {"item_id": "msg_789", "output_index": 1, "content_index": 0, "delta": "Based on the documentation¹, "}

event: response.output_text.delta
data: {"item_id": "msg_789", "output_index": 1, "content_index": 0, "delta": "the refund policy states..."}

event: response.output_text.done
data: {"item_id": "msg_789", "output_index": 1, "content_index": 0}

event: response.completed
data: {"id": "resp_abc123", "status": "completed", "output": [...], "usage": {"input_tokens": 150, "output_tokens": 200, "total_tokens": 350}}

```

## Tool Execution Flow

### Built-in Tools (Auto-Executed)

1. **File Search** - Automatically searches vector stores
2. **Web Search** - Automatically searches the web
3. **List Documents** - Automatically discovers documents

These tools execute within the system and return results in the response.

### External Tools (Client-Executed)

**Function Tools** require client execution:

1. Request includes function tool definition
2. Response contains function call with `status: "in_progress"`
3. Client executes function and provides result
4. New request includes tool result to continue

## Error Handling

### Tool Status Codes

| Tool Type | Success | Partial | Failed |
|-----------|---------|---------|---------|
| `file_search` | `completed` | `incomplete` | `incomplete` |
| `web_search` | `completed` | `incomplete` | `failed` |
| `function` | `completed` | `incomplete` | `incomplete` |

### Error Response

```json
{
  "id": "resp_123",
  "object": "response", 
  "status": "failed",
  "error": {
    "type": "tool_error",
    "message": "File search failed: invalid vector store ID"
  }
}
```

## Complete Example

### Request

```bash
curl -X POST "https://api.knowledge-forge.com/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "kf-alpha",
    "user": "user-123",
    "input": [
      {
        "type": "input_text", 
        "text": "What are the key features of our premium plan?"
      }
    ],
    "tools": [
      {
        "type": "file_search",
        "vector_store_ids": ["vs_product_docs"],
        "max_num_results": 5
      },
      {
        "type": "web_search",
        "search_context_size": "medium"
      }
    ],
    "effort": "high",
    "stream": true
  }'
```

### Response Stream

```
event: response.created
data: {"id": "resp_abc123", "status": "in_progress", "output": [], "model": "kf-alpha", ...}

event: response.file_search_call.in_progress  
data: ...

event: response.output_item.added
data: ...

event: response.file_search_call.completed
data: ...

event: response.output_item.added
data: ...

event: response.output_text.delta
data: ...

event: response.output_text.delta
data: ...

event: response.output_text.done
data: ...

event: response.completed
data: {"id": "resp_abc123", "status": "completed", "output": [...], "usage": {"input_tokens": 245, "output_tokens": 156, "total_tokens": 401}}

```

## Best Practices

### Tool Selection

- Use **file_search** for specific document content
- Use **list_documents** for document discovery
- Use **web_search** for current/external information
- Combine multiple tools for comprehensive answers

### Error Handling

- Check tool call status before using results
- Handle partial results gracefully
- Provide fallback for failed tool calls

### Performance

- Set appropriate `max_num_results` limits
- Use metadata filters to narrow searches
- Consider `effort` level for response quality vs speed

### Citations

- Citations are automatically generated and formatted
- Use Unicode symbols (¹, ², ³) for display
- Citation IDs map to tool call results

---

*Last updated: 2025-06-15*
