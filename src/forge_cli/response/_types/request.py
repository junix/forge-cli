"""Request parameters for generating a response."""

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    # Import message types for as_openai_chat_request method
    from message import (
        AssistantMessage,
        ChatCompletionRequest,
        ChatMessage,
        MessageContent,
        SystemMessage,
        ToolCall,
        ToolMessage,
        UserMessage,
    )
    from message._types.tool import Tool as MessageTool
from pydantic import Field, model_validator

from ..chat_input import fold_chat_messages, verify_chat_messages
from ._models import BaseModel
from .document_finder_tool import DocumentFinderTool
from .file_search_tool import FileSearchTool
from .input_message import InputMessage
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
    "document_finder",
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

    def input_as_typed_messages(self) -> list["ChatMessage"]:
        """
        Process the input data into typed ChatMessage objects.

        Returns:
            List[ChatMessage]: A list of typed chat messages.
        """
        # Import locally to avoid circular imports
        from message import UserMessage

        input_data = self.input

        if isinstance(input_data, str):
            # Convert simple string to a user message
            return [UserMessage(content=input_data)]

        elif isinstance(input_data, list):
            # Process list of input messages
            typed_messages = []
            for msg in input_data:
                typed_msg = self._convert_input_to_typed_message(msg)
                if typed_msg:
                    typed_messages.append(typed_msg)

            # Use ChatHistory for folding
            # Import locally to avoid circular imports
            from message import ChatHistory

            chat_history = ChatHistory(messages=typed_messages)
            folded_history = chat_history.fold_messages()
            return folded_history.messages

        # Default case - should not happen due to validator
        return []

    def _convert_input_to_typed_message(self, msg: object) -> "ChatMessage | None":
        """Convert various input message types to typed ChatMessage objects."""
        # Import locally to avoid circular imports
        from message import AssistantMessage, SystemMessage, ToolMessage, UserMessage

        if isinstance(msg, dict):
            # Already a dictionary, convert to typed
            if "role" in msg and "content" in msg:
                return self._dict_to_typed_message(msg)
            return None

        # If it's already a ChatMessage, return as-is
        if isinstance(msg, UserMessage | AssistantMessage | SystemMessage | ToolMessage):
            return msg

        # Handle tool calls and tool call results
        msg_type = getattr(msg, "type", None)

        # Handle output text (convert to assistant message)
        if msg_type == "output_text":
            return AssistantMessage(content=getattr(msg, "text", ""))

        # Handle function tool calls
        if msg_type in [
            "function_call",
            "code_interpreter_call",
            "computer_call",
            "web_search_call",
            "file_search_call",
            "document_finder_call",
        ]:
            # Create a tool call message
            if hasattr(msg, "to_chat_tool_call"):
                tool_call = getattr(msg, "to_chat_tool_call")()
                return AssistantMessage(content=None, tool_calls=[tool_call])
            return None

        # Handle tool call results/outputs
        if msg_type in ["function_call_output"]:
            return ToolMessage(content=getattr(msg, "output", ""), tool_call_id=str(getattr(msg, "call_id", "unknown")))

        # Handle Pydantic objects with role and content
        if hasattr(msg, "content") and hasattr(msg, "role"):
            return self._pydantic_msg_to_typed(msg)

        return None

    def _dict_to_typed_message(self, msg_dict: dict) -> "ChatMessage | None":
        """Convert a message dict to typed ChatMessage."""
        role = msg_dict.get("role")

        if role == "system":
            return self._create_system_message(msg_dict)
        elif role == "user":
            return self._create_user_message(msg_dict)
        elif role == "assistant":
            return self._create_assistant_message(msg_dict)
        elif role == "tool":
            return self._create_tool_message(msg_dict)
        else:
            return None

    def _pydantic_msg_to_typed(self, msg: object) -> "ChatMessage | None":
        """Convert Pydantic message object to typed ChatMessage."""
        # Import locally to avoid circular imports
        from message import AssistantMessage, SystemMessage, UserMessage

        role = getattr(msg, "role", None)
        content_val = getattr(msg, "content", None)

        if role == "user":
            if isinstance(content_val, str):
                return UserMessage(content=content_val, name=getattr(msg, "name", None))
            else:
                # List of content objects
                if isinstance(content_val, list):
                    typed_content = self._convert_pydantic_content_list(content_val)
                    return UserMessage(content=typed_content, name=getattr(msg, "name", None))
                else:
                    return UserMessage(content="", name=getattr(msg, "name", None))

        elif role == "assistant":
            if isinstance(content_val, str):
                return AssistantMessage(content=content_val, name=getattr(msg, "name", None))
            else:
                # Handle complex content
                return AssistantMessage(content="", name=getattr(msg, "name", None))

        elif role == "system":
            return SystemMessage(content=str(content_val), name=getattr(msg, "name", None))

        return None

    def _convert_pydantic_content_list(self, content_val: list[object]) -> list["MessageContent"]:
        """Convert Pydantic content list to typed MessageContent objects."""
        # Import locally to avoid circular imports
        from message import FileContent, ImageContent, ImageUrlContent, TextContent

        typed_content: list[MessageContent] = []
        for content_item in content_val:
            content_type = getattr(content_item, "type", None)
            if content_type == "input_text":
                typed_content.append(TextContent(text=getattr(content_item, "text", "")))
            elif content_type == "input_image":
                typed_content.append(
                    ImageContent(image_url=ImageUrlContent(url=getattr(content_item, "image_url", "")))
                )
            elif content_type == "input_file":
                file_id = getattr(content_item, "file_id", None)
                if file_id is None:
                    raise ValueError("File ID is required for input_file")
                # Work around mypy issue with FileContent
                fc = FileContent()
                fc.file_id = file_id
                typed_content.append(fc)
            elif content_type == "output_text":
                typed_content.append(TextContent(text=getattr(content_item, "text", "")))
        return typed_content

    def _input_as_dict_messages(self) -> list[dict]:
        """Internal method that returns dict messages for backward compatibility."""
        input_data = self.input

        if isinstance(input_data, str):
            # Convert simple string to a user message
            return [{"role": "user", "content": input_data}]

        elif isinstance(input_data, list):
            # Process list of input messages
            processed_messages = []
            for msg in input_data:
                if isinstance(msg, dict):
                    # Already a dictionary, just use it directly
                    if "role" in msg and "content" in msg:
                        processed_messages.append(msg)
                        continue

                # Handle tool calls and tool call results
                msg_type = getattr(msg, "type", None)

                # Handle output text (convert to assistant message)
                if msg_type == "output_text":
                    # Convert ResponseOutputText to an assistant message
                    assistant_msg = {
                        "role": "assistant",
                        "content": getattr(msg, "text", ""),
                    }
                    processed_messages.append(assistant_msg)
                    continue

                # Handle function tool calls
                if msg_type in [
                    "function_call",
                    "code_interpreter_call",
                    "computer_call",
                    "web_search_call",
                    "file_search_call",
                    "document_finder_call",
                ]:
                    # Create a tool call message for regular functions
                    tool_call = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [getattr(msg, "to_chat_tool_call")().model_dump()],
                    }
                    processed_messages.append(tool_call)
                    continue

                # Handle tool call results/outputs
                if msg_type in ["function_call_output"]:
                    # Create a tool result message
                    tool_result = {
                        "role": "tool",
                        "content": getattr(msg, "output", ""),
                        "tool_call_id": str(getattr(msg, "call_id", "unknown")),
                    }
                    processed_messages.append(tool_result)
                    continue

                # Handle Pydantic objects with role and content
                if hasattr(msg, "content") and hasattr(msg, "role"):
                    content_val = msg.content

                    if isinstance(content_val, str):
                        # Simple string content
                        processed_messages.append(
                            {
                                "role": msg.role,
                                "content": content_val,
                                "name": getattr(msg, "name", None),
                            }
                        )
                    else:
                        # List of content objects (text and images)
                        processed_content = []
                        for content_item in content_val:
                            content_type = getattr(content_item, "type", None)
                            if content_type == "input_text":
                                processed_content.append({"type": "text", "text": getattr(content_item, "text", "")})
                            elif content_type == "input_image":
                                processed_content.append(
                                    {
                                        "type": "image",
                                        "image_url": {"url": getattr(content_item, "image_url", "")},
                                    }
                                )
                            elif content_type == "input_file":
                                file_id = getattr(content_item, "file_id", None)
                                if file_id is None:
                                    raise ValueError("File ID is required for input_file")
                                processed_content.append({"type": "file", "file_id": file_id})
                            elif content_type == "output_text":
                                # Handle output_text content type
                                processed_content.append({"type": "text", "text": getattr(content_item, "text", "")})
                            else:
                                raise ValueError(f"Unsupported content type: {content_type}")

                        processed_messages.append(
                            {
                                "role": msg.role,
                                "content": processed_content,
                                "name": getattr(msg, "name", None),
                            }
                        )

            messages = fold_chat_messages(processed_messages)
            verify_chat_messages(messages)
            return messages

        # Default case - should not happen due to validator
        return []

    def pack_as_typed_messages(self) -> list["ChatMessage"]:
        """
        Process the input data and pack it with instructions into typed ChatMessage objects.

        This method processes the input, adds system instructions if provided, and returns
        the complete list of typed messages ready to be sent to the model service.

        Returns:
            List[ChatMessage]: A list of typed chat messages, including system instructions if provided.
        """
        from message import SystemMessage

        # Get the processed input messages as typed messages
        processed_messages = self.input_as_typed_messages()

        # Add instructions as system message if provided
        if self.instructions:
            system_msg = SystemMessage(content=self.instructions)
            processed_messages.insert(0, system_msg)

        return processed_messages

    def as_openai_chat_request(self, with_internal_tool: bool = False, **kwargs) -> "ChatCompletionRequest":
        """
        Convert the Request to a ChatCompletionRequest object with proper typed messages.

        This method creates a fully typed ChatCompletionRequest object,
        converting all dict-based messages to proper message objects (UserMessage,
        AssistantMessage, etc.) and dict-based content to proper content objects
        (TextContent, ImageContent, etc.).

        Features:
        - Returns ChatCompletionRequest object with full type safety
        - Messages are typed ChatMessage objects instead of dicts
        - Content is typed content objects (TextContent, ImageContent, etc.)
        - Provides full type safety and IDE support
        - Compatible with message module's ChatHistory and other tools

        Args:
            with_internal_tool: If True, includes internal/hosted tools (file_search, web_search, etc.)
                               in the tools list. If False (default), only function tools are included.
            **kwargs: Additional parameters to include in the request or override existing ones.
                     These take precedence over the original Request parameters.

        Returns:
            ChatCompletionRequest: A fully typed ChatCompletionRequest object ready for
                                  OpenAI API usage or message processing.

        Raises:
            ImportError: If message types are not available.
            ValueError: If message conversion fails.

        Example:
            ```python
            request = Request(
                model="gpt-4o",
                input="Hello world",
                temperature=0.7
            )

            # Get typed ChatCompletionRequest (function tools only)
            chat_request = request.as_openai_chat_request(stream=True)

            # Include all tools including internal ones
            chat_request_all = request.as_openai_chat_request(with_internal_tool=True, stream=True)

            # Use with message tools
            chat_history = ChatHistory(messages=chat_request.messages)
            token_count = chat_request.estimate_tokens()
            api_dict = chat_request.to_api_dict()
            ```
        """

        # Get typed messages directly
        typed_messages = self.pack_as_typed_messages()

        # Build request parameters
        request_params: dict[str, object] = {
            "model": self.model,
            "messages": typed_messages,
        }

        # Map optional parameters
        if self.temperature is not None:
            request_params["temperature"] = self.temperature

        if self.top_p is not None:
            request_params["top_p"] = self.top_p

        if self.max_output_tokens is not None:
            request_params["max_tokens"] = self.max_output_tokens

        if self.user is not None:
            request_params["user"] = self.user

        # Handle logprobs and top_logprobs
        if self.top_logprobs is not None:
            request_params["logprobs"] = True
            request_params["top_logprobs"] = self.top_logprobs

        # Handle tool_choice (reuse existing conversion logic)
        if self.tool_choice is not None:
            request_params["tool_choice"] = self._convert_tool_choice_for_openai()

        # Handle tools (convert to OpenAI-compatible format)
        if self.tools is not None:
            converted_tools = self._convert_tools_for_openai(with_internal_tool=with_internal_tool)
            if converted_tools:
                request_params["tools"] = converted_tools

        # Handle response_format
        if self.response_format is not None:
            response_format = self.response_format.model_dump(exclude_none=True)
            if response_format:  # Only add if not empty
                request_params["response_format"] = response_format

        # Override with any additional kwargs
        request_params.update(kwargs)

        # Import locally to avoid circular imports
        from message import ChatCompletionRequest

        return ChatCompletionRequest(**request_params)

    def _create_system_message(self, msg_dict: dict) -> "SystemMessage":
        """Create SystemMessage from dict."""
        # Import locally to avoid circular imports
        from message._types import SystemMessage

        content = msg_dict.get("content")

        # Handle string content
        if isinstance(content, str):
            return SystemMessage(content=content, name=msg_dict.get("name"))

        # Handle list content (multimodal) - convert to string
        elif isinstance(content, list):
            # System messages no longer support list content, so we need to convert to string
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
                # Skip non-text content items for system messages

            combined_text = " ".join(text_parts).strip()
            return SystemMessage(content=combined_text if combined_text else "", name=msg_dict.get("name"))

        else:
            # Fallback to empty string
            return SystemMessage(content="", name=msg_dict.get("name"))

    def _create_user_message(self, msg_dict: dict) -> "UserMessage":
        """Create UserMessage from dict."""
        # Import locally to avoid circular imports
        from message import UserMessage

        content = msg_dict.get("content")

        # Handle string content
        if isinstance(content, str):
            return UserMessage(content=content, name=msg_dict.get("name"))

        # Handle list content (multimodal)
        elif isinstance(content, list):
            typed_content = self._convert_content_list(content)
            return UserMessage(content=typed_content, name=msg_dict.get("name"))

        else:
            # Fallback to empty string
            return UserMessage(content="", name=msg_dict.get("name"))

    def _create_assistant_message(self, msg_dict: dict) -> "AssistantMessage":
        """Create AssistantMessage from dict."""
        # Import locally to avoid circular imports
        from message import AssistantMessage

        content = msg_dict.get("content")
        tool_calls_data = msg_dict.get("tool_calls")

        # Handle content conversion
        processed_content = content
        if isinstance(content, list):
            # Convert list content to typed MessageContent objects
            processed_content = self._convert_content_list(content)
        elif content is None:
            # Keep None as is for tool-only messages
            processed_content = None
        # String content passes through as-is

        # Convert tool calls if present
        tool_calls = None
        if tool_calls_data:
            tool_calls = []
            for tc_dict in tool_calls_data:
                tool_call = self._convert_tool_call_dict(tc_dict)
                tool_calls.append(tool_call)

        return AssistantMessage(content=processed_content, tool_calls=tool_calls, name=msg_dict.get("name"))

    def _create_tool_message(self, msg_dict: dict) -> "ToolMessage":
        """Create ToolMessage from dict."""
        # Import locally to avoid circular imports
        from message import ToolMessage

        return ToolMessage(
            content=msg_dict.get("content", ""), tool_call_id=str(msg_dict.get("tool_call_id", "unknown"))
        )

    def _convert_content_list(self, content_list: list[dict]) -> list["MessageContent"]:
        """Convert list of content dicts to typed content objects."""
        # Import locally to avoid circular imports
        from message import AudioContent, FileContent, ImageContent, ImageUrlContent, RefusalContent, TextContent

        typed_content: list[MessageContent] = []

        for content_item in content_list:
            content_type = content_item.get("type")

            if content_type == "text":
                typed_content.append(TextContent(text=content_item.get("text", "")))

            elif content_type == "image":
                image_url_data = content_item.get("image_url", {})
                image_url = ImageUrlContent(
                    url=image_url_data.get("url", ""), detail=image_url_data.get("detail", "auto")
                )
                typed_content.append(ImageContent(image_url=image_url))

            elif content_type == "file":
                # Work around mypy issue with FileContent
                fc = FileContent()
                fc.file_id = content_item.get("file_id")
                fc.name = content_item.get("name")
                fc.mime_type = content_item.get("mime_type")
                fc.size = content_item.get("size")
                typed_content.append(fc)

            elif content_type == "input_audio":
                typed_content.append(AudioContent(input_audio=content_item.get("input_audio", {})))

            elif content_type == "refusal":
                typed_content.append(RefusalContent(refusal=content_item.get("refusal", "")))

            else:
                # Fallback: treat as text
                text_value = content_item.get("text", str(content_item))
                typed_content.append(TextContent(text=text_value))

        return typed_content

    def _convert_tool_call_dict(self, tc_dict: dict) -> "ToolCall":
        """Convert tool call dict to ToolCall object."""
        # Import locally to avoid circular imports
        from message import FunctionCall, ToolCall

        function_data = tc_dict.get("function", {})

        function_call = FunctionCall(name=function_data.get("name", ""), arguments=function_data.get("arguments", "{}"))

        return ToolCall(id=tc_dict.get("id", ""), function=function_call)

    def _convert_tool_choice_for_openai(self) -> str | dict[str, object]:
        """Convert tool_choice to OpenAI-compatible format (reuses existing logic)."""
        if isinstance(self.tool_choice, str):
            return self.tool_choice
        elif isinstance(self.tool_choice, dict):
            tool_type = self.tool_choice.get("type")

            if tool_type == "function":
                function_name = self.tool_choice.get("name")
                if function_name:
                    return {"type": "function", "function": {"name": function_name}}
                else:
                    return "auto"
            elif tool_type in HOSTED_TOOL_TYPES:
                return "auto"
            else:
                return "auto"
        else:
            return "auto"

    def _convert_tools_for_openai(self, with_internal_tool: bool = False) -> list["MessageTool"] | None:
        """Convert response tools to OpenAI-compatible tool format.

        This method converts various tool types (FileSearchTool, WebSearchTool, etc.)
        to the OpenAI function tool format which requires name, description, and parameters.

        Args:
            with_internal_tool: If True, includes internal/hosted tools in the output.
                               If False, only function tools are included.

        Returns:
            List of tool dictionaries in OpenAI format, or None if no compatible tools.
        """
        if not self.tools:
            return None
        return [tool for tool in self.tools if with_internal_tool or tool.type not in HOSTED_TOOL_TYPES]

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

    def seek_document_finder_tools(self) -> list[DocumentFinderTool]:
        """
        Extracts document finder tools from the request.

        Returns:
            List[DocumentFinderTool]: A list of document finder tools if present, otherwise an empty list.
        """
        if not self.tools:
            return []
        return [tool for tool in self.tools if tool.type == "document_finder"]

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
