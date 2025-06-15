"""Format specification for the response."""


from pydantic import Field

from ._models import BaseModel


class ResponseFormat(BaseModel):
    """Specifies the format of the response."""

    type: str | None = Field(None, description="The type of the response format, e.g., 'json_object'")
