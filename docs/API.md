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

Below is an example of how to construct a typed `Request` object using Python. The `forge_cli.response._types` module provides the necessary classes.

```python
from forge_cli.response._types import Request, InputMessage, FileSearchTool, WebSearchTool

# Create input messages
messages = [
    InputMessage(
        type="input_text", # This might be inferred by Pydantic if text is given directly
        text="What is the refund policy in our documents?"
    )
]

# Define tools
tools = [
    FileSearchTool( # Populates the 'tool_choice' or specific tool fields if applicable
        file_search={
            "vector_store_ids": ["vs_abc123"],
            "max_num_results": 10
        }
    ),
    WebSearchTool(
        web_search={
            "max_results": 5
        }
    )
]

# Create the typed Request object
# Note: Some fields like 'user' might be part of a session or client config
# rather than directly in each Request model instance depending on SDK design.
# The example below assumes 'user' is part of the Request model.
typed_request = Request(
    user="user-123", # Or handle user via client/session
    input=messages,
    tools=tools,
    effort="high",
    stream=True,
    store=True,
    previous_response_id="resp_xyz789"
    # Other parameters like 'temperature', 'max_output_tokens' can be added here
)

# To get the dictionary format (e.g., for sending as JSON to an older endpoint):
# request_dict = typed_request.model_dump(by_alias=True, exclude_none=True)
# import json
# print(json.dumps(request_dict, indent=2))
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

Below is a Python example demonstrating how to use the typed `Request` object with the SDK function `astream_typed_response` for streaming:

```python
import asyncio
from forge_cli.response._types import Request, InputMessage, FileSearchTool
from forge_cli.sdk import astream_typed_response # Or async_create_typed_response for non-streaming

async def get_ai_response():
    # 1. Create a typed Request object
    messages = [
        InputMessage(text="Explain our refund policy")
    ]

    tools = [
        FileSearchTool(
            file_search={"vector_store_ids": ["vs_123"]}
        )
    ]

    request = Request(
        user="user-123", # Ensure 'user' is a valid field in your Request model or handle appropriately
        input=messages,
        tools=tools,
        effort="high",
        stream=True # Important for astream_typed_response
    )

    # 2. Call the typed SDK function for streaming
    print("Streaming response:")
    try:
        async for event_type, event_data in astream_typed_response(request):
            if event_data is None: # Some events might have no data (e.g. just 'done')
                if event_type == "done":
                    print("\n\nStream completed (done event).")
                continue

            if event_type == "response.output_text.delta" and event_data.delta:
                print(event_data.delta.text, end="", flush=True)
            elif event_type == "response.completed":
                print("\n\nStream completed (response.completed event).")
                # The final Response object is often part of event_data here for 'response.completed'
                # Example: final_response_data = event_data.response
                # print(f"Final Response ID: {final_response_data.id if final_response_data else 'N/A'}")
            elif event_type == "error" and event_data.message:
                print(f"\nError: {event_data.message}")
                break
            # Add more specific event handling as needed
            # For example, to see all events:
            # else:
            #    print(f"\nEvent: {event_type}, Data: {event_data.model_dump_json(indent=2) if hasattr(event_data, 'model_dump_json') else event_data}")

    except Exception as e:
        print(f"\nAn error occurred during streaming: {e}")

if __name__ == "__main__":
    # Note: Ensure KNOWLEDGE_FORGE_URL environment variable is set if your SDK relies on it.
    # Example: os.environ["KNOWLEDGE_FORGE_URL"] = "http://localhost:10000"
    asyncio.run(get_ai_response())
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

Input messages are structured using Pydantic models from `forge_cli.response._types`. An `InputMessage` object typically contains a list of content parts (like text or images).

```python
from forge_cli.response._types import InputMessage, InputTextContent, InputImageContent

# Text Input Example
# The 'content' field of InputMessage can be a simple string for text,
# or a list of content blocks for multi-modal input.
text_message = InputMessage(
    role="user",
    content="Your question here" # Simple text content
)

# Alternatively, for more structured text or multi-part messages:
structured_text_message = InputMessage(
    role="user",
    content=[
        InputTextContent(type="text", text="Your question here")
    ]
)

# Image Input Example
# Assuming InputImageContent is used within the content list of an InputMessage
image_message = InputMessage(
    role="user",
    content=[
        InputTextContent(type="text", text="What do you see in this image?"),
        InputImageContent(
            type="image_url", # or "image_base64"
            image_url={"url": "https://example.com/image.jpg", "detail": "auto"}
            # For base64: image_base64={"base64": "...", "media_type": "image/jpeg"}
        )
    ]
)

# File Input (Conceptual)
# Direct file content within an InputMessage is less common with Pydantic models.
# Typically, files are uploaded separately and referred to by ID, or specific tools handle file inputs.
# If a model like 'InputFileContent' were available for direct inclusion:
# file_content_message = InputMessage(
#     role="user",
#     content=[
#         InputFileContent(type="file_url", file_url={"url": "https://example.com/document.pdf"})
#         # Or, if referring to an already uploaded file:
#         # InputFileReference(type="file_id", file_id="file_abc123")
#     ]
# )
# Note: The exact structure for InputFileContent would depend on its definition in _types.
# For now, text and image inputs are more clearly defined for the content list.
```

