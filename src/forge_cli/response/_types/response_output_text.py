# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel
from .annotations import Annotation

__all__ = [
    "ResponseOutputText",
]


class ResponseOutputText(BaseModel):
    annotations: list[Annotation]
    """The annotations of the text output."""

    text: str
    """The text output from the model."""

    type: Literal["output_text"]
    """The type of the output text. Always `output_text`."""
