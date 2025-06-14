# Knowledge Forge API Documentation

## Overview

Knowledge Forge provides a comprehensive RESTful API for intelligent document processing, semantic search, and AI-powered question answering. The API is built with FastAPI and follows OpenAI-compatible formats where applicable, making it easy to integrate with existing applications.

## Base URL

```
http://localhost:10000  # Local development
```

## Authentication

Currently uses header-based authentication:
```
Authorization: Bearer <your-api-token>
```

## API Architecture

Knowledge Forge follows a layered architecture:

```
┌─────────────────────────────────────────┐
│              FastAPI APIs               │  HTTP endpoints
├─────────────────────────────────────────┤
│            Service Layer                │  Business logic
├─────────────────────────────────────────┤
│        Tools & Processing              │  RAG pipeline
├─────────────────────────────────────────┤
│      Storage & Vector Stores          │  Data persistence
└─────────────────────────────────────────┘
```

## Core API Endpoints

### 1. Response Generation API

**Endpoint:** `POST /v1/responses`

The main AI response generation endpoint with RAG capabilities, streaming support, and tool execution.

#### Request Format

```json
{
  "user": "user-123",
  "input": [
    {
      "type": "input_text", 
      "text": "What is the refund policy in our documents?"
    }
  ],
  "tools": [
    {
      "type": "file_search",
      "file_search": {
        "vector_store_ids": ["vs_abc123"],
        "max_num_results": 10
      }
    },
    {
      "type": "web_search",
      "web_search": {
        "max_results": 5
      }
    }
  ],
  "effort": "high",
  "stream": true,
  "store": true,
  "previous_response_id": "resp_xyz789"
}
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user` | string | Yes | User identifier for request tracking |
| `input` | array | Yes | Input messages (text, files, images) |
| `tools` | array | No | Available tools for the response |
| `effort` | string | No | Response quality level: `low`, `medium`, `high`, `dev` |
| `stream` | boolean | No | Enable Server-Sent Events streaming |
| `store` | boolean | No | Save response for conversation history |
| `previous_response_id` | string | No | Continue conversation from previous response |

#### Supported Tools

| Tool Type | Description | Configuration |
|-----------|-------------|---------------|
| `file_search` | Search within vector stores | `vector_store_ids`, `max_num_results` |
| `web_search` | Search the web for information | `max_results`, `search_context_size` |
| `document_finder` | Advanced document discovery | `vector_store_ids`, `filters` |

#### Response Format (Streaming)

The API returns Server-Sent Events (SSE) for real-time streaming:

```
data: {"type": "response.created", "response": {"id": "resp_abc123"}}

data: {"type": "response.output_text.delta", "delta": {"text": "Based on"}}

data: {"type": "response.file_search.in_progress", "tool_call_id": "call_123"}

data: {"type": "response.file_search.completed", "tool_call_id": "call_123", "results": [...]}

data: {"type": "response.output_text.delta", "delta": {"text": " the documents¹"}}

data: {"type": "response.completed", "response": {"usage": {"total_tokens": 150}}}
```

#### Event Types

| Event Type | Description |
|------------|-------------|
| `response.created` | Response generation started |
| `response.output_text.delta` | Incremental text output |
| `response.file_search.in_progress` | File search in progress |
| `response.file_search.completed` | File search completed |
| `response.web_search.in_progress` | Web search in progress |
| `response.web_search.completed` | Web search completed |
| `response.completed` | Response generation finished |

#### Effort Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `low` | Basic tool execution | Quick responses, simple queries |
| `medium` | Enhanced reasoning | Better quality, moderate complexity |
| `high` | Full RAG pipeline | Best quality, complex analysis |
| `dev` | Prompt chaining | Non-tool-calling LLM compatibility |

#### Example Usage

```bash
curl -X POST "http://localhost:10000/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "user": "user-123",
    "input": [{"type": "input_text", "text": "Explain our refund policy"}],
    "tools": [{"type": "file_search", "file_search": {"vector_store_ids": ["vs_123"]}}],
    "effort": "high",
    "stream": true
  }'
```

