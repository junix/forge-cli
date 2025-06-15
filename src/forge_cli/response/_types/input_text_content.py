"""Text content provided as input to the model."""

from pydantic import Field

from ._models import BaseModel


class InputTextContent(BaseModel):
    """Text content provided as input to the model."""

    type: str = Field("input_text", description="The type of content, must be 'input_text'")
    text: str = Field(..., description="The actual text content sent to the model")
