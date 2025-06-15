# Tasks API

**Base Path:** `/v1/tasks`

Several API operations, such as creating a vector store or uploading a file, are performed asynchronously. When you initiate one of these operations, the API will start a background task and immediately return an object containing a `task_id`.

You can use the endpoints on this page to retrieve the status of that task, allowing you to monitor its progress, check for completion, or see if an error occurred.

## Get Task Status

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

* `pending` - Task queued but not started
* `in_progress` - Task currently running  
* `completed` - Task finished successfully
* `failed` - Task failed with an error
* `cancelled` - Task was cancelled before completion

**Common Task Types:**

* `file_processing` - File upload and content extraction
* `vectorization` - Converting documents to embeddings
* `vector_store_creation` - Creating new vector collections
* `document_analysis` - Generating summaries/abstracts

## The Task Object (Trace)

The `Trace` object is returned when you query a task's status.

```python
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any

class Trace(BaseModel):
    """Represents a background task or job."""
    id: str = Field(description="Unique task identifier.")
    status: Optional[str] = Field(None, description="Current status (e.g., 'pending', 'running', 'completed', 'failed').")
    progress: float = Field(default=0.0, description="Task completion progress (0.0 to 1.0)." )
    data: Optional[Union[str, int, float, list, Dict[str, Any]]] = Field(None, description="Associated data for the task.")
    failure_reason: Optional[str] = Field(None, description="Reason for task failure if status is 'failed'.")
```
