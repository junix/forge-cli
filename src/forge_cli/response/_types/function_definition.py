"""Definition of a function that can be called by the model."""


from pydantic import Field

from ._models import BaseModel
from .function_parameters import FunctionParameters


class FunctionDefinition(BaseModel):
    """Definition of a function that can be called by the model."""

    name: str = Field(..., description="Name of the function")
    description: str | None = Field(None, description="Description of what the function does")
    parameters: FunctionParameters = Field(..., description="Parameters that the function accepts")
