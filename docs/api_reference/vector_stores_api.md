# Vector Store API

**Base Path:** `/v1/vector_stores`

Manages vector stores (collections) for semantic search, document clustering, and retrieval-augmented generation (RAG).

## The Vector Store Object

A Vector Store is a container for your files and their associated text embeddings. When you create a vector store, the uploaded files are processed, chunked, and converted into vector embeddings, which allows for efficient semantic search.

```json
{
  "id": "vs_abc123",
  "object": "vector_store",
  "created_at": 1699061776,
  "name": "Support Documents",
  "description": "Customer support FAQ and policies",
  "bytes": 139920,
  "file_counts": {
    "in_progress": 0,
    "completed": 5,
    "failed": 0,
    "cancelled": 0,
    "total": 5
  },
  "task_id": "vectorize-vs_abc123"
}
```

### Attributes

- `id` (string): Unique identifier for the vector store.
- `object` (string): The type of object, always `"vector_store"`.
- `created_at` (integer): The Unix timestamp (in seconds) for when the vector store was created.
- `name` (string, optional): The name of the vector store.
- `description` (string, optional): The description of the vector store.
- `bytes` (integer, optional): The total size in bytes of all files in the vector store.
- `file_counts` (object): An object detailing the processing status of files in the store.
- `task_id` (string, optional): The ID of the last task associated with this vector store (e.g., creation, modification). See the [Tasks API](./tasks_api.md) for details on how to monitor task progress.

## Create Vector Store

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

## Search Vector Store

**Endpoint:** `POST /v1/vector_stores/{vector_store_id}/search`

Semantic search within a specific vector store.

```json
{
  "queries": ["What is the return policy?"],
  "max_num_results": 10,
  "filters": {
    "document_type": "policy"
  },
  "score_threshold": 0.7
}
```

**Response:**

```json
{
  "object": "file_search.results",
  "vector_store_id": "vs_123",
  "queries": ["What is the return policy?"],
  "results": [
    {
      "file_id": "file_123",
      "filename": "policies.pdf",
      "text": "Our return policy allows customers to return items within 30 days...",
      "score": 0.95,
      "attributes": {
        "segment_index": 42,
        "document_type": "policy",
        "page": 5
      }
    }
  ]
}
```

**Note:** This endpoint provides direct access to vector store search. For integrated search with response generation, use the [Response Generation API](./response_generation_api.md) with `file_search` tools.

## Modify Vector Store

**Endpoint:** `POST /v1/vector_stores/{vector_store_id}`

```json
{
  "name": "Updated Support Documents",
  "description": "Updated customer support documentation",
  "join_file_ids": ["file_789"],
  "left_file_ids": ["file_123"]
}
```

## Delete Vector Store

**Endpoint:** `DELETE /v1/vector_stores/{vector_store_id}`

```json
{
  "id": "vs_abc123",
  "object": "vector_store.deleted",
  "deleted": true,
  "task_id": "delete-vs_abc123"
}
```

## Get Vector Store Summary

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
