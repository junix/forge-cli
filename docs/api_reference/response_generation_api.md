# Response Generation API

**Endpoint:** `POST /v1/responses`

The core Knowledge Forge endpoint for AI-powered response generation with built-in RAG capabilities, tool execution, and streaming support.

## Request Format

Knowledge Forge uses a **Response API** format (not Chat Completions):

```json
{
  "model": "kf-alpha",
  "user": "user-123",
  "input": [
    {
      "type": "input_text",
      "text": "What is our refund policy?"
    }
  ],
  "tools": [
    {
      "type": "file_search",
      "vector_store_ids": ["vs_abc123"],
      "max_num_results": 10
    }
  ],
  "effort": "high",
  "stream": true,
  "store": true
}
```

## Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | No | Model ID (default: "kf-alpha") |
| `user` | string | Yes | User identifier for request tracking |
| `input` | string \| array | Yes | Input text or array of input items |
| `tools` | array | No | Available tools for the response |
| `effort` | string | No | Response quality: `low`, `medium`, `high`, `dev` |
| `stream` | boolean | No | Enable SSE streaming (default: false) |
| `store` | boolean | No | Save response for history (default: true) |
| `instructions` | string | No | System instructions |
| `temperature` | number | No | Sampling temperature (0-2) |
| `max_output_tokens` | integer | No | Maximum tokens to generate |
| `previous_response_id` | string | No | Continue from previous response |

## Input Types

### Text Input

```json
{
  "type": "input_text",
  "text": "Your question here"
}
```

### File Input

```json
{
  "type": "input_file",
  "file_id": "file_123"
}
```

### Image Input

```json
{
  "type": "input_image",
  "image_url": "data:image/jpeg;base64,..."
}
```

## Built-in Tools

Knowledge Forge tools execute automatically within the system:

### File Search Tool

```json
{
  "type": "file_search",
  "vector_store_ids": ["vs_123"],
  "max_num_results": 10,
  "filters": {"category": "policy"},
  "ranking_options": {
    "score_threshold": 0.7,
    "ranker": "default-2024-11-15"
  }
}
```

### Web Search Tool

```json
{
  "type": "web_search",
  "search_context_size": "medium",
  "user_location": {
    "type": "approximate",
    "city": "San Francisco"
  }
}
```

### List Documents Tool

```json
{
  "type": "list_documents",
  "vector_store_ids": ["vs_123"],
  "max_num_results": 20,
  "score_threshold": 0.8,
  "deduplicate": true
}
```

## Response Format

### Non-Streaming Response

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
          "text": "Based on the company documentation¹, our refund policy states...",
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
  },
  "tools": [...],
  "parallel_tool_calls": true
}
```

## Hybrid Streaming Events (混合流式方法)

Knowledge Forge's streaming is **fundamentally different** from standard Chat API streaming.

### 🔥 Why Knowledge Forge Streaming is Special

**Standard Chat Streaming** (OpenAI, Anthropic, etc.):

```
data: {"choices": [{"delta": {"content": "Hello"}}]}
data: {"choices": [{"delta": {"content": " world"}}]}
data: {"choices": [{"delta": {"content": "!"}}]}
```

- Pure delta-based approach
- Client must reconstruct full message from deltas
- No intermediate state snapshots
- Limited progress visibility

**Knowledge Forge Hybrid Streaming** (混合流式方法):

```
# Snapshot: Full state
data: {"id": "resp_123", "status": "in_progress", "output": [...]} 

# Progress: Tool status  
data: {"item_id": "call_456", "output_index": 0}

# Delta: Content chunk
data: {"delta": "Hello world!", "output_index": 1}

