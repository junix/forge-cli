from datetime import datetime
from enum import Enum  # Added for potential Enum usage
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field  # Added Field

# Suggested Enum for FileStatus if a fixed set of statuses is known:
# class FileStatus(str, Enum):
#     UPLOADING = "uploading"
#     UPLOADED = "uploaded"
#     PROCESSING = "processing"
#     COMPLETED = "completed"
#     FAILED = "failed"


class File(BaseModel):
    """
    Represents a file entity with its attributes.
    """

    id: str
    custom_id: Optional[str] = None
    name: str
    size: int
    content_type: str
    md5: Optional[str] = None
    purpose: str
    status: str  # Replace with FileStatus if using the Enum: status: FileStatus
    created_at: datetime
    updated_at: datetime
    processing_task_id: Optional[str] = None
    processing_error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        # Example for Pydantic V2 if needed, or for aliasing if API fields differ
        # populate_by_name = True
        # alias_generator = to_camel
        # allow_population_by_field_name = True
        pass


# Example of how to convert field names to camelCase if the API uses that
# (for Pydantic V1, use `alias_generator = to_camel_case` and `allow_population_by_alias = True`)
# def to_camel(string: str) -> str:
#     return ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(string.split('_')))

# If you needed to use this model with FastAPI or similar, you might also add:
# class FileCreate(BaseModel):
#     # Fields required to create a file, subset of File
#     pass

# class FileUpdate(BaseModel):
#     # Fields that can be updated on a file
#     pass


# Suggested Enum for VectorStoreStatus if a fixed set of statuses is known:
# class VectorStoreStatus(str, Enum):
#     CREATING = "creating"
#     ACTIVE = "active"
#     PROCESSING = "processing" # Or more specific like PROCESSING_FILES
#     UPDATING = "updating"
#     FAILED = "failed"
#     DELETED = "deleted"


class Vectorstore(BaseModel):
    """
    Represents a vector store entity with its attributes.
    """

    id: str
    name: str
    description: Optional[str] = None
    file_ids: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    status: str  # Replace with VectorStoreStatus if using the Enum
    created_at: datetime
    updated_at: datetime
    file_count: int
    total_size_bytes: int
    last_task_id: Optional[str] = None
    last_task_status: Optional[str] = None
    last_processed_at: Optional[datetime] = None

    class Config:
        # Example for Pydantic V2 if needed, or for aliasing if API fields differ
        # populate_by_name = True
        # alias_generator = to_camel
        # allow_population_by_field_name = True
        pass
