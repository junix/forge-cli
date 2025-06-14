# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ._models import BaseModel
from message._types.tool import Tool, JSONSchemaParameters, JSONSchemaProperty

__all__ = ["WebSearchTool", "UserLocation"]


class UserLocation(BaseModel):
    type: Literal["approximate"]
    """The type of location approximation. Always `approximate`."""

    city: Optional[str] = None
    """Free text input for the city of the user, e.g. `San Francisco`."""

    country: Optional[str] = None
    """
    The two-letter [ISO country code](https://en.wikipedia.org/wiki/ISO_3166-1) of
    the user, e.g. `US`.
    """

    region: Optional[str] = None
    """Free text input for the region of the user, e.g. `California`."""

    timezone: Optional[str] = None
    """
    The [IANA timezone](https://timeapi.io/documentation/iana-timezones) of the
    user, e.g. `America/Los_Angeles`.
    """


class WebSearchTool(BaseModel):
    type: Literal["web_search_preview", "web_search_preview_2025_03_11", "web_search"]
    """The type of the web search tool.

    One of `web_search_preview` or `web_search_preview_2025_03_11`.
    """

    search_context_size: Optional[Literal["low", "medium", "high"]] = None
    """High level guidance for the amount of context window space to use for the
    search.

    One of `low`, `medium`, or `high`. `medium` is the default.
    """

    user_location: Optional[UserLocation] = None
    """The user's location."""

    def as_openai_tool(self, strict: bool = False, **kwargs) -> Tool:
        """Convert WebSearchTool to OpenAI-compatible Tool definition.

        Creates a Tool object representing a function that performs web search
        operations. The function accepts search queries and retrieves relevant
        information from the internet.

        Args:
            strict (bool, optional): Whether to enable strict validation for the tool schema.
                Defaults to False.
            **kwargs: Additional keyword arguments (currently unused).

        Returns:
            Tool: An OpenAI-compatible tool definition with:
                - name: "web_search"
                - description: Detailed description of web search functionality
                - parameters: JSON Schema for the queries parameter (array of strings)
                - strict: Optional strict validation flag

        Example:
            >>> web_search = WebSearchTool(
            ...     type="web_search",
            ...     search_context_size="medium"
            ... )
            >>> tool = web_search.as_openai_tool()
            >>> print(tool.name)
            web_search
            >>> print(tool.parameters.properties["queries"].type)
            array
            
            >>> # With strict validation
            >>> tool_strict = web_search.as_openai_tool(strict=True)
            >>> print(tool_strict.strict)
            True
        """
        # Build description based on tool configuration
        description_parts = [
            "Search the web for current information, news, facts, and real-time data. "
            "This tool provides access to up-to-date information from the internet "
            "that may not be available in the model's training data."
        ]
        
        description = "".join(description_parts) + " Provide one or more search queries to find relevant information."

        # Define the parameters schema for the web search function
        parameters = JSONSchemaParameters(
            type="object",
            properties={
                "queries": JSONSchemaProperty(
                    type="array",
                    items={"type": "string"},
                    description="One or more search queries to find relevant information on the web",
                )
            },
            required=["queries"],
            additionalProperties=False,
        )

        # Create and return the Tool object
        return Tool(name="web_search", description=description, parameters=parameters, strict=strict)
