from typing import Any, Dict, List, Optional, TYPE_CHECKING
from typing_extensions import Literal

from pydantic import BaseModel, Field, PrivateAttr

if TYPE_CHECKING:
    from message._types.tool_call import ToolCall

from .response_function_tool_call import (
    ResponseFunctionToolCall,
)

from common.logger import logger
from _types.chunk import Chunk
from constants.metadata_keys import (
    FILE_ID_KEY,
    DOC_ID_KEY,
)
from message._types.tool import Tool, JSONSchemaParameters, JSONSchemaProperty


class FileReaderTool(BaseModel):
    """Response function for file reader tool calls.

    This class represents a file reader tool call in the LLM response.
    It contains the query to be answered based on document content and
    document IDs to read.

    Attributes:
        type (str): The type of the function, always "file_reader_call"
        status (Literal): The current status of the file reader call ("in_progress", "searching", "completed", "incomplete")
        doc_ids (List[str]): List of document IDs to be read
        query (str): The query to answer based on the document content
        progress (float): Reading progress from 0.0 to 1.0
        navigation (str): Browsing history/path as a string
        _results (Optional[List[Chunk]]): The results of the file reading operation
        _native_tool_call (Optional[ResponseFunctionToolCall]): The native tool call
        _navigator (Any): Private temporary navigator object (not serialized)
    """

    type: Literal["file_reader"] = "file_reader"

    def as_openai_tool(self, documents: list["Document"] = None, strict: bool = False, **kwargs) -> Tool:
        """Convert FileReaderTool to OpenAI-compatible Tool definition.

        Creates a Tool object representing a function that performs file reading
        operations. The function accepts document IDs and reads their content in detail.

        Args:
            documents (dict[str, Any], optional): Dictionary mapping document IDs 
                to Document objects, used to generate descriptions of available documents.
            strict (bool, optional): Whether to enable strict validation for the tool schema.
                Defaults to False.
            **kwargs: Additional keyword arguments (currently unused).

        Returns:
            Tool: An OpenAI-compatible tool definition with:
                - name: "file_reader"
                - description: Detailed description of file reading functionality and available documents
                - parameters: JSON Schema for the document_ids parameter (array of strings)
                - strict: Optional strict validation flag

        Example:
            >>> file_reader = FileReaderTool(type="file_reader")
            >>> tool = file_reader.as_openai_tool()
            >>> print(tool.name)
            file_reader
            >>> print(tool.parameters.properties["document_ids"].type)
            array
            
            >>> # With documents information
            >>> documents = {
            ...     "doc_123": Document(title="Tech Guide", description="Technology documentation"),
            ...     "doc_456": Document(title="Science Paper", description="Research findings")
            ... }
            >>> tool_with_docs = file_reader.as_openai_tool(
            ...     documents=documents,
            ...     strict=True
            ... )
            >>> print("doc_123" in tool_with_docs.description)
            True
            >>> print("Tech Guide" in tool_with_docs.description)
            True
        """
        # Build description with document information
        if documents:
            document_descriptions = []
            for document in documents:
                document_descriptions.append(f"""<doc id=\"{document.id}\">{document.title}</doc>""")
            
            documents_text = "\n".join(document_descriptions)
            description = (
                "Read specific documents in detail to get comprehensive information about their content. "
                "This tool allows you to access the full content of documents when you need detailed "
                "information that may not be available through search results alone.\n"
                "Available documents:\n"
                f"{documents_text}\n"
                "Provide one or more document IDs to read their complete content."
            )
        else:
            description = (
                "Read specific documents in detail to get comprehensive information about their content. "
                "This tool allows you to access the full content of documents when you need detailed "
                "information that may not be available through search results alone. "
                "Provide one or more document IDs to read their complete content."
            )

        # Define the parameters schema for the file reader function
        parameters = JSONSchemaParameters(
            type="object",
            properties={
                "document_ids": JSONSchemaProperty(
                    type="array",
                    items={"type": "string"},
                    description="One or more document IDs to read in detail",
                ), 
                "query": JSONSchemaProperty(
                    type="string",
                    description="The query to answer based on the document content",
                ),
            },
            required=["query"],
            additionalProperties=False,
        )

        # Create and return the Tool object
        return Tool(name="file_reader", description=description, parameters=parameters, strict=strict)

