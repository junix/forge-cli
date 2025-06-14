# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal

from ._models import BaseModel
from message._types.tool import Tool, JSONSchemaParameters, JSONSchemaProperty

__all__ = ["DocumentFinderTool"]


class DocumentFinderTool(BaseModel):
    type: Literal["document_finder"]
    """The type of the document finder tool. Always `document_finder`."""

    vector_store_ids: List[str]
    """The IDs of the vector stores to search across."""

    max_num_results: Optional[int] = None
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive. Defaults to 5.
    """

    filters: Optional[Dict[str, Union[str, float, bool, int]]] = None
    """Optional metadata filters to apply during search.
    
    Filters are applied as key-value pairs where the key is the metadata field name
    and the value is the expected value for that field.
    """

    score_threshold: Optional[float] = None
    """Minimum relevance score threshold for results.

    Results with scores below this threshold will be filtered out.
    Should be a value between 0 and 1.
    """

    deduplicate: Optional[bool] = None
    """Whether to remove duplicate documents across vector stores.

    When True, keeps only the highest-scoring version of each document.
    Defaults to True.
    """

    def as_openai_tool(self, collections: dict[str, Any] = None, strict: bool = False, **kwargs) -> Tool:
        """Convert DocumentFinderTool to OpenAI-compatible Tool definition.

        Creates a Tool object representing a function that performs document discovery
        operations. The function accepts search criteria and finds relevant documents
        across vector stores based on metadata and content similarity.

        Args:
            collections (dict[str, Any], optional): Dictionary mapping collection IDs 
                to Collection objects, used to generate descriptions of available collections.
            strict (bool, optional): Whether to enable strict validation for the tool schema.
                Defaults to False.
            **kwargs: Additional keyword arguments (currently unused).

        Returns:
            Tool: An OpenAI-compatible tool definition with:
                - name: "document_finder"
                - description: Detailed description of document discovery functionality and available collections
                - parameters: JSON Schema for the queries parameter (array of strings)
                - strict: Optional strict validation flag

        Example:
            >>> doc_finder = DocumentFinderTool(
            ...     type="document_finder",
            ...     vector_store_ids=["vs_123", "vs_456"],
            ...     max_num_results=10
            ... )
            >>> tool = doc_finder.as_openai_tool()
            >>> print(tool.name)
            document_finder
            >>> print(tool.parameters.properties["queries"].type)
            array
            
            >>> # With collections information
            >>> collections = {
            ...     "vs_tech": Collection(name="Tech Docs", description="Technology documentation"),
            ...     "vs_science": Collection(name="Science Papers", description="Scientific research papers")
            ... }
            >>> tool_with_collections = doc_finder.as_openai_tool(
            ...     collections=collections,
            ...     strict=True
            ... )
            >>> print("vs_tech" in tool_with_collections.description)
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
                "Find and discover documents across vector stores based on search criteria. "
                "This tool helps locate relevant documents by analyzing their metadata and content similarity. "
                "Use this when you need to identify which documents contain information related to your query.\n"
                "Available collections:\n"
                f"{collections_text}\n"
                "Each query should describe what type of documents or content you're looking for."
            )
        else:
            description = (
                "Find and discover documents across vector stores based on search criteria. "
                "This tool helps locate relevant documents by analyzing their metadata and content similarity. "
                "Use this when you need to identify which documents contain information related to your query. "
                "Each query should describe what type of documents or content you're looking for."
            )

        # Define the parameters schema for the document finder function
        parameters = JSONSchemaParameters(
            type="object",
            properties={
                "queries": JSONSchemaProperty(
                    type="array",
                    items=JSONSchemaProperty(type="string"),
                    description="One or more search queries describing the type of documents or content to find",
                )
            },
            required=["queries"],
            additionalProperties=False,
        )

        # Create and return the Tool object
        return Tool(name="document_finder", description=description, parameters=parameters, strict=strict)