#### Tool Definitions

Tools are defined using Pydantic models from `forge_cli.response._types`. These models are then included in the `tools` list of a `Request` object.

```python
from forge_cli.response._types import (
    FileSearchTool,
    WebSearchTool,
    DocumentFinderTool,
    FileSearchToolParam, # Parameter models for tool configuration
    WebSearchToolParam,
    DocumentFinderToolParam
)

# File Search Tool Example
# The main tool model (e.g., FileSearchTool) often wraps a parameter model
# (e.g., FileSearchToolParam) that holds the actual configuration.
file_search_params = FileSearchToolParam(
    vector_store_ids=["vs_123"],
    max_num_results=10,
    filters={"key": "value"} # Filters might have a more structured type
)
file_search_tool = FileSearchTool(
    type="file_search", # This type field is often part of the base Tool model
    file_search=file_search_params
)


# Web Search Tool Example
web_search_params = WebSearchToolParam(
    max_results=5
    # search_context_size="medium" # Include if part of WebSearchToolParam
)
web_search_tool = WebSearchTool(
    type="web_search",
    web_search=web_search_params
)


# Document Finder Tool Example
doc_finder_params = DocumentFinderToolParam(
    vector_store_ids=["vs_123", "vs_456"],
    max_num_results=5, # If 'max_num_results' is part of DocumentFinderToolParam
    filters={"document_type": "policy"} # Filters might have a more structured type
)
doc_finder_tool = DocumentFinderTool(
    type="document_finder",
    document_finder=doc_finder_params
)

# These tool objects would then be used in a Request:
# from forge_cli.response._types import Request, InputMessage
# request = Request(
#     input=[InputMessage(content="Search for policy documents.")],
#     tools=[file_search_tool, web_search_tool, doc_finder_tool]
# )
```

#### Response Structure

The API response is a Pydantic model, `Response`, defined in `forge_cli.response._types`. It includes various nested models for output items, tool calls, and usage statistics.

```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from forge_cli.response._types import (
    Response,
    ResponseOutputText, # Example of an output item
    ResponseFileSearchToolCall, # Example of a tool call item
    ResponseUsage,
    AnnotationFileCitation # For annotations within text
)

# Example of constructing a Response object (typically done by the SDK when receiving API data)
# This demonstrates the structure; you usually wouldn't build this manually as a user.

# Sample annotation
sample_annotation = AnnotationFileCitation(
    type="file_citation",
    text="documents",
    file_id="file_doc456",
    start_index=18,
    end_index=27,
    filename="policy.pdf",
    snippet="the relevant section from policy.pdf"
)

# Sample output item (text)
output_text_item = ResponseOutputText(
    type="output_text",
    text="Based on the documents, our refund policy...",
    annotations=[sample_annotation] # Annotations list
)

# Sample tool call (file search)
file_search_tool_call = ResponseFileSearchToolCall(
    id="call_123",
    type="file_search", # This should match the specific tool call type, e.g. "file_search_tool_call"
    # The actual tool call data would be nested here, e.g.,
    # file_search={"queries": ["refund policy"], "results": [...]}
    # For simplicity, specific tool call fields are omitted here.
    # Refer to specific tool call models like ResponseFileSearchToolCall,
    # ResponseWebSearchToolCall, etc., for their detailed structure.
    status="completed", # Added status, which is common for tool calls
    results=[{"document_id": "doc_xyz", "score": 0.9}] # Simplified results
)

# Sample usage statistics
usage_stats = ResponseUsage(
    input_tokens=100,
    output_tokens=200,
    total_tokens=300
)

# Constructing the main Response object
api_response = Response(
    id="resp_123",
    object="response", # Or inferred if it's a Literal in the model
    created_at=datetime.now(), # Or an int timestamp: 1699061776
    status="completed",
    model="qwen-max-latest", # Added model field
    output=[output_text_item], # List of ResponseOutputItem instances
    # The 'tool_calls' field might be part of 'output' items of type 'tool_call',
    # or a separate top-level field depending on the exact Pydantic model definition.
    # If tool calls are part of output:
    # output=[output_text_item, file_search_tool_call],
    # If 'tool_calls' is a distinct field:
    # tool_calls=[file_search_tool_call], # Assuming a top-level field
    usage=usage_stats,
    # Other fields like 'user', 'effort', 'previous_response_id' might also be present
    user="user-123",
    effort="high"
)

# Accessing data from the typed Response object:
# print(f"Response ID: {api_response.id}")
# if api_response.output:
#     for item in api_response.output:
#         if isinstance(item, ResponseOutputText):
#             print(f"Assistant says: {item.text}")
#             if item.annotations:
#                 for ann in item.annotations:
#                     if isinstance(ann, AnnotationFileCitation):
#                         print(f"  Cited: {ann.filename} (ID: {ann.file_id})")
# if api_response.usage:
#     print(f"Tokens used: {api_response.usage.total_tokens}")

```

