"""Conversation state management for multi-turn chat mode."""

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# Import proper types from response system
from ..response._types.response_input_message_item import ResponseInputMessageItem
from ..response._types.response_usage import InputTokensDetails, OutputTokensDetails, ResponseUsage
from ..response._types.tool import Tool


@dataclass
class ConversationState:
    """Manages the state of a multi-turn conversation using typed API."""

    # Use proper typed messages instead of custom Message class
    messages: list[ResponseInputMessageItem] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:12]}")
    created_at: float = field(default_factory=time.time)
    model: str = "qwen-max-latest"
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
                # Handle both Pydantic objects and dict formats
                if hasattr(content_item, 'type') and content_item.type == "input_text":
                    content_parts.append(content_item.text)
                elif isinstance(content_item, dict) and content_item.get("type") == "input_text":
                    content_parts.append(content_item.get("text", ""))
            
            content_str = " ".join(content_parts)
            
            api_messages.append({
                "role": msg.role,
                "content": content_str,
            })
        
        return api_messages

    def clear(self) -> None:
        """Clear conversation history but keep configuration."""
        self.messages.clear()

    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)

    def get_last_n_messages(self, n: int) -> list[ResponseInputMessageItem]:
        """Get the last n messages."""
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
            from ..response._types import (
                FileSearchTool,
                WebSearchTool,
                FunctionTool,
                ComputerTool,
                DocumentFinderTool,
            )
            from ..response._types.file_reader_tool import FileReaderTool
            
            for tool_data in tools_data:
                if isinstance(tool_data, dict):
                    tool_type = tool_data.get("type")
                    if tool_type == "file_search":
                        tools.append(FileSearchTool.model_validate(tool_data))
                    elif tool_type in ["web_search", "web_search_preview", "web_search_preview_2025_03_11"]:
                        tools.append(WebSearchTool.model_validate(tool_data))
                    elif tool_type == "function":
                        tools.append(FunctionTool.model_validate(tool_data))
                    elif tool_type == "computer_use_preview":
                        tools.append(ComputerTool.model_validate(tool_data))
                    elif tool_type == "document_finder":
                        tools.append(DocumentFinderTool.model_validate(tool_data))
                    elif tool_type == "file_reader":
                        tools.append(FileReaderTool.model_validate(tool_data))
                    else:
                        # For unknown tool types, we could either skip or try a generic approach
                        # For now, let's skip unknown tools with a note
                        continue
                else:
                    # Already a Tool object, keep as is
                    tools.append(tool_data)

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

        # Simple heuristic: assume ~4 chars per token
        # Extract text content from the new message format
        def get_text_content(msg: ResponseInputMessageItem) -> str:
            text_parts = []
            for content_item in msg.content:
                # Handle both Pydantic objects and dict formats
                if hasattr(content_item, "type") and content_item.type == "input_text":
                    text_parts.append(content_item.text)
                elif isinstance(content_item, dict) and content_item.get("type") == "input_text":
                    text_parts.append(content_item.get("text", ""))
            return " ".join(text_parts)

        estimated_tokens = sum(len(get_text_content(msg)) // 4 for msg in self.messages)

        while estimated_tokens > max_tokens and len(self.messages) > 2:
            # Keep at least the last 2 messages
            removed = self.messages.pop(0)
            estimated_tokens -= len(get_text_content(removed)) // 4

    def to_display_format(self) -> str:
        """Format conversation for display."""
        lines = []
        for msg in self.messages:
            # Extract text content from the new message format
            text_content = []
            for content_item in msg.content:
                # Handle both Pydantic objects and dict formats
                if hasattr(content_item, "type") and content_item.type == "input_text":
                    text_content.append(content_item.text)
                elif isinstance(content_item, dict) and content_item.get("type") == "input_text":
                    text_content.append(content_item.get("text", ""))

            content_str = " ".join(text_content)

            if msg.role == "user":
                lines.append(f"\n**You**: {content_str}")
            elif msg.role == "system":
                lines.append(f"\n**Assistant**: {content_str}")  # Treat system as assistant for display
            elif msg.role == "developer":
                lines.append(f"\n**Developer**: {content_str}")
        return "\n".join(lines)
