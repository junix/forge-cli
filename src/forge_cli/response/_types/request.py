"""Request parameters for generating a response."""

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass  # All message types previously here were removed
from pydantic import Field, model_validator

from ._models import BaseModel
from .file_search_tool import FileSearchTool
from .input_message import InputMessage
from .list_documents_tool import ListDocumentsTool
from .response_file_search_tool_call import ResponseFileSearchToolCall
from .response_format import ResponseFormat
from .response_function_web_search import ResponseFunctionWebSearch
from .response_input_message_item import ResponseInputMessageItem
from .response_output_message import ResponseOutputMessage
from .response_reasoning_item import ResponseReasoningItem
from .response_text_config_param import ResponseTextConfigParam
from .tool import Tool
from .tool_choice_function_param import ToolChoiceFunctionParam
from .tool_choice_options import ToolChoiceOptions
from .tool_choice_types_param import ToolChoiceTypesParam
from .web_search_tool import WebSearchTool

# Define hosted tool types that are not supported by OpenAI's tool_choice
HOSTED_TOOL_TYPES = {
    "file_search",
    "web_search",
    "web_search_preview",
    "computer_use_preview",
    "code_interpreter",
    "mcp",
    "image_generation",
    "web_search_preview_2025_03_11",
    "list_documents",
}


