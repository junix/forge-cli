from __future__ import annotations

from pydantic import BaseModel, Field


class DeleteResponse(BaseModel):
    """
    Standard response for delete operations.
    """

    id: str = Field(description="The unique identifier of the deleted resource.")
    object_field: str = Field(
        alias="object", description="The type of object that was deleted (e.g., 'file', 'vector_store')."
    )
    deleted: bool = Field(description="Indicates whether the deletion was successful.")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


# Example usage:
# delete_data = {"id": "file_123", "object": "file", "deleted": True}
# del_resp = DeleteResponse(**delete_data)