### 2. File Management API

**Base Path:** `/v1/files`

Handles file upload, processing, and management with support for multiple formats and background processing.

#### Upload File

**Endpoint:** `POST /v1/files`

```bash
curl -X POST "http://localhost:10000/v1/files" \
  -F "file=@document.pdf" \
  -F "purpose=qa" \
  -F "parse_options={\"abstract\": \"enable\", \"keywords\": \"enable\"}"
```

**Form Data Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | No* | File to upload (max 512MB) |
| `url` | string | No* | URL to download file from |
| `name` | string | No** | File name (required with URL) |
| `file_type` | string | No** | MIME type (required with URL) |
| `purpose` | string | No | Purpose: `qa`, `general` |
| `id` | string | No | Custom UUID for the file |
| `md5` | string | No | MD5 hash for deduplication |
| `parse_options` | string | No | JSON parsing configuration |
| `skip_exists` | boolean | No | Skip if file already exists |

*Either `file` or `url` must be provided
**Required when using `url`

**Parse Options:**
```json
{
  "abstract": "enable|disable",
  "summary": "enable|disable", 
  "outline": "enable|disable",
  "keywords": "enable|disable",
  "contexts": "enable|disable",
  "graph": "enable|disable"
}
```

**Response:**
```json
{
  "id": "file_abc123",
  "object": "file",
  "bytes": 1024000,
  "created_at": 1699061776,
  "filename": "document.pdf",
  "purpose": "qa",
  "task_id": "task_xyz789"
}
```

#### Get File Content

**Endpoint:** `GET /v1/files/{file_id}/content`

```bash
curl "http://localhost:10000/v1/files/file_abc123/content"
```

**Response:**
```json
{
  "id": "file_abc123",
  "title": "Document Title",
  "content": {
    "pages": [...],
    "summary": "Document summary",
    "keywords": ["keyword1", "keyword2"]
  },
  "metadata": {
    "author": "John Doe",
    "created_date": "2023-01-01"
  }
}
```

#### Delete File

**Endpoint:** `DELETE /v1/files/{file_id}`

```bash
curl -X DELETE "http://localhost:10000/v1/files/file_abc123"
```

**Response:**
```json
{
  "id": "file_abc123",
  "object": "file",
  "deleted": true
}
```

### 3. Vector Store API

**Base Path:** `/v1/vector_stores`

Manages vector collections for semantic search and document clustering.

#### Create Vector Store

**Endpoint:** `POST /v1/vector_stores`

```json
{
  "id": "vs_custom_id",
  "name": "Support Documents", 
  "description": "Customer support FAQ and policies",
  "file_ids": ["file_123", "file_456"],
  "metadata": {
    "project": "customer_support",
    "version": "1.0"
  }
}
```

**Response:**
```json
{
  "id": "vs_custom_id",
  "object": "vector_store",
  "created_at": 1699061776,
  "name": "Support Documents",
  "description": "Customer support FAQ and policies", 
  "bytes": null,
  "file_counts": {
    "in_progress": 2,
    "completed": 0,
    "failed": 0,
    "cancelled": 0,
    "total": 2
  },
  "task_id": "create-vs_custom_id"
}
```

#### Search Vector Store

**Endpoint:** `POST /v1/vector_stores/{vector_store_id}/search`

```json
{
  "query": "What is the return policy?",
  "top_k": 10,
  "filters": {
    "document_type": "policy"
  }
}
```

**Response:**
```json
{
  "object": "vector_store.search_results.page",
  "search_query": "What is the return policy?",
  "data": [
    {
      "file_id": "file_123",
      "filename": "policies.pdf",
      "score": 0.95,
      "attributes": {
        "section": "returns",
        "page": 5
      },
      "content": [
        {
          "type": "text",
          "text": "Our return policy allows..."
        }
      ]
    }
  ],
  "has_more": false,
  "next_page": null
}
```

#### Modify Vector Store

**Endpoint:** `POST /v1/vector_stores/{vector_store_id}`

