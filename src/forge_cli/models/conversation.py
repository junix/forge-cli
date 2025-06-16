"""Conversation state management for multi-turn chat mode."""

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, NewType, Protocol, overload

# Import proper types from response system
from ..response._types.response_input_message_item import ResponseInputMessageItem
from ..response._types.response_usage import InputTokensDetails, OutputTokensDetails, ResponseUsage
from ..response._types.tool import Tool
from ..response.type_guards import (
    is_file_search_tool,
    is_input_text,
    is_list_documents_tool,
)

if TYPE_CHECKING:
    from ..config import SearchConfig
    from ..response._types import Request, Response
    from ..stream.handler_typed import StreamState

# Type aliases for clarity
type MessageRole = Literal["user", "system", "developer"]
type ToolType = Literal[
    "file_search", "web_search", "function", "computer_use_preview", "list_documents", "file_reader"
]

# Domain-specific types
SessionId = NewType("SessionId", str)
MessageId = NewType("MessageId", str)

# Constants
DEFAULT_MODEL: Final[str] = "qwen-max-latest"
TOKENS_PER_CHAR: Final[int] = 4  # Heuristic for token estimation
MIN_MESSAGES_TO_KEEP: Final[int] = 2


class ConversationPersistence(Protocol):
    """Protocol for conversation persistence strategies."""

    def save(self, state: "ConversationState", path: Path) -> None:
        """Save conversation state to storage."""
        ...

    def load(self, path: Path) -> "ConversationState":
        """Load conversation state from storage."""
        ...


