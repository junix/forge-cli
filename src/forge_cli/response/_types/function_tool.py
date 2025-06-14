# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Any, Dict, Optional
from typing_extensions import Literal

from ._models import BaseModel
from message._types.tool import Tool, JSONSchemaParameters

__all__ = ["FunctionTool"]


class FunctionTool(BaseModel):
    name: str
    """The name of the function to call."""

    parameters: Optional[Dict[str, object]] = None
    """A JSON schema object describing the parameters of the function."""

    strict: Optional[bool] = None
    """Whether to enforce strict parameter validation. Default `true`."""

    type: Literal["function"]
    """The type of the function tool. Always `function`."""

    description: Optional[str] = None
    """A description of the function.

    Used by the model to determine whether or not to call the function.
    """

    def as_openai_tool(self, strict: bool = None, **kwargs) -> Tool:
        """Convert FunctionTool to OpenAI-compatible Tool definition.

        Creates a Tool object representing a generic function that can be called
        with custom parameters. This method converts the FunctionTool's existing
        configuration into the OpenAI tool format.

        Args:
            strict (bool, optional): Whether to enable strict validation for the tool schema.
                If not provided, uses the tool's own strict setting or defaults to False.
            **kwargs: Additional keyword arguments (currently unused).

        Returns:
            Tool: An OpenAI-compatible tool definition with:
                - name: The function name
                - description: The function description or a default description
                - parameters: JSON Schema converted from the tool's parameters
                - strict: Strict validation flag

        Example:
            >>> func_tool = FunctionTool(
            ...     name="calculate_tax",
            ...     type="function",
            ...     description="Calculate tax based on income and deductions",
            ...     parameters={"income": {"type": "number"}, "deductions": {"type": "number"}},
            ...     strict=True
            ... )
            >>> tool = func_tool.as_openai_tool()
            >>> print(tool.name)
            calculate_tax
            >>> print(tool.description)
            Calculate tax based on income and deductions
            
            >>> # Override strict setting
            >>> tool_no_strict = func_tool.as_openai_tool(strict=False)
            >>> print(tool_no_strict.strict)
            False
            
            >>> # Function without description
            >>> simple_func = FunctionTool(name="helper", type="function")
            >>> tool_simple = simple_func.as_openai_tool()
            >>> print("Execute function" in tool_simple.description)
            True
        """
        # Use provided strict setting, fall back to tool's setting, then to False
        effective_strict = strict if strict is not None else (self.strict if self.strict is not None else False)
        
        # Use provided description or create a default one
        description = self.description if self.description else f"Execute function '{self.name}'"
        
        # Convert parameters to JSONSchemaParameters if available
        parameters = None
        if self.parameters:
            # Convert the parameters dict to JSONSchemaParameters
            # Assume the parameters are already in JSON Schema format
            parameters = JSONSchemaParameters(
                type="object",
                properties=self.parameters.get("properties", {}),
                required=self.parameters.get("required", []),
                additionalProperties=self.parameters.get("additionalProperties", False)
            )
        
        # Create and return the Tool object
        return Tool(
            name=self.name,
            description=description,
            parameters=parameters,
            strict=effective_strict
        )