```json
{
  "name": "Updated Support Documents",
  "description": "Updated customer support documentation",
  "join_file_ids": ["file_789"],
  "left_file_ids": ["file_123"]
}
```

#### Delete Vector Store

**Endpoint:** `DELETE /v1/vector_stores/{vector_store_id}`

```json
{
  "id": "vs_abc123",
  "object": "vector_store.deleted",
  "deleted": true,
  "task_id": "delete-vs_abc123"
}
```

#### Get Vector Store Summary

**Endpoint:** `GET /v1/vector_stores/{vector_store_id}/summary?model=qwen-max&max_tokens=1000`

Generates an AI-powered summary of all documents in the vector store.

**Response:**
```json
{
  "object": "vector_store.summary",
  "vector_store_id": "vs_abc123",
  "summary": "This collection contains customer support documents covering...",
  "model": "qwen-max",
  "token_count": 156
}
```

### 4. Document Finder API

**Base Path:** `/v1/doc`

Advanced document discovery with query understanding and multi-strategy retrieval.

#### Find Documents

**Endpoint:** `POST /v1/doc/find`

```json
{
  "queries": [
    "refund policy",
    "return procedure"
  ],
  "vector_store_ids": ["vs_123", "vs_456"],
  "top_k": 5,
  "filter": {
    "document_type": "policy"
  }
}
```

**Response:**
```json
{
  "object": "doc.finder_results",
  "candidates": [
    {
      "document_id": "doc_123",
      "title": "Refund and Return Policy",
      "content": "Complete text snippet with relevant information...",
      "score": 0.92,
      "metadata": {
        "file_id": "file_123",
        "title": "Refund and Return Policy",
        "collection_name": "support_docs",
        "other_metadata": {
          "author": "Legal Team",
          "last_updated": "2023-01-01"
        }
      }
    }
  ]
}
```

### 5. Task Management API

**Base Path:** `/v1/tasks`

Track background task progress for file processing and vector store operations.

#### Get Task Status

**Endpoint:** `GET /v1/tasks/{task_id}`

```bash
curl "http://localhost:10000/v1/tasks/task_abc123"
```

**Response:**
```json
{
  "id": "task_abc123",
  "status": "completed",
  "progress": 1.0,
  "data": {
    "operation": "file_processing",
    "file_id": "file_123",
    "chunks_created": 45
  },
  "created_at": 1699061776,
  "updated_at": 1699061876,
  "failure_reason": null
}
```

**Task Status Values:**
- `pending` - Task queued but not started
- `in_progress` - Task currently running
- `completed` - Task finished successfully  
- `failed` - Task failed with error

### 6. Server Status API

**Base Path:** `/v1/serverstatus`

Health checks and server information.

**Endpoint:** `GET /v1/serverstatus`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1699061776,
  "services": {
    "database": "connected",
    "vector_store": "operational",
    "llm": "available"
  }
}
```

## Data Models

### Core Types

#### Input Message Types

```json
// Text input
{
  "type": "input_text",
  "text": "Your question here"
}

// File input
{
  "type": "input_file", 
  "file": {
    "id": "file_123",
    "content": [/* chunk objects */]
  }
}

// Image input
{
  "type": "input_image",
  "image": {
    "url": "https://example.com/image.jpg"
  }
}
```

#### Tool Definitions

```json
// File search tool
{
  "type": "file_search",
  "file_search": {
    "vector_store_ids": ["vs_123"],
    "max_num_results": 10,
    "filters": {"key": "value"}
  }
}

// Web search tool  
{
  "type": "web_search",
  "web_search": {
    "max_results": 5,
    "search_context_size": "medium"
  }
}

// Document finder tool
{
  "type": "document_finder",
  "document_finder": {
    "vector_store_ids": ["vs_123"],
    "max_num_results": 5,
    "filters": {"key": "value"}
  }
}
```

#### Response Structure

```json
{
  "id": "resp_123",
  "object": "response",
  "created_at": 1699061776,
  "status": "completed",
  "output": [
    {
      "type": "text",
      "text": "Based on the documents¹, our refund policy..."
    }
  ],
  "tool_calls": [
    {
      "id": "call_123",
      "type": "file_search",
      "status": "completed",
      "results": [...]
    }
  ],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 200,
    "total_tokens": 300
  }
}
```

## Client Libraries

### Python SDK Example

```python
import requests
import json