## Client Libraries

### Python SDK Example

The following example demonstrates using the Python SDK with the new typed Pydantic models for requests and responses. It showcases both streaming and non-streaming response generation.

```python
import asyncio
import os
from forge_cli.response._types import (
    Request,
    InputMessage,
    # InputTextContent, # Use if you prefer structured text content
    FileSearchTool,
    FileSearchToolParam,
    Response # For non-streaming example
)
# Assuming your SDK functions are available in forge_cli.sdk
from forge_cli.sdk import (
    astream_typed_response,
    async_create_typed_response,
    # Conceptual: async_upload_file,
    # Conceptual: async_create_vectorstore
)

# Note: For a runnable example, ensure KNOWLEDGE_FORGE_URL is set, e.g.:
# os.environ["KNOWLEDGE_FORGE_URL"] = "http://localhost:10000"
# Actual file/VS management SDK functions would be used in a real scenario.

async def main():
    # --- Conceptual Setup: File and Vector Store ---
    # This part is illustrative. In a real application, you'd use actual file paths
    # and await the results of async_upload_file and async_create_vectorstore.
    # For this documentation example, we'll use placeholder IDs.
    file_id = "file_placeholder_doc.pdf"
    vs_id = "vs_placeholder_my_documents"
    print(f"Conceptual setup: Using File ID: {file_id}, Vector Store ID: {vs_id}\n")
    # --- End of Conceptual Setup ---

    # 1. Create a typed Request for asking a question
    messages = [
        InputMessage(role="user", content="What is mentioned about refunds in the document?")
        # Example with structured text content:
        # InputMessage(role="user", content=[InputTextContent(text="What about refunds?")])
    ]

    tools = [
        FileSearchTool(
            type="file_search",
            file_search=FileSearchToolParam(vector_store_ids=[vs_id], max_num_results=5)
        )
        # Example of adding WebSearchTool:
        # from forge_cli.response._types import WebSearchTool, WebSearchToolParam
        # WebSearchTool(type="web_search", web_search=WebSearchToolParam(max_results=3))
    ]

    # Create the main request object for streaming
    typed_request_streaming = Request(
        input=messages,
        tools=tools,
        model="qwen-max-latest", # Specify your desired model
        effort="high",
        stream=True,
        user="typed_sdk_user_streaming" # Optional: if your Request model includes user
    )

    # 2. Get response using streaming with astream_typed_response
    print("--- Streaming Typed Response Example ---")
    try:
        async for event_type, event_data in astream_typed_response(request=typed_request_streaming):
            if event_data is None: # Some events like 'done' might not have data
                if event_type == "done":
                    print("\nStream finished (done event).")
                continue

            if event_type == "response.output_text.delta" and hasattr(event_data, 'delta') and event_data.delta:
                print(event_data.delta.text, end="", flush=True)
            elif event_type == "response.completed" and hasattr(event_data, 'response'):
                print("\nStream fully completed (response.completed event).")
                if event_data.response and event_data.response.usage:
                   print(f"Usage: {event_data.response.usage.total_tokens} tokens")
            elif event_type == "error" and hasattr(event_data, 'message'):
                print(f"\nError during stream: {event_data.message}")
                break
            # Add more handlers for other event types (e.g., tool calls) as needed
            # elif "tool_call" in event_type:
            #     print(f"\nTool event: {event_type} - Data: {event_data.model_dump_json(indent=2)}")
        print("\n------------------------------------")
    except Exception as e:
        print(f"\nError during streaming response: {e}")
        print("------------------------------------")


    # 3. (Alternative) Get a non-streaming typed response
    print("\n--- Non-Streaming Typed Response Example ---")
    # Create a new request object or copy and modify the streaming one
    typed_request_non_streaming = Request(
        input=messages, # Reusing messages and tools from above
        tools=tools,
        model="qwen-max-latest",
        effort="high",
        stream=False, # Key change for non-streaming
        user="typed_sdk_user_non_streaming"
    )
    try:
        final_response: Response = await async_create_typed_response(request=typed_request_non_streaming)
        if final_response:
            print(f"Response ID: {final_response.id}")
            print(f"Status: {final_response.status}")
            if final_response.output:
                for item in final_response.output:
                    # Example: Accessing text from ResponseOutputText
                    if item.type == "output_text" and hasattr(item, 'text'):
                        print(f"Output Text: {item.text}")
                        if hasattr(item, 'annotations') and item.annotations:
                            print("Annotations:")
                            for ann in item.annotations:
                                # .model_dump_json() is a Pydantic V2 method
                                print(f"  - {ann.model_dump_json(indent=2) if hasattr(ann, 'model_dump_json') else vars(ann)}")
            if final_response.usage:
                print(f"Total tokens: {final_response.usage.total_tokens}")
        else:
            print("Failed to get a non-streaming typed response.")
    except Exception as e:
        print(f"Error during non-streaming typed response: {e}")
    print("----------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
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