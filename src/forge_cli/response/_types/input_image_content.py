"""Image content provided as input to the model."""

from pydantic import Field
from ._models import BaseModel


class InputImageContent(BaseModel):
    """Image content provided as input to the model."""

    type: str = Field("input_image", description="The type of content, must be 'input_image'")
    image_url: str = Field(..., description="URL or base64 encoded image data")
