"""Parameters for function definition in a tool."""

from typing import Any, Dict, List, Optional

from pydantic import Field
from ._models import BaseModel


class FunctionParameters(BaseModel):
    """Parameters for function definition in a tool."""

    type: str = Field(..., description="The type of the parameters, usually 'object'")
    properties: Dict[str, Any] = Field(..., description="Properties of the function parameters")
    required: Optional[List[str]] = Field(None, description="List of required parameter names")
