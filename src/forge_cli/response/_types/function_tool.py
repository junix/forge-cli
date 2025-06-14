# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["FunctionTool"]


class FunctionTool(BaseModel):
    name: str
    """The name of the function to call."""

    parameters: dict[str, object] | None = None
    """A JSON schema object describing the parameters of the function."""

    strict: bool | None = None
    """Whether to enforce strict parameter validation. Default `true`."""

    type: Literal["function"]
    """The type of the function tool. Always `function`."""

    description: str | None = None
    """A description of the function.

    Used by the model to determine whether or not to call the function.
    """
