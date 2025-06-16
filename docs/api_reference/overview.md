# Knowledge Forge API Documentation

## Overview

Knowledge Forge provides a comprehensive **Response API** for intelligent document processing, semantic search, and AI-powered question answering. The API implements a Response-based architecture (not Chat Completions) with advanced RAG capabilities, tool execution, and streaming support.

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

Knowledge Forge uses a **Response API architecture** distinct from Chat Completions APIs:

### Response vs Chat API

| Aspect | Knowledge Forge Response API | Chat Completions API |
|--------|------------------------------|---------------------|
| **Object Type** | `"response"` | `"chat.completion"` |
| **Request Format** | Single `Request` object | Messages array |
| **Response Format** | `Response` with `output` array | `choices` array |
| **Tool Execution** | Built-in tools auto-execute | External execution required |
| **Streaming** | **Hybrid SSE** (snapshot + delta + progress) | Delta-only streaming |
| **Citations** | Automatic with Unicode formatting | Manual implementation |

### System Architecture

```
┌─────────────────────────────────────────┐
│          Response API Endpoints        │  HTTP/SSE interface
├─────────────────────────────────────────┤
│           Service Layer                 │  Business logic & orchestration
├─────────────────────────────────────────┤
│          Tool System                    │  Auto-executing RAG tools
├─────────────────────────────────────────┤
│       Vector Stores & Processing       │  Embeddings & search
├─────────────────────────────────────────┤
│        Storage & Data Persistence      │  Documents & responses
└─────────────────────────────────────────┘
```

## Core Features

### 1. Response Generation (`/v1/responses`)

- Main AI response endpoint with RAG capabilities
- Built-in tool execution (file search, web search, document finder)
- Server-Sent Events (SSE) streaming with rich event types
- Automatic citation management with Unicode formatting
- Multi-effort levels (low, medium, high, dev)

### 2. Document Management (`/v1/files`)

- Multi-format file upload and processing
- Background processing with progress tracking
- Rich content extraction (text, images, tables)
- Automatic chunking and embedding generation

### 3. Vector Store Operations (`/v1/vector_stores`)

- FAISS-based vector collections
- Semantic search with metadata filtering
- Document clustering and organization
- Collection-level statistics and management

### 4. Task Management (`/v1/tasks`)

- Background job tracking and monitoring
- Progress reporting for long-running operations
- Status updates for file processing and vectorization

### 5. Server Status (`/v1/serverstatus`)

- Health checks and system status
- Service availability monitoring

## Data Flow

1. **Document Upload** → Files processed and chunked
2. **Vector Store Creation** → Documents embedded and indexed
3. **Response Generation** → Tools execute automatically, citations generated
4. **Streaming Response** → Real-time updates via SSE events

## Key Differentiators

### Built-in Tool Execution

Unlike Chat APIs that require external tool execution, Knowledge Forge tools execute within the system:

- **File Search**: Automatic vector store queries
- **Web Search**: Live web search integration  
- **List Documents**: Intelligent document discovery

### Advanced Citation System

Automatic citation management with:

- Unicode citation markers (¹, ², ³)
- Source tracking and attribution
- Annotation-based reference linking

### Hybrid Streaming Method (混合流式方法)

**Knowledge Forge's unique streaming architecture**:

- **Snapshot Events**: Complete Response objects at key points
- **Delta Events**: Efficient incremental content updates
- **Progress Events**: Rich tool execution status
- **Best of Both Worlds**: Full state reliability + efficient streaming

## Request Patterns

### Standard Response Request

```json
{
  "user": "user-123",
  "input": [{"type": "input_text", "text": "Query here"}],
  "tools": [{"type": "file_search", "vector_store_ids": ["vs_123"]}],
  "effort": "high",
  "stream": true
}
```

### File Upload

```json
{
  "file": "<binary>",
  "purpose": "qa",
  "parse_options": {"abstract": "enable"}
}
```

### Vector Store Creation

```json
{
  "name": "Document Collection",
  "description": "Project documents",
  "file_ids": ["file_123", "file_456"]
}
```

## Response Patterns

### Hybrid Streaming Response (混合流式响应)

```
# 📸 SNAPSHOT: Full Response state
event: response.created
data: {"id": "resp_123", "status": "in_progress", "output": [], ...}

# 🔄 PROGRESS: Tool execution status
event: response.file_search_call.in_progress
data: {"item_id": "call_456", "output_index": 0}

# ⚡ DELTA: Incremental content
event: response.output_text.delta
data: {"delta": "Based on the documents¹, ..."}

# 📸 SNAPSHOT: Complete final state
event: response.completed
data: {"id": "resp_123", "status": "completed", "output": [...], "usage": {...}}
```

**Why This Matters**: Unlike Chat APIs that only send deltas, Knowledge Forge provides complete state snapshots, making client integration more robust and state management simpler.

### Standard JSON Response

```json
{
  "id": "resp_123",
  "object": "response",
  "status": "completed",
  "output": [...],
  "usage": {"total_tokens": 150}
}
```

## Error Handling

All APIs return consistent error formats:

```json
{
  "code": 1,
  "message": "Error description",
  "detail": {"type": "validation_error", "field": "input"}
}
```

## Rate Limiting

- File uploads: 100 requests/hour
- Response generation: 1000 requests/hour  
- Vector operations: 500 requests/hour

## SDKs and Integration

The Response API is designed for easy integration:

- RESTful HTTP interface
- **Hybrid SSE streaming** for robust real-time updates
- OpenAPI 3.0 specification
- Pydantic data models
- **Flexible streaming**: Use snapshots-only for simple integration, or full hybrid approach for rich UX

---

For detailed endpoint documentation, see the individual API reference pages.
