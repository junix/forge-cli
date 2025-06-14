"""Enhanced convert_to_response that handles citations from bi-patcher.

This is a proposed enhancement to chat2response.py that demonstrates
how to integrate citation annotations from the bi-patcher.
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from citation._types import Citations

from common.logger import logger

# Import tool name constants
from constants.tool_names import (
    DOCUMENT_FINDER,
    DOCUMENT_FINDER_CALL,
    FILE_READER,
    FILE_READER_CALL,
    FILE_SEARCH,
    FILE_SEARCH_CALL,
    WEB_SEARCH,
    WEB_SEARCH_CALL,
)
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from response._types.response import Response
from response._types.response_output_message import ResponseOutputMessage
from response._types.response_output_text import ResponseOutputText
from response._types.response_reasoning_item import ResponseReasoningItem, Summary
from response.citation_utils import extract_citations_from_chunk_enhanced
from response.id_utils import message_id_of, reason_id_of
from tools.toolset import ToolSet


def convert_to_response(
    chunk_combined: dict[str, Any] | ChatCompletionChunk,
    request_prototype: Response,
    toolset: ToolSet,
    cited: Optional["Citations"] = None,
    reason_cited: Optional["Citations"] = None,
    available_citations: Optional["Citations"] = None,
) -> Response:
    """Enhanced version of convert_to_response that handles citation annotations.

    This version checks for _cited and _reason_cited attributes on the chunk
    and creates proper annotations for the Response API.

    The key changes:
    1. Keep reference to original chunk object
    2. Extract citations using the citation_utils module
    3. Add annotations to ResponseOutputText
    4. Support fallback text-based citation extraction

    Args:
        chunk_combined: ChatCompletionChunk or dict, may have _cited/_reason_cited
        request_prototype: Response template
        toolset: Available tools
        cited: Optional pre-extracted Citations for content
        reason_cited: Optional pre-extracted Citations for reasoning
        available_citations: Optional Citations container for fallback text extraction

    Returns:
        Response with citation annotations
    """
    response = request_prototype.model_copy()

    # IMPORTANT: Keep the original chunk for citation extraction
    original_chunk = chunk_combined

    # Convert ChatCompletionChunk to dictionary if needed
    if isinstance(chunk_combined, ChatCompletionChunk | ChatCompletion):
        chunk_combined = chunk_combined.model_dump()

    # Process the dictionary format
    choices = chunk_combined.get("choices")
    msg_id = chunk_combined.get("id")
    if not choices:
        return None
    assert len(choices) == 1
    choice = choices[0]
    chat_message = choice.get("delta") or choice.get("message")
    if not chat_message:
        return None

    # Initialize variables for response construction
    # response.output = []

    # Use provided citations or extract from chunk
    if cited is not None or reason_cited is not None:
        citations = {"content": [], "reasoning": []}
        # Convert Citations objects to annotation lists
        if cited:
            content_annotations = cited.to_annotations()
            citations["content"] = content_annotations
            # logger.bind(content_annotations=content_annotations).info("Content annotations")

        if reason_cited:
            reasoning_annotations = reason_cited.to_annotations()
            citations["reasoning"] = reasoning_annotations
    else:
        # Fallback to enhanced extraction with text parsing support
        citations = extract_citations_from_chunk_enhanced(
            original_chunk,
            include_reasoning=True,
            available_citations=available_citations,
        )

    # Process reasoning content if present in the delta
    reasoning_content = chat_message.get("reasoning_content")
    if reasoning_content:
        # Create a new reasoning item with the content
        reasoning_item = ResponseReasoningItem(
            id=reason_id_of(msg_id),
            type="reasoning",
            summary=[Summary(type="summary_text", text=reasoning_content)],
            status="in_progress",
        )
        # TODO: ResponseReasoningItem may need annotation support added
        # For now, reasoning citations are tracked but not included in response
        response.output.append(reasoning_item)

    # Process text content if present in the delta
    content = chat_message.get("content")
    if content:
        # Get content annotations from citations
        content_annotations = citations.get("content", [])

        # Create a new message with the text content
        message = ResponseOutputMessage(
            type="message",
            id=message_id_of(msg_id),
            status="in_progress",
            role="assistant",
            content=[],
        )
        # Add the text content WITH ANNOTATIONS
        message.content.append(
            ResponseOutputText(
                type="output_text",
                text=content,
                annotations=content_annotations,  # Now includes citations!
            )
        )
        # Add the message to the response output
        response.output.append(message)

    # Process tool calls if present in the delta
    tool_calls = chat_message.get("tool_calls") or []
    # Convert raw tool call dictionaries to ChoiceDeltaToolCall objects
    from langchain_core.output_parsers import JsonOutputParser
    from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
    from response._types.response_file_search_tool_call import (
        ResponseFileSearchToolCall,
    )
    from response._types.response_function_file_reader import ResponseFunctionFileReader
    from response._types.response_function_tool_call import ResponseFunctionToolCall
    from response._types.response_function_web_search import ResponseFunctionWebSearch

    tool_calls = [ChoiceDeltaToolCall(**tool_call) for tool_call in tool_calls]
    # Sort tool calls by their index to maintain order
    tool_calls = sorted(tool_calls, key=lambda x: x.index)
    # Create a JSON parser for parsing tool arguments
    json_parser = JsonOutputParser()

    # Process each tool call
    for _, tool_call in enumerate(tool_calls):
        tool_name = tool_call.function.name
        # Check if the tool exists in our toolset
        if tool_name in toolset:
            toolset[tool_name]
            # Special handling for CollectionAsRetriever tools (file search)
            # Check for either real CollectionAsRetriever or our mock with is_collection_retriever flag
            if tool_name == FILE_SEARCH:
                queries = []
                file_id = None
                try:
                    # Parse the tool arguments as JSON
                    arguments = json_parser.invoke(tool_call.function.arguments)
                    if arguments:
                        # Extract queries from the arguments
                        queries = arguments.get("queries", [])
                        # Convert doc_id to file_id
                        file_id = arguments.get("doc_id")
                except Exception:
                    # Continue with empty queries if parsing fails
                    pass

                # Create a file search tool call object
                file_search_tool_call = ResponseFileSearchToolCall(
                    id=tool_call.id,
                    queries=queries,
                    status="in_progress",  # Mark as in-progress
                    type=FILE_SEARCH_CALL,
                    file_id=file_id,
                )
                # Set private attribute after instance creation
                file_search_tool_call._native_tool_call = ResponseFunctionToolCall(
                    arguments=tool_call.function.arguments,
                    call_id=tool_call.id,
                    name=tool_call.function.name,
                    type="function_call",
                    id=tool_call.id,
                    status="in_progress",
                )
                # Add the file search tool call to the response output
                response.output.append(file_search_tool_call)
            # Handle document finder tool calls
            elif tool_name == DOCUMENT_FINDER:
                queries = []
                count = 10  # Default value
                try:
                    # Parse the tool arguments as JSON
                    arguments = json_parser.invoke(tool_call.function.arguments)
                    if arguments:
                        # Extract queries from the arguments
                        queries = arguments.get("queries", [])
                        # Extract count parameter
                        count = arguments.get("count", 10)
                except Exception:
                    # Continue with empty queries if parsing fails
                    pass

                # Import the ResponseDocumentFinderToolCall class
                from response._types.response_document_finder_tool_call import (
                    ResponseDocumentFinderToolCall,
                )

                # Create a document finder tool call object
                document_finder_tool_call = ResponseDocumentFinderToolCall(
                    id=tool_call.id,
                    queries=queries,
                    count=count,
                    status="in_progress",  # Mark as in-progress
                    type=DOCUMENT_FINDER_CALL,
                )
                # Set private attribute after instance creation
                document_finder_tool_call._native_tool_call = ResponseFunctionToolCall(
                    arguments=tool_call.function.arguments,
                    call_id=tool_call.id,
                    name=tool_call.function.name,
                    type="function_call",
                    id=tool_call.id,
                    status="in_progress",
                )

                # Add the document finder tool call to the response output
                response.output.append(document_finder_tool_call)
            # Handle web search tool calls
            elif tool_name in [WEB_SEARCH, "web_search_preview"]:
                try:
                    # Parse the tool arguments as JSON
                    arguments = json_parser.invoke(tool_call.function.arguments)

                    # Web search uses "queries" array, take first query
                    queries = arguments.get("queries") or arguments.get("query") or []
                    if isinstance(queries, str):
                        queries = [queries]
                except Exception:
                    logger.exception(f"Error parsing tool arguments:{tool_call.function.arguments}")
                    # Continue with empty query if parsing fails
                    queries = []

                # Create a web search tool call object using the existing ResponseFunctionWebSearch class
                web_search_tool_call = ResponseFunctionWebSearch(
                    id=tool_call.id,
                    status="in_progress",  # Mark as in-progress
                    type=WEB_SEARCH_CALL,
                    queries=queries,  # Add the query parameter
                )
                # Set private attribute to store the original tool call data
                web_search_tool_call._results = []
                # Store the original tool call data
                web_search_tool_call._native_tool_call = ResponseFunctionToolCall(
                    arguments=tool_call.function.arguments,
                    call_id=tool_call.id,
                    name=tool_call.function.name,
                    type="function_call",
                    id=tool_call.id,
                    status="in_progress",
                )
                # Add the web search tool call to the response output
                response.output.append(web_search_tool_call)
            elif tool_name == FILE_READER:
                # Parse the tool arguments as JSON
                arguments = json_parser.invoke(tool_call.function.arguments)
                if arguments:
                    # Extract doc_ids and query from the arguments
                    doc_ids = arguments.get("doc_ids", [])
                    queries = arguments.get("query") or arguments.get("queries") or []
                    if isinstance(queries, str):
                        queries = [queries]
                    file_reader_tool_call = ResponseFunctionFileReader(
                        id=tool_call.id,
                        status="in_progress",
                        type=FILE_READER_CALL,
                        doc_ids=doc_ids,
                        query=queries[0] if queries else "",
                    )

                    # Create a file reader tool call object
                    file_reader_tool_call._native_tool_call = ResponseFunctionToolCall(
                        arguments=tool_call.function.arguments,
                        call_id=tool_call.id,
                        name=tool_call.function.name,
                        type="function_call",
                        id=tool_call.id,
                        status="in_progress",
                    )
                    response.output.append(file_reader_tool_call)

    # Mark all previous message outputs as completed when a tool call is processed
    # This ensures only the latest message is marked as in-progress
    for output in response.output[:-1]:
        if output.type == "reasoning":
            # Check if there are reasoning citations to append
            reasoning_citations = citations.get("reasoning", [])
            if reasoning_citations and output.summary:
                # Get citation display text from reasoning citations
                citation_display = ""
                for idx, citation in enumerate(reasoning_citations, start=1):
                    if hasattr(citation, "get_display_text"):
                        citation_display += f"{idx}. {citation.get_display_text()}" + "\n"

                if citation_display and output.summary:
                    last_summary = output.summary[-1]
                    # Check if citations haven't been appended already (avoid duplication)
                    if "### 参考" not in last_summary.text:
                        # Append citations to reasoning content
                        last_summary.text += f"\n\n### 参考\n{citation_display.strip()}"

            output.status = "completed"
        elif output.type == "message":
            output.status = "completed"

    return response


# Example usage showing the integration
def example_usage():
    """Demonstrate how the enhanced function works with bi-patcher."""

    # Assume we have a stream that's been processed by bi-patcher
    # The chunks have _cited and _reason_cited attributes

    from citation.bi_patcher import patch

    async def process_with_citations(llm_stream, citations, prototype, toolset):
        # Apply bi-patcher to add citation tracking
        async for chunk in patch(llm_stream, citations):
            # chunk now has _cited and _reason_cited attributes

            # Convert to response with citations
            response = convert_to_response(chunk, prototype, toolset)

            if response:
                # Response now includes proper citation annotations
                yield response