# Snapshot: Complete final state
data: {"id": "resp_123", "status": "completed", "output": [...], "usage": {...}}
```

### Three-Tier Event Architecture

When `stream: true`, responses use **Server-Sent Events (SSE)** with this hybrid approach:

#### 1. 📸 **Snapshot Events** (完整状态快照)

- Complete Response objects at major lifecycle points
- Client gets full current state, no reconstruction needed
- **Events**: `response.created`, `response.in_progress`, `response.completed`, `response.failed`

#### 2. ⚡ **Delta Events** (增量更新)

- Incremental content updates for efficient streaming  
- Real-time text delivery without redundant payloads
- **Events**: `response.output_text.delta`, `response.function_call_arguments.delta`

#### 3. 🔄 **Progress Events** (工具执行进度)

- Tool execution status without full Response payloads
- Rich progress tracking with minimal bandwidth
- **Events**: `response.file_search_call.in_progress`, `response.web_search_call.searching`

### 🌊 Complete Hybrid Streaming Flow

**This shows how the three event types work together**:

```
# 📸 SNAPSHOT: Response created with full initial state
event: response.created
data: {
  "id": "resp_abc123", 
  "object": "response",
  "status": "in_progress", 
  "model": "kf-alpha",
  "output": [],
  "usage": {"input_tokens": 50, "output_tokens": 0, "total_tokens": 50}
}

# 🔄 PROGRESS: Tool execution started (no full Response)
event: response.file_search_call.in_progress
data: {"item_id": "call_def456", "output_index": 0}

# 🔄 PROGRESS: New output item added 
event: response.output_item.added
data: {
  "item": {
    "type": "file_search_call",
    "id": "call_def456", 
    "status": "searching",
    "queries": ["refund policy"]
  }, 
  "output_index": 0
}

# 🔄 PROGRESS: Tool execution completed
event: response.file_search_call.completed
data: {"item_id": "call_def456", "output_index": 0}

# 🔄 PROGRESS: Assistant message added
event: response.output_item.added
data: {
  "item": {
    "type": "message",
    "role": "assistant",
    "content": []
  },
  "output_index": 1
}

# ⚡ DELTA: Text content streaming starts
event: response.output_text.delta
data: {
  "item_id": "msg_789",
  "output_index": 1, 
  "content_index": 0,
  "delta": "Based on the documentation¹, "
}

# ⚡ DELTA: More text content
event: response.output_text.delta  
data: {
  "item_id": "msg_789",
  "output_index": 1,
  "content_index": 0, 
  "delta": "our refund policy states..."
}

# ⚡ DELTA: Text streaming completed
event: response.output_text.done
data: {
  "item_id": "msg_789",
  "output_index": 1,
  "content_index": 0
}

# 📸 SNAPSHOT: Final complete Response with all results
event: response.completed
data: {
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "output": [
    {
      "type": "file_search_call",
      "id": "call_def456",
      "status": "completed", 
      "results": [...]
    },
    {
      "type": "message",
      "role": "assistant",
      "content": [...]
    }
  ],
  "usage": {"input_tokens": 50, "output_tokens": 123, "total_tokens": 173}
}
```

### 🎯 Hybrid Benefits for Developers

1. **Robust State Management**: Snapshots provide authoritative state
2. **Efficient Bandwidth**: Deltas minimize redundant data
3. **Rich Progress**: Progress events give detailed tool feedback
4. **Flexible Integration**: Use only snapshots for simple clients, or all events for rich UX
5. **Error Recovery**: Always have complete state from latest snapshot

## 📡 Complete Event Reference

### 📸 Snapshot Events (完整Response状态)

**Data**: Complete Response object with full current state

- `response.created` - Response initialized with full Response object
- `response.in_progress` - Response updated with current complete state
- `response.completed` - Final complete Response object  
- `response.failed` - Error Response with complete error details

### ⚡ Delta Events (增量内容更新)

**Data**: Incremental content changes only

- `response.output_text.delta` - Text content streaming in chunks
- `response.output_text.done` - Text output completed
- `response.function_call_arguments.delta` - Function arguments streaming
- `response.reasoning_summary_text.delta` - Reasoning content streaming

### 🔄 Progress Events (工具执行进度)

**Data**: Status information without full Response payloads

- `response.file_search_call.in_progress` - File search started
- `response.file_search_call.searching` - File search executing  
- `response.file_search_call.completed` - File search finished
- `response.web_search_call.in_progress` - Web search started
- `response.web_search_call.searching` - Web search executing
- `response.web_search_call.completed` - Web search finished
- `response.output_item.added` - New output item added
- `response.output_item.done` - Output item completed

## Effort Levels

| Level | Description | Tool Usage | Response Quality |
|-------|-------------|------------|------------------|
| `low` | Basic execution | Single tool calls | Fast, basic responses |
| `medium` | Enhanced reasoning | Multiple tools | Balanced quality/speed |
| `high` | Full RAG pipeline | All available tools | Best quality, comprehensive |
| `dev` | Prompt chaining | Non-tool-calling LLMs | Development/testing |

## Error Handling

### Error Response Format

```json
{
  "id": "resp_123",
  "object": "response",
  "status": "failed",
  "error": {
    "type": "tool_error",
    "message": "File search failed: invalid vector store ID",
    "code": "invalid_vector_store"
  },
  "output": [],
  "usage": {"input_tokens": 50, "output_tokens": 0, "total_tokens": 50}
}
```

### Tool Status Codes

| Tool Type | Success | Partial | Failed |
|-----------|---------|---------|---------|
| `file_search` | `completed` | `incomplete` | `incomplete` |
| `web_search` | `completed` | `incomplete` | `failed` |
| `list_documents` | `completed` | `incomplete` | `incomplete` |

## Citations

Knowledge Forge automatically generates citations with Unicode formatting:

### Citation Display

- `¹` `²` `³` - First 3 citations
- `⁴` `⁵` `⁶` - Citations 4-6
- `⁽⁷⁾` `⁽⁸⁾` - Citations 7+

### Citation Objects

```json
{
  "type": "file_citation",
  "file_id": "file_789",
  "index": 42,
  "snippet": "Our refund policy allows...",
  "filename": "policy.pdf"
}
```

## Usage Examples

### Basic Query

```bash
curl -X POST "http://localhost:10000/v1/responses" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user-123",
    "input": [{"type": "input_text", "text": "What is our return policy?"}],
    "tools": [{"type": "file_search", "vector_store_ids": ["vs_policies"]}],
    "effort": "medium"
  }'
