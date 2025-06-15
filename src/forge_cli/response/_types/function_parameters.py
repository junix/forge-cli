"""Parameters for function definition in a tool."""

from typing import Any

from pydantic import Field

from ._models import BaseModel


class FunctionParameters(BaseModel):
    """Parameters for function definition in a tool."""

    type: str = Field(..., description="The type of the parameters, usually 'object'")
    properties: dict[str, Any] = Field(..., description="Properties of the function parameters")
    required: list[str] | None = Field(None, description="List of required parameter names")