@dataclass
class ConversationState:
    """Manages the state of a multi-turn conversation using typed API."""

    # Use proper typed messages instead of custom Message class
    messages: list[ResponseInputMessageItem] = field(default_factory=list)
    session_id: SessionId = field(default_factory=lambda: SessionId(f"session_{uuid.uuid4().hex[:12]}"))
    created_at: float = field(default_factory=time.time)
    model: str = DEFAULT_MODEL
    tools: list[Tool] = field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)
    # Use proper ResponseUsage instead of manual tracking
    usage: ResponseUsage | None = None
    used_vector_store_ids: set[str] = field(default_factory=set)
    # Track files accessed during the session
    accessed_files: set[str] = field(default_factory=set)
    # Track conversation turns
    turn_count: int = 0

    # Conversation-specific tool settings that can be changed during chat
    web_search_enabled: bool = False
    file_search_enabled: bool = False
    current_vector_store_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize used_vector_store_ids from tools if not set."""
        if not self.used_vector_store_ids and self.tools:
            # Extract vector store IDs from file search and list documents tools
            for tool in self.tools:
                if is_file_search_tool(tool):
                    self.used_vector_store_ids.update(tool.vector_store_ids)
                elif is_list_documents_tool(tool):
                    self.used_vector_store_ids.update(tool.vector_store_ids)

        # Initialize current_vector_store_ids from used_vector_store_ids if empty
        if not self.current_vector_store_ids and self.used_vector_store_ids:
            self.current_vector_store_ids = list(self.used_vector_store_ids)

    def add_message(self, message: ResponseInputMessageItem) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)

    def add_user_message(self, content: str) -> ResponseInputMessageItem:
        """Add a user message using proper typed API."""
        from ..response._types.response_input_text import ResponseInputText

        message = ResponseInputMessageItem(
            id=f"user_{uuid.uuid4().hex[:8]}",
            role="user",
            content=[ResponseInputText(type="input_text", text=content)],
        )
        self.add_message(message)
        return message

    def add_assistant_message(self, content: str, assistant_id: str | None = None) -> ResponseInputMessageItem:
        """Add an assistant message using proper typed API."""
        # Note: Assistant messages need proper handling since they don't fit the input message format
        # This might need adjustment based on how assistant messages are actually handled
        # For now, creating a compatible structure using system role
        from ..response._types.response_input_text import ResponseInputText

        message = ResponseInputMessageItem(
            id=assistant_id or f"assistant_{uuid.uuid4().hex[:8]}",
            role="system",  # Using system role as assistant isn't in the enum
            content=[ResponseInputText(type="input_text", text=content)],
        )
        self.add_message(message)
        return message

    def to_api_format(self) -> list[dict[str, str]]:
        """Convert messages to API format (dict with role and content)."""
        api_messages = []
        for msg in self.messages:
            # Extract text content from ResponseInputText objects
            content_parts = []
            for content_item in msg.content:
                if is_input_text(content_item):
                    # Type guard ensures content_item is ResponseInputText
                    content_parts.append(content_item.text)

            content_str = " ".join(content_parts)

            api_messages.append(
                {
                    "role": msg.role,
                    "content": content_str,
                }
            )

        return api_messages

    def clear(self) -> None:
        """Clear conversation history but keep configuration."""
        self.messages.clear()

    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)

    @overload
    def get_last_n_messages(self, n: Literal[1]) -> ResponseInputMessageItem | None: ...

    @overload
    def get_last_n_messages(self, n: int) -> list[ResponseInputMessageItem]: ...

    def get_last_n_messages(self, n: int) -> ResponseInputMessageItem | None | list[ResponseInputMessageItem]:
        """Get the last n messages."""
        if n == 1:
            return self.messages[-1] if self.messages else None
        return self.messages[-n:] if n > 0 else []

    def add_token_usage(self, usage: ResponseUsage) -> None:
        """Add token usage using proper ResponseUsage type."""
        if self.usage is None:
            self.usage = usage
        else:
            self.usage += usage  # Uses built-in __add__ method

    def get_token_usage(self) -> ResponseUsage | None:
        """Get current token usage."""
        return self.usage

    def reset_token_usage(self) -> None:
        """Reset token usage."""
        self.usage = None

    def add_accessed_file(self, file_path: str) -> None:
        """Add a file to the accessed files set."""
        if file_path:
            self.accessed_files.add(file_path)

    def add_accessed_files(self, file_paths: list[str]) -> None:
        """Add multiple files to the accessed files set."""
        for file_path in file_paths:
            self.add_accessed_file(file_path)

    def get_accessed_files(self) -> list[str]:
        """Get sorted list of accessed files."""
        return sorted(self.accessed_files)

    def increment_turn_count(self) -> None:
        """Increment the conversation turn counter."""
        self.turn_count += 1

    def enable_web_search(self) -> None:
        """Enable web search for this conversation."""
        self.web_search_enabled = True

    def disable_web_search(self) -> None:
        """Disable web search for this conversation."""
        self.web_search_enabled = False

    def enable_file_search(self) -> None:
        """Enable file search for this conversation."""
        self.file_search_enabled = True

    def disable_file_search(self) -> None:
        """Disable file search for this conversation."""
        self.file_search_enabled = False

    def set_vector_store_ids(self, vector_store_ids: list[str]) -> None:
        """Set the vector store IDs for file search in this conversation.

        Args:
            vector_store_ids: List of vector store IDs to use for file search
        """
        self.current_vector_store_ids = vector_store_ids.copy()
        # Also update the used_vector_store_ids set
        self.used_vector_store_ids.update(vector_store_ids)

    def get_current_vector_store_ids(self) -> list[str]:
        """Get the current vector store IDs for this conversation.

        Returns:
            List of current vector store IDs
        """
        return self.current_vector_store_ids.copy()

    def is_web_search_enabled(self) -> bool:
        """Check if web search is enabled for this conversation."""
        return self.web_search_enabled

    def is_file_search_enabled(self) -> bool:
        """Check if file search is enabled for this conversation."""
        return self.file_search_enabled

    def update_stream_state(self, state: "StreamState") -> None:
        """Update conversation state from stream state.

        This method transfers relevant information from a StreamState object
        to the ConversationState, including:
        - Token usage statistics
        - Accessed files
        - Vector store IDs
        - Model information

        Args:
            state: StreamState object from stream processing
        """
        # Import here to avoid circular imports

        # Handle usage information from response
        if state.response and state.response.usage:
            self.add_token_usage(state.response.usage)

        # Handle accessed files - extract from response
        if state.response:
            accessed_files = self._extract_accessed_files_from_response(state.response)
            if accessed_files:
                self.add_accessed_files(accessed_files)

        # Handle vector store IDs
        vector_store_ids = state.get_vector_store_ids()
        if vector_store_ids:
            self.used_vector_store_ids.update(vector_store_ids)

        # Handle model information from response
        if state.response and state.response.model:
            # Only update if we don't have a model set or if it's different
            if not self.model or self.model != state.response.model:
                self.model = state.response.model

        # Add assistant message from response
        if state.response:
            assistant_text = state.response.output_text
            if assistant_text:
                self.add_assistant_message(assistant_text)
                # Increment turn count when we successfully add an assistant message
                self.increment_turn_count()

    def _extract_accessed_files_from_response(self, response: "Response") -> list[str]:
        """Extract accessed files from Response object using type guards."""
        from ..response.type_guards import get_tool_results, is_file_search_call

        file_mapping = {}
        for item in response.output:
            if is_file_search_call(item):
                results = get_tool_results(item)
                for result in results:
                    file_id = getattr(result, "file_id", None)
                    filename = getattr(result, "filename", None)
                    if file_id and filename:
                        file_mapping[file_id] = filename

        return list(file_mapping.values())

    def save(self, path: Path) -> None:
        """Save conversation to a JSON file."""
        data = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "model": self.model,
            "tools": [tool.model_dump() for tool in self.tools],
            "metadata": self.metadata,
            "usage": self.usage.model_dump() if self.usage else None,
            "messages": [msg.model_dump() for msg in self.messages],
            "used_vector_store_ids": list(self.used_vector_store_ids),
            "accessed_files": list(self.accessed_files),
            "turn_count": self.turn_count,
            # Save conversation-specific tool settings
            "web_search_enabled": self.web_search_enabled,
            "file_search_enabled": self.file_search_enabled,
            "current_vector_store_ids": self.current_vector_store_ids,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "ConversationState":
        """Load conversation from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Handle usage data
        usage = None
        usage_data = data.get("usage")
        if usage_data:
            usage = ResponseUsage.model_validate(usage_data)

        # Handle backward compatibility with old token fields
        elif any(key in data for key in ["total_input_tokens", "total_output_tokens", "total_tokens"]):
            # Convert old format to new ResponseUsage
            usage = ResponseUsage(
                input_tokens=data.get("total_input_tokens", 0),
                output_tokens=data.get("total_output_tokens", 0),
                total_tokens=data.get("total_tokens", 0),
                input_tokens_details=InputTokensDetails(cached_tokens=0),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
            )

        # Handle tools data - convert dicts to typed Tool objects
        tools = []
        tools_data = data.get("tools", [])
        if tools_data:
            tools = cls._load_tools(tools_data)

        # Load used_vector_store_ids
        used_vector_store_ids = set(data.get("used_vector_store_ids", []))

        # Load accessed_files
        accessed_files = set(data.get("accessed_files", []))

        # Load turn_count
        turn_count = data.get("turn_count", 0)

        # Load conversation-specific tool settings
        web_search_enabled = data.get("web_search_enabled", False)
        file_search_enabled = data.get("file_search_enabled", False)
        current_vector_store_ids = data.get("current_vector_store_ids", [])

        conversation = cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            model=data["model"],
            tools=tools,
            metadata=data.get("metadata", {}),
            usage=usage,
            used_vector_store_ids=used_vector_store_ids,
            accessed_files=accessed_files,
            turn_count=turn_count,
            web_search_enabled=web_search_enabled,
            file_search_enabled=file_search_enabled,
            current_vector_store_ids=current_vector_store_ids,
        )

        # Load messages using Pydantic models
        for msg_data in data.get("messages", []):
            # Handle both old and new message formats
            if "role" in msg_data and "content" in msg_data and isinstance(msg_data["content"], str):
                # Old format - convert to new format
                from ..response._types.response_input_text import ResponseInputText

                message = ResponseInputMessageItem(
                    id=msg_data.get("id", f"{msg_data['role']}_{uuid.uuid4().hex[:8]}"),
                    role=msg_data["role"] if msg_data["role"] in ["user", "system", "developer"] else "user",
                    content=[ResponseInputText(type="input_text", text=msg_data["content"])],
                )
            else:
                # New format - use Pydantic validation
                message = ResponseInputMessageItem.model_validate(msg_data)

            conversation.add_message(message)

        return conversation

    def truncate_to_token_limit(self, max_tokens: int = 100000) -> None:
        """
        Truncate conversation to fit within token limit.
        This is a simple implementation that removes oldest messages.
        """

        # Simple heuristic: assume ~TOKENS_PER_CHAR chars per token
        # Extract text content from the new message format
        def get_text_content(msg: ResponseInputMessageItem) -> str:
            text_parts = []
            for content_item in msg.content:
                if is_input_text(content_item):
                    text_parts.append(content_item.text)
            return " ".join(text_parts)

        estimated_tokens = sum(len(get_text_content(msg)) // TOKENS_PER_CHAR for msg in self.messages)

        while estimated_tokens > max_tokens and len(self.messages) > MIN_MESSAGES_TO_KEEP:
            # Keep at least the last MIN_MESSAGES_TO_KEEP messages
            removed = self.messages.pop(0)
            estimated_tokens -= len(get_text_content(removed)) // TOKENS_PER_CHAR

    def to_display_format(self) -> str:
        """Format conversation for display."""
        lines = []
        for msg in self.messages:
            # Extract text content from the new message format
            text_content = self._extract_text_content(msg)
            content_str = " ".join(text_content)

            if msg.role == "user":
                lines.append(f"\n**You**: {content_str}")
            elif msg.role == "system":
                lines.append(f"\n**Assistant**: {content_str}")  # Treat system as assistant for display
            elif msg.role == "developer":
                lines.append(f"\n**Developer**: {content_str}")
        return "\n".join(lines)

    def _extract_text_content(self, msg: ResponseInputMessageItem) -> list[str]:
        """Extract text content from a message using type guards."""
        text_content = []
        for content_item in msg.content:
            if is_input_text(content_item):
                text_content.append(content_item.text)
        return text_content

    def new_request(self, content: str, config: "SearchConfig") -> "Request":
        """Create a new typed request with conversation history and current content.

        This method automatically adds the new user message to the conversation history
        and creates a typed Request object ready for the API. It prioritizes conversation
        state settings over global config for tool enablement.

        Args:
            content: The new user message content
            config: SearchConfig containing fallback tool and model settings

        Returns:
            A typed Request object ready for the API
        """
        from ..response._types import FileSearchTool, InputMessage, Request, WebSearchTool
        from ..response._types.web_search_tool import UserLocation

        # Add the new user message to conversation history first
        self.add_user_message(content)

        # Build tools list based on conversation state (prioritized) and config (fallback)
        tools = []

        # File search tool - use conversation state if available, otherwise fall back to config
        file_search_enabled = self.file_search_enabled or "file-search" in config.enabled_tools
        vector_store_ids = self.current_vector_store_ids if self.current_vector_store_ids else config.vec_ids

        if file_search_enabled and vector_store_ids:
            tools.append(
                FileSearchTool(
                    type="file_search",
                    vector_store_ids=vector_store_ids,
                    max_num_results=config.max_results,
                )
            )

        # Web search tool - use conversation state if available, otherwise fall back to config
        web_search_enabled = self.web_search_enabled or "web-search" in config.enabled_tools

        if web_search_enabled:
            tool_params = {"type": "web_search"}
            location = config.get_web_location()
            if location:
                user_location = UserLocation(
                    type="approximate",
                    country=location.get("country"),
                    city=location.get("city"),
                )
                tool_params["user_location"] = user_location
            tools.append(WebSearchTool(**tool_params))

        # Build input messages from current conversation history (including the new message)
        input_messages = []

        # Convert conversation history to InputMessage objects
        for msg in self.messages:
            # Extract text content from ResponseInputText objects
            content_parts = []
            for content_item in msg.content:
                if is_input_text(content_item):
                    content_parts.append(content_item.text)

            content_str = " ".join(content_parts)
            input_messages.append(InputMessage(role=msg.role, content=content_str))

        # Create typed request
        return Request(
            input=input_messages,
            model=config.model,
            tools=tools,
            temperature=config.temperature or 0.7,
            max_output_tokens=config.max_output_tokens or 2000,
            effort=config.effort or "low",
        )

    @classmethod
    def _load_tools(cls, tools_data: list[dict[str, Any] | Tool]) -> list[Tool]:
        """Load tools from data, handling both dict and Tool formats."""
        from ..response._types import (
            ComputerTool,
            FileSearchTool,
            FunctionTool,
            ListDocumentsTool,
            WebSearchTool,
        )
        from ..response._types.file_reader_tool import FileReaderTool

        # Tool factory mapping
        tool_factories: dict[str, type[Tool]] = {
            "file_search": FileSearchTool,
            "web_search": WebSearchTool,
            "web_search_preview": WebSearchTool,
            "web_search_preview_2025_03_11": WebSearchTool,
            "function": FunctionTool,
            "computer_use_preview": ComputerTool,
            "list_documents": ListDocumentsTool,
            "file_reader": FileReaderTool,
        }

        tools = []
        for tool_data in tools_data:
            if isinstance(tool_data, Tool):
                # Already a Tool object
                tools.append(tool_data)
            elif isinstance(tool_data, dict):
                tool_type = tool_data.get("type")
                if tool_type and tool_type in tool_factories:
                    tool_class = tool_factories[tool_type]
                    tools.append(tool_class.model_validate(tool_data))
                # Skip unknown tool types
        return tools
