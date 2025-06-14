"""A message provided as input to the model."""

from typing import List, Optional, Union

from pydantic import Field
from ._models import BaseModel
from .input_image_content import InputImageContent
from .input_text_content import InputTextContent


class InputMessage(BaseModel):
    """A message provided as input to the model."""

    role: str = Field(
        ...,
        description="Role of the message sender, e.g., 'user', 'assistant', 'system'",
    )
    content: Union[str, List[Union[InputTextContent, InputImageContent]]] = Field(
        ...,
        description="Content of the message, either a string or a list of content objects supporting text and images",
    )
    name: Optional[str] = Field(None, description="Name of the message sender, optional identifier")