class KnowledgeForgeClient:
    def __init__(self, base_url="http://localhost:10000", api_key=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    def ask(self, question, vector_store_ids=None, effort="high", stream=False):
        """Ask a question with optional vector store search"""
        payload = {
            "user": "user-123",
            "input": [{"type": "input_text", "text": question}],
            "effort": effort,
            "stream": stream
        }
        
        if vector_store_ids:
            payload["tools"] = [{
                "type": "file_search",
                "file_search": {"vector_store_ids": vector_store_ids}
            }]
        
        if stream:
            return self._stream_request(payload)
        else:
            response = requests.post(
                f"{self.base_url}/v1/responses",
                json=payload,
                headers=self.headers
            )
            return response.json()
    
    def upload_file(self, file_path, purpose="qa"):
        """Upload a file for processing"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'purpose': purpose}
            response = requests.post(
                f"{self.base_url}/v1/files",
                files=files,
                data=data,
                headers=self.headers
            )
            return response.json()
    
    def create_vector_store(self, name, description, file_ids=None):
        """Create a new vector store"""
        payload = {
            "name": name,
            "description": description,
            "file_ids": file_ids or []
        }
        response = requests.post(
            f"{self.base_url}/v1/vector_stores",
            json=payload,
            headers=self.headers
        )
        return response.json()

# Usage example
client = KnowledgeForgeClient(api_key="your-token")

# Upload a document
file_result = client.upload_file("document.pdf")

# Create vector store
vs_result = client.create_vector_store(
    name="My Documents",
    description="Personal document collection",
    file_ids=[file_result["id"]]
)

# Ask a question
answer = client.ask(
    "What is mentioned about refunds?",
    vector_store_ids=[vs_result["id"]]
)
```

### JavaScript SDK Example

```javascript
class KnowledgeForgeClient {
    constructor(baseUrl = "http://localhost:10000", apiKey = null) {
        this.baseUrl = baseUrl;
        this.headers = apiKey ? {"Authorization": `Bearer ${apiKey}`} : {};
    }
    
    async ask(question, vectorStoreIds = null, effort = "high", stream = false) {
        const payload = {
            user: "user-123",
            input: [{type: "input_text", text: question}],
            effort: effort,
            stream: stream
        };
        
        if (vectorStoreIds) {
            payload.tools = [{
                type: "file_search",
                file_search: {vector_store_ids: vectorStoreIds}
            }];
        }
        
        if (stream) {
            return this.streamRequest(payload);
        } else {
            const response = await fetch(`${this.baseUrl}/v1/responses`, {
                method: "POST",
                headers: {...this.headers, "Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            return response.json();
        }
    }
    
    async uploadFile(file, purpose = "qa") {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("purpose", purpose);
        
        const response = await fetch(`${this.baseUrl}/v1/files`, {
            method: "POST",
            headers: this.headers,
            body: formData
        });
        return response.json();
    }
    
    async streamRequest(payload) {
        const response = await fetch(`${this.baseUrl}/v1/responses`, {
            method: "POST",
            headers: {
                ...this.headers,
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            body: JSON.stringify(payload)
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        return {
            async *[Symbol.asyncIterator]() {
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data.trim()) {
                                yield JSON.parse(data);
                            }
                        }
                    }
                }
            }
        };
    }
}

// Usage example
const client = new KnowledgeForgeClient("http://localhost:10000", "your-token");

// Upload and ask with streaming
const fileInput = document.getElementById('file-input');
const result = await client.uploadFile(fileInput.files[0]);

const stream = await client.ask("Explain the main points", [result.id], "high", true);
for await (const event of stream) {
    console.log("Received:", event);
}
```

## Error Handling

### Error Response Format

All errors follow a consistent structure:

```json
{
  "detail": "Error description",
  "type": "error_type",
  "code": 400
}
```

### Common HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Invalid input, missing required fields |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource doesn't exist |
| 413 | Payload Too Large | File exceeds 512MB limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side processing error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Handling Best Practices

```python
try:
    response = client.ask("Your question")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Bad request:", e.response.json()["detail"])
    elif e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 500:
        print("Server error, please try again")
    else:
        print(f"Unexpected error: {e}")
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Rate Limits:** 100 requests per minute per user
- **Headers:** Rate limit information in response headers
- **Retry:** Implement exponential backoff for retry logic

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699061776
```

## Performance Optimization

### Response Streaming

Use streaming for long-running operations:

```python
# Enable streaming for real-time updates
response = client.ask("Complex question", stream=True)
for event in response:
    if event["type"] == "response.output_text.delta":
        print(event["delta"]["text"], end="")
```

### Batch Operations

Process multiple files efficiently:

```python
# Upload multiple files
file_ids = []
for file_path in file_paths:
    result = client.upload_file(file_path)
    file_ids.append(result["id"])

# Create vector store with all files
vector_store = client.create_vector_store(
    name="Batch Upload",
    description="Multiple files processed together",
    file_ids=file_ids
)
```

### Caching Strategy

- **Document caching:** Frequently accessed documents are cached
- **Vector caching:** Embedding results cached for deduplication
- **LLM response caching:** Similar queries may return cached responses

## Security Considerations

### Input Validation
- All inputs validated using Pydantic models
- File type and size restrictions enforced
- SQL injection prevention through parameterized queries

### File Safety
- Virus scanning for uploaded files
- Sandboxed file processing
- Content-based file type detection

### Data Privacy
- User data isolation
- Conversation history encryption
- Configurable data retention policies

## Migration and Versioning

### API Versioning
- Current version: `v1`
- Breaking changes introduce new version
- Backward compatibility maintained for one major version

### Migration Guide
When upgrading to newer versions:

1. Check API changelog for breaking changes
2. Update client libraries to compatible versions
3. Test against new endpoints before full migration
4. Monitor deprecated endpoint warnings

## Monitoring and Debugging

### Request Tracing
Enable request tracing for debugging:

```bash
curl -X POST "http://localhost:10000/v1/responses" \
  -H "X-Trace-Id: unique-trace-id" \
  -H "X-Debug: true" \
  ...
```

### Health Checks
Monitor service health:

```bash
# Quick health check
curl "http://localhost:10000/v1/serverstatus"

# Detailed service status
curl "http://localhost:10000/v1/serverstatus?detailed=true"
```

### Logging
- Structured JSON logging
- Request/response correlation IDs
- Performance metrics included
- Error stack traces for debugging

## Frequently Asked Questions

### Q: How do I handle large files?
A: Files up to 512MB are supported. For larger files, consider splitting them or using the URL upload method with cloud storage.

### Q: Can I customize the embedding model?
A: Yes, configure the embedding model through environment variables. See the embedding configuration documentation.

### Q: How do I improve response quality?
A: Use higher effort levels (`high` vs `low`), provide more specific queries, and ensure your vector stores contain relevant documents.

### Q: What file formats are supported?
A: PDF, DOCX, TXT, MD, HTML, and common image formats. The system automatically detects file types.

### Q: How do I implement conversation history?
A: Use the `previous_response_id` field in requests to continue conversations, and set `store: true` to save responses.

### Q: Can I use custom tools?
A: The current version supports built-in tools (file_search, web_search, document_finder). Custom tool support is planned for future releases.

### Q: How do I optimize for speed?
A: Use `low` effort level for faster responses, enable streaming, and pre-index documents in vector stores.

### Q: What about multilingual support?
A: The system supports multiple languages depending on the configured embedding model and LLM. Text processing is generally language-agnostic.

## Support and Resources

- **Documentation:** Complete API reference and guides
- **GitHub Issues:** Bug reports and feature requests
- **Community:** Developer forums and discussions
- **Professional Support:** Enterprise support packages available

---

For the most up-to-date API documentation and examples, please refer to the interactive OpenAPI documentation available at `/docs` when running the server.