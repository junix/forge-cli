"""Conversation state management for multi-turn chat mode."""

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Union, List, Optional, Literal


@dataclass
class Message:
    """Represents a single message in the conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Union[str, int, float, bool]]] = None

    def __post_init__(self):
        """Initialize defaults after dataclass init."""
        if self.id is None:
            self.id = f"{self.role}_{uuid.uuid4().hex[:8]}"
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Union[str, float, Dict]]:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "id": self.id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, float, Dict]]) -> "Message":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            id=data.get("id"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ConversationState:
    """Manages the state of a multi-turn conversation."""

    messages: List[Message] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:12]}")
    created_at: float = field(default_factory=time.time)
    model: str = "qwen-max-latest"
    tools: List[Dict[str, Union[str, bool, List]]] = field(default_factory=list)
    metadata: Dict[str, Union[str, int, float, bool]] = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)

    def add_user_message(self, content: str) -> Message:
        """Add a user message and return it."""
        message = Message(role="user", content=content)
        self.add_message(message)
        return message

    def add_assistant_message(self, content: str) -> Message:
        """Add an assistant message and return it."""
        message = Message(role="assistant", content=content)
        self.add_message(message)
        return message

    def to_api_format(self) -> List[Dict[str, Union[str, float]]]:
        """Convert messages to API format."""
        return [{"role": msg.role, "content": msg.content, "id": msg.id} for msg in self.messages]

    def clear(self) -> None:
        """Clear conversation history but keep configuration."""
        self.messages.clear()

    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)

    def get_last_n_messages(self, n: int) -> List[Message]:
        """Get the last n messages."""
        return self.messages[-n:] if n > 0 else []

    def save(self, path: Path) -> None:
        """Save conversation to a JSON file."""
        data = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "model": self.model,
            "tools": self.tools,
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages],
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "ConversationState":
        """Load conversation from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conversation = cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            model=data["model"],
            tools=data.get("tools", []),
            metadata=data.get("metadata", {}),
        )

        # Load messages
        for msg_data in data.get("messages", []):
            message = Message.from_dict(msg_data)
            conversation.add_message(message)

        return conversation

    def truncate_to_token_limit(self, max_tokens: int = 100000) -> None:
        """
        Truncate conversation to fit within token limit.
        This is a simple implementation that removes oldest messages.
        """
        # Simple heuristic: assume ~4 chars per token
        estimated_tokens = sum(len(msg.content) // 4 for msg in self.messages)

        while estimated_tokens > max_tokens and len(self.messages) > 2:
            # Keep at least the last 2 messages
            removed = self.messages.pop(0)
            estimated_tokens -= len(removed.content) // 4

    def to_display_format(self) -> str:
        """Format conversation for display."""
        lines = []
        for msg in self.messages:
            if msg.role == "user":
                lines.append(f"\n**You**: {msg.content}")
            elif msg.role == "assistant":
                lines.append(f"\n**Assistant**: {msg.content}")
            elif msg.role == "system":
                lines.append(f"\n**System**: {msg.content}")
        return "\n".join(lines)