```

### Streaming Query

```bash
curl -X POST "http://localhost:10000/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "user": "user-123",
    "input": [{"type": "input_text", "text": "Analyze market trends"}],
    "tools": [
      {"type": "file_search", "vector_store_ids": ["vs_reports"]},
      {"type": "web_search", "search_context_size": "high"}
    ],
    "effort": "high",
    "stream": true
  }'
```

### Multi-turn Conversation

```bash
curl -X POST "http://localhost:10000/v1/responses" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user-123",
    "input": [{"type": "input_text", "text": "Can you elaborate on that policy?"}],
    "previous_response_id": "resp_abc123",
    "effort": "medium"
  }'
```

## Best Practices

### 🔄 Streaming Integration Strategies

**Simple Integration** (Snapshot-only):

```javascript
eventSource.addEventListener('response.completed', (event) => {
  const response = JSON.parse(event.data);
  displayFullResponse(response); // Complete state, no reconstruction
});
```

**Rich Integration** (Full hybrid approach):

```javascript
// Track complete state from snapshots
eventSource.addEventListener('response.created', (event) => {
  currentResponse = JSON.parse(event.data);
});

// Stream content from deltas
eventSource.addEventListener('response.output_text.delta', (event) => {
  const {delta, output_index, content_index} = JSON.parse(event.data);
  appendTextDelta(delta, output_index, content_index);
});

// Show progress from progress events  
eventSource.addEventListener('response.file_search_call.in_progress', (event) => {
  showToolProgress('Searching documents...');
});
```

### Tool Selection

- Use `file_search` for specific document content
- Use `list_documents` for document discovery
- Use `web_search` for current/external information
- Combine multiple tools for comprehensive answers

### Performance Optimization

- Set appropriate `max_num_results` limits
- Use metadata filters to narrow searches
- Choose effort level based on requirements
- Enable streaming for better user experience
- Process progress events for responsive UI feedback

### Error Handling

- Check response `status` field
- Handle tool call failures gracefully
- Provide fallback for failed operations
- Monitor task progress for long operations
- Use snapshot events for authoritative error state

---

### 🔥 Summary: Why Knowledge Forge Streaming Matters

Knowledge Forge's **hybrid streaming method** (混合流式方法) represents a significant advancement over traditional Chat API streaming:

- **More Reliable**: Full state snapshots prevent synchronization issues
- **More Efficient**: Targeted deltas and progress events optimize bandwidth
- **More Informative**: Rich tool execution visibility
- **More Flexible**: Clients can choose their integration complexity level

This approach enables building more robust, responsive, and user-friendly applications with Knowledge Forge.

---

*For complete API reference, see [Tools Integration API](./tools_integration_api.md)*
