"""Conversation state management for multi-turn chat mode."""

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, NewType, Protocol, TypeAlias, overload

# Import proper types from response system
from ..response._types.response_input_message_item import ResponseInputMessageItem
from ..response._types.response_usage import InputTokensDetails, OutputTokensDetails, ResponseUsage
from ..response._types.tool import Tool
from ..response.type_guards import (
    is_input_text,
    is_file_search_tool,
    is_web_search_tool,
    is_function_tool,
    is_computer_tool,
    is_document_finder_tool,
    is_file_reader_tool,
)

if TYPE_CHECKING:
    from ..response._types.response_input_text import ResponseInputText
    from ..response._types import (
        ComputerTool,
        DocumentFinderTool,
        FileSearchTool,
        FunctionTool,
        WebSearchTool,
    )
    from ..response._types.file_reader_tool import FileReaderTool

# Type aliases for clarity
MessageRole: TypeAlias = Literal["user", "system", "developer"]
ToolType: TypeAlias = Literal["file_search", "web_search", "function", "computer_use_preview", "document_finder", "file_reader"]

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

        conversation = cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            model=data["model"],
            tools=tools,
            metadata=data.get("metadata", {}),
            usage=usage,
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

    @classmethod
    def _load_tools(cls, tools_data: list[dict[str, Any] | Tool]) -> list[Tool]:
        """Load tools from data, handling both dict and Tool formats."""
        from ..response._types import (
            ComputerTool,
            DocumentFinderTool,
            FileSearchTool,
            FunctionTool,
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
            "document_finder": DocumentFinderTool,
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
