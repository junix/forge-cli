from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

class VectorStoreQueryResultItem(BaseModel):
    """
    Represents a single item in a vector store query result.
    """
    id: str = Field(description="Unique identifier for the result item (e.g., chunk ID or document ID).")
    vector_store_id: str = Field(description="Identifier of the vector store this result belongs to.")
    file_id: Optional[str] = Field(None, description="Identifier of the source file, if applicable.")

    score: float = Field(description="Relevance score of the result item for the query.")
    text: str = Field(description="The actual text content of the result item.")
    metadata: Optional[dict[str, Any]] = Field(None, description="Any associated metadata with the result item.")

    created_at: Optional[datetime] = Field(None, description="Timestamp when the underlying data was created or indexed.")
    # Add other relevant fields like chunk_index, document_title, etc., if available from API

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class VectorStoreQueryResponse(BaseModel):
    """
    Represents the response from a vector store query operation.
    """
    object_field: str = Field(default="list", alias="object", description="The type of object, typically 'list'.")
    data: List[VectorStoreQueryResultItem] = Field(description="A list of query result items.")

    vector_store_id: str = Field(description="Identifier of the vector store that was queried.")
    query: str = Field(description="The original query string.")
    top_k: int = Field(description="The number of results requested.")

    # Optional pagination fields if supported by the API
    # total_results: Optional[int] = Field(None, description="Total number of results available for the query.")
    # limit: Optional[int] = Field(None, description="The maximum number of items to return.")
    # offset: Optional[int] = Field(None, description="The starting position of the results.")
    # next_page_token: Optional[str] = Field(None, description="Token for fetching the next page of results.")

    # Additional metadata about the query execution
    # duration_ms: Optional[float] = Field(None, description="Time taken for the query in milliseconds.")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

# Example Usage (for illustration):
# item_data = {
#     "id": "chunk_789",
#     "vector_store_id": "vs_123",
#     "file_id": "file_abc",
#     "score": 0.89,
#     "text": "This is a relevant snippet of text from the document.",
#     "metadata": {"source": "document_xyz.pdf", "page": 2}
# }
# query_item = VectorStoreQueryResultItem(**item_data)
#
# response_data = {
#     "object": "list",
#     "data": [item_data],
#     "vector_store_id": "vs_123",
#     "query": "What is type safety?",
#     "top_k": 1
# }
# query_response = VectorStoreQueryResponse(**response_data)
