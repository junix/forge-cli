"""Format specification for text output."""

from pydantic import Field

from ._models import BaseModel


class TextFormatType(BaseModel):
    """Format specification for text output."""

    type: str = Field("text", description="The type of text format, typically 'text'")
