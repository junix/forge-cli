# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from collections.abc import Collection
from typing import List, Optional, Union

from openai.types.shared.comparison_filter import ComparisonFilter
from openai.types.shared.compound_filter import CompoundFilter
from typing_extensions import Literal, TypeAlias

from ._models import BaseModel
from message._types.tool import Tool, JSONSchemaParameters, JSONSchemaProperty

__all__ = ["FileSearchTool", "Filters", "RankingOptions"]

Filters: TypeAlias = Union[ComparisonFilter, CompoundFilter, None]


class RankingOptions(BaseModel):
    ranker: Optional[Literal["auto", "default-2024-11-15"]] = None
    """The ranker to use for the file search."""

    score_threshold: Optional[float] = None
    """The score threshold for the file search, a number between 0 and 1.

    Numbers closer to 1 will attempt to return only the most relevant results, but
    may return fewer results.
    """


class FileSearchTool(BaseModel):
    type: Literal["file_search"]
    """The type of the file search tool. Always `file_search`."""

    vector_store_ids: List[str]
    """The IDs of the vector stores to search."""

    filters: Optional[Filters] = None
    """A filter to apply."""

    max_num_results: Optional[int] = None
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive.
    """

    ranking_options: Optional[RankingOptions] = None
    """Ranking options for search."""


    def as_openai_tool(self, collections: dict[str, Collection] = None, strict: bool = False, **kwargs) -> Tool:
        """Convert FileSearchTool to OpenAI-compatible Tool definition.

        Creates a Tool object representing a function that performs file search
        operations. The function accepts an array of query strings and searches
        through the specified vector stores.

        Args:
            collections (dict[str, Collection], optional): Dictionary mapping collection IDs 
                to Collection objects, used to generate descriptions of available collections.
            strict (bool, optional): Whether to enable strict validation for the tool schema.
                Defaults to False.
            **kwargs: Additional keyword arguments (currently unused).

        Returns:
            Tool: An OpenAI-compatible tool definition with:
                - name: "file_search"
                - description: Detailed description of file search functionality and available collections
                - parameters: JSON Schema for the queries parameter (array of strings)
                - strict: Optional strict validation flag

        Example:
            >>> file_search = FileSearchTool(
            ...     type="file_search",
            ...     vector_store_ids=["vs_123", "vs_456"]
            ... )
            >>> tool = file_search.as_openai_tool()
            >>> print(tool.name)
            file_search
            >>> print(tool.parameters.properties["queries"].type)
            array

            >>> # With collections information
            >>> from collection import Collection
            >>> collections = {
            ...     "vs_tech": Collection(name="Tech Docs", description="Technology documentation"),
            ...     "vs_science": Collection(name="Science Papers", description="Scientific research papers")
            ... }
            >>> tool_with_collections = file_search.as_openai_tool(
            ...     collections=collections,
            ...     strict=True
            ... )
            >>> print("vs_tech" in tool_with_collections.description)
            True
            >>> print("Technology documentation" in tool_with_collections.description)
            True
        """
        # Build description with collection information
        if collections:
            collection_descriptions = []
            for collection_id, collection in collections.items():
                collection_descriptions.append(f"""<collection id=\"{collection_id}\">
    <name>{collection.name}</name>
    <description>{collection.description}</description>
</collection>""")
            
            collections_text = "\n".join(collection_descriptions)
            description = (
                "Search knowledge in a vector store.\n"
                "Available collections:\n"
                f"{collections_text}\n"
                "Each query should be a string representing a search term or question. "
                "Multiple queries can be provided for comprehensive search."
            )
        else:
            description = (
                "Search knowledge in a vector store.\n"
                "Each query should be a string representing a search term or question. "
                "Multiple queries can be provided for comprehensive search."
            )

        # Define the parameters schema for the file search function
        parameters = JSONSchemaParameters(
            type="object",
            properties={
                "queries": JSONSchemaProperty(
                    type="array",
                    items={"type": "string"},
                    description="One or more search queries to find relevant chunks in the collections",
                )
            },
            required=["queries"],
            additionalProperties=False,
        )

        # Create and return the Tool object
        return Tool(name="file_search", description=description, parameters=parameters, strict=strict)