class Request(BaseModel):
    """Request parameters for generating a response."""

    model: str = Field(..., description="Model ID used to generate the response")
    input: (
        str
        | list[
            InputMessage
            | ResponseInputMessageItem
            | ResponseOutputMessage
            | ResponseFileSearchToolCall
            | ResponseFunctionWebSearch
            | ResponseReasoningItem
        ]
    ) = Field(
        ...,
        description="Input text or array of messages to process. String input is treated as a user message",
    )
    effort: Literal["low", "medium", "high", "dev"] = Field(
        default="low", description="The effort level for the response generation"
    )

    # Optional parameters
    instructions: str | None = Field(
        None,
        description="System instructions for the model, inserted at the beginning of the context",
    )
    tools: list[Tool] | None = Field(None, description="Tools the model can use during response generation")
    tool_choice: ToolChoiceOptions | ToolChoiceTypesParam | ToolChoiceFunctionParam | None = Field(
        "auto",
        description="Controls tool usage. Can be 'auto', 'none', or an object specifying a function",
    )
    temperature: float | None = Field(
        1.0,
        description="Sampling temperature between 0 and 2. Higher values make output more random",
        ge=0.0,
        le=2.0,
    )
    top_p: float | None = Field(1.0, description="Nucleus sampling parameter between 0 and 1", gt=0.0, le=1.0)
    max_output_tokens: int | None = Field(None, description="Maximum number of tokens to generate")
    previous_response_id: str | None = Field(
        None,
        description="ID of a previous response to continue from, enabling conversation continuity",
    )
    reasoning_effort: str | None = Field(
        None,
        description="Amount of reasoning effort the model should expend, if supported by the model",
    )

    text: ResponseTextConfigParam | None = Field(None, description="Additional text format specifications")
    response_format: ResponseFormat | None = Field(
        None, description="Specification for the response format, e.g., for JSON output"
    )
    truncation: str | None = Field(
        "disabled",
        description="Truncation strategy when context length is exceeded, either 'disabled' or 'auto'",
    )
    top_logprobs: int | None = Field(
        None,
        description="Number of most likely tokens to return at each token position, with their log probabilities",
    )
    user: str | None = Field(
        None,
        description="A unique identifier representing your end-user for monitoring and abuse prevention",
    )
    metadata: dict[str, str] | None = Field(None, description="Additional metadata to include with the response")
    parallel_tool_calls: bool | None = Field(
        None, description="Whether to enable parallel tool calls for this response"
    )
    store: bool | None = Field(
        True,
        description="Whether to store this response for later retrieval. Defaults to True for conversation continuity",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_input(cls, data):
        """Validates that either input or messages are provided, but not both."""
        if isinstance(data, dict):
            input_value = data.get("input")
            if input_value is None:
                raise ValueError("Either 'input' or an array of messages must be provided")
        return data

    def seek_file_search_tools(self) -> list[FileSearchTool]:
        """
        Extracts vectorstore IDs from file_search tools in the request.

        Returns:
            List[str]: A list of vectorstore IDs if file_search tools with
                       vector_store_ids are present, otherwise an empty list.
        """
        if not self.tools:
            return []
        return [tool for tool in self.tools if tool.type == "file_search"]

    def web_search_tools(self) -> list[WebSearchTool]:
        """
        Extracts web search tools from the request.

        Returns:
            List[WebSearchTool]: A list of web search tools if present, otherwise an empty list.
        """
        if not self.tools:
            return []

        tools = []
        for tool in self.tools:
            if isinstance(tool, WebSearchTool) and tool.type in [
                "web_search",
                "web_search_preview",
            ]:
                tools.append(tool)

        return tools

    def seek_list_documents_tools(self) -> list[ListDocumentsTool]:
        """
        Extracts list documents tools from the request.

        Returns:
            List[ListDocumentsTool]: A list of list documents tools if present, otherwise an empty list.
        """
        if not self.tools:
            return []
        return [tool for tool in self.tools if tool.type == "list_documents"]

    def create_partial_response(
        self,
        *,
        response_id: str,
        created_at: float,
        status: str = "in_progress",
        output: list | None = None,
        usage: dict | None = None,
        effort: str = "low",
        reasoning: dict | None = None,
        **overrides,
    ) -> "Response":
        """Create a Response object using fields from this Request.

        This method provides a clean way to create Response objects by automatically
        extracting relevant fields from the Request and allowing specific overrides.
        This replaces the manual pattern of extracting fields in error response creation.

        Args:
            response_id: Unique identifier for the response
            created_at: Unix timestamp when the response was created
            status: Status of the response (default: "in_progress")
            output: List of output items (default: empty list)
            usage: Token usage information (default: basic usage structure)
            effort: Response generation effort level (default: "low")
            reasoning: Reasoning metadata (default: basic reasoning structure)
            **overrides: Additional fields to override or add to the response

        Returns:
            Response: A new Response object with fields populated from this Request

        Example:
            ```python
            request = Request(model="gpt-4o", input="Hello", temperature=0.7)
            response = request.create_partial_response(
                response_id="resp_123",
                created_at=time.time(),
                status="completed",
                output=[message],
            )
            ```
        """
        # Import Response here to avoid circular imports
        from .response import Response
        from .response_usage import InputTokensDetails, OutputTokensDetails, ResponseUsage

        # Set default values
        if output is None:
            output = []
        if usage is None:
            usage = ResponseUsage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                input_tokens_details=InputTokensDetails(cached_tokens=0),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
            )
        if reasoning is None:
            reasoning = {"effort": effort, "summary": None}

        # Convert tools to dict format
        tools_dict = [tool.model_dump() for tool in self.tools or []]

        # Extract tool_choice as string or dict for Response compatibility
        tool_choice_value = self.tool_choice
        if isinstance(tool_choice_value, str):
            tool_choice_final = tool_choice_value
        else:
            tool_choice_final = "auto"

        # Build the response data
        response_data = {
            "id": response_id,
            "object": "response",
            "created_at": created_at,
            "status": status,
            "error": None,
            "incomplete_details": None,
            # Extract from request with None fallbacks
            "instructions": self.instructions,
            "max_output_tokens": self.max_output_tokens,
            "model": self.model,
            "effort": effort,
            "output": output,
            "parallel_tool_calls": self.parallel_tool_calls or False,
            "previous_response_id": self.previous_response_id,
            "reasoning": reasoning,
            "temperature": self.temperature,
            "text": {"format": {"type": "text"}},
            "tool_choice": tool_choice_final,
            "tools": tools_dict,
            "top_p": self.top_p,
            "truncation": self.truncation,
            "usage": usage,
            "user": self.user,
            "metadata": self.metadata or {},
            "top_logprobs": self.top_logprobs,
        }

        # Apply any overrides
        response_data.update(overrides)

        return Response(**response_data)
