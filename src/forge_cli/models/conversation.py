"""Conversation state management for multi-turn chat mode."""

import json
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, NewType, Protocol, overload

from pydantic import BaseModel, Field, field_validator

# Import proper types from response system
from ..response._types.response_input_message_item import ResponseInputMessageItem
from ..response._types.response_usage import ResponseUsage
from ..response._types.tool import Tool
from ..response.type_guards import (
    is_file_search_tool,
    is_input_text,
    is_list_documents_tool,
)

if TYPE_CHECKING:
    from ..config import AppConfig
    from ..response._types import Request, Response

# Type aliases for clarity
type MessageRole = Literal["user", "system", "developer"]
type ToolType = Literal[
    "file_search", "web_search", "function", "computer_use_preview", "list_documents", "file_reader", "page_reader"
]

# Domain-specific types
ConversationId = NewType("ConversationId", str)
SessionId = NewType("SessionId", str)  # Keep for backward compatibility
MessageId = NewType("MessageId", str)

# Constants
DEFAULT_MODEL: Final[str] = "qwen-max-latest"


CUSTOM_ROLE_JSON_SCHEMA = {
    "role": "南京的云学堂公司客服",
    "response_style": {"tone": "string (optional)", "language": "日文"},
}


class ConversationPersistence(Protocol):
    """Protocol for conversation persistence strategies."""

    def save(self, state: "ConversationState", path: Path) -> None:
        """Save conversation state to storage."""
        ...

    def load(self, path: Path) -> "ConversationState":
        """Load conversation state from storage."""
        ...


class ConversationState(BaseModel):
    """Manages the state of a multi-turn conversation using typed API."""

    # Use proper typed messages instead of custom Message class
    messages: list[ResponseInputMessageItem] = Field(default_factory=list)
    conversation_id: ConversationId = Field(default_factory=lambda: ConversationId(f"conv_{uuid.uuid4().hex[:8]}"))
    session_id: SessionId = Field(
        default_factory=lambda: SessionId(f"session_{uuid.uuid4().hex[:12]}")
    )  # Keep for backward compatibility
    created_at: float = Field(default_factory=time.time)
    model: str = Field(default=DEFAULT_MODEL)
    tools: list[Tool] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)
    # Use proper ResponseUsage instead of manual tracking
    usage: ResponseUsage | None = Field(default=None)
    # Track conversation turns
    turn_count: int = Field(default=0, ge=0)

    # Conversation-specific tool settings that can be changed during chat
    web_search_enabled: bool = Field(default=False)
    file_search_enabled: bool = Field(default=False)
    page_reader_enabled: bool = Field(default=False)
    current_vector_store_ids: list[str] = Field(default_factory=list)
    
    # Track documents uploaded during this conversation
    uploaded_documents: list[dict[str, str]] = Field(default_factory=list)

    # Pydantic configuration
    model_config = {"arbitrary_types_allowed": True}

    @field_validator("conversation_id", mode="before")
    @classmethod
    def validate_conversation_id(cls, v: Any) -> ConversationId:
        """Ensure conversation_id is properly typed."""
        if isinstance(v, str):
            return ConversationId(v)
        return v

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v: Any) -> SessionId:
        """Ensure session_id is properly typed."""
        if isinstance(v, str):
            return SessionId(v)
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name is not empty."""
        if not v or not v.strip():
            return DEFAULT_MODEL
        return v.strip()

    def model_post_init(self, __context: Any) -> None:
        """Initialize current_vector_store_ids from tools if not set."""
        # Initialize current_vector_store_ids from tools if empty
        if not self.current_vector_store_ids and self.tools:
            # Extract vector store IDs from file search and list documents tools
            vector_store_ids = set()
            for tool in self.tools:
                if is_file_search_tool(tool):
                    vector_store_ids.update(tool.vector_store_ids)
                elif is_list_documents_tool(tool):
                    vector_store_ids.update(tool.vector_store_ids)

            if vector_store_ids:
                self.current_vector_store_ids = list(vector_store_ids)

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
        from ..response._types.response_input_text import ResponseInputText

        message = ResponseInputMessageItem(
            id=assistant_id or f"assistant_{uuid.uuid4().hex[:8]}",
            role="assistant",  # Now using correct assistant role
            content=[ResponseInputText(type="input_text", text=content)],
        )
        self.add_message(message)
        return message

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

    def get_current_vector_store_ids(self) -> list[str]:
        """Get the current vector store IDs for this conversation.

        Returns:
            List of current vector store IDs
        """
        return self.current_vector_store_ids.copy()

    def is_file_search_enabled(self) -> bool:
        """Check if file search is enabled for this conversation."""
        return self.file_search_enabled

    def add_uploaded_document(self, document_id: str, filename: str, upload_time: str | None = None) -> None:
        """Add a document to the uploaded documents list.
        
        Args:
            document_id: The unique ID of the uploaded document
            filename: The original filename of the uploaded document
            upload_time: ISO format timestamp (defaults to current time)
        """
        import datetime
        
        if upload_time is None:
            upload_time = datetime.datetime.now().isoformat()
            
        document_info = {
            "id": document_id,
            "filename": filename,
            "uploaded_at": upload_time
        }
        
        # Avoid duplicates based on document ID
        if not any(doc["id"] == document_id for doc in self.uploaded_documents):
            self.uploaded_documents.append(document_info)

    def get_uploaded_documents(self) -> list[dict[str, str]]:
        """Get the list of documents uploaded during this conversation.
        
        Returns:
            List of document info dictionaries with keys: id, filename, uploaded_at
        """
        return self.uploaded_documents.copy()

    def remove_uploaded_document(self, document_id: str) -> bool:
        """Remove a document from the uploaded documents list.
        
        Args:
            document_id: The ID of the document to remove
            
        Returns:
            True if document was found and removed, False otherwise
        """
        original_length = len(self.uploaded_documents)
        self.uploaded_documents = [
            doc for doc in self.uploaded_documents 
            if doc["id"] != document_id
        ]
        return len(self.uploaded_documents) < original_length

    def clear_uploaded_documents(self) -> None:
        """Clear all uploaded documents from the conversation."""
        self.uploaded_documents.clear()

    @classmethod
    def get_conversations_dir(cls) -> Path:
        """Get the directory where conversations are stored."""
        from pathlib import Path

        # Use user's home directory/.forge-cli/conversations
        home_dir = Path.home()
        conversations_dir = home_dir / ".forge-cli" / "conversations"
        conversations_dir.mkdir(parents=True, exist_ok=True)
        return conversations_dir

    def get_default_save_path(self) -> Path:
        """Get the default save path for this conversation based on its ID."""
        return self.get_conversations_dir() / f"{self.conversation_id}.json"

    def save_by_id(self) -> Path:
        """Save conversation using its ID as filename.

        Returns:
            Path where the conversation was saved
        """
        path = self.get_default_save_path()
        self.save(path)
        return path

    @classmethod
    def from_config(cls, config: "AppConfig") -> "ConversationState":
        """Create a new ConversationState initialized from AppConfig.

        Args:
            config: AppConfig containing initialization settings

        Returns:
            New ConversationState with config-based initialization
        """
        return cls(
            model=config.model,
            web_search_enabled="web-search" in config.enabled_tools,
            file_search_enabled="file-search" in config.enabled_tools,
            page_reader_enabled="page-reader" in config.enabled_tools,
            current_vector_store_ids=config.vec_ids.copy() if config.vec_ids else [],
            metadata={
                "effort": config.effort,
                "temperature": config.temperature,
                "max_output_tokens": config.max_output_tokens,
                "server_url": config.server_url,
            },
        )

    @classmethod
    def load_by_id(cls, conversation_id: str) -> "ConversationState":
        """Load conversation by its ID.

        Args:
            conversation_id: The conversation ID to load

        Returns:
            Loaded ConversationState

        Raises:
            FileNotFoundError: If conversation file doesn't exist
        """
        conversations_dir = cls.get_conversations_dir()
        path = conversations_dir / f"{conversation_id}.json"

        if not path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")

        return cls.load(path)

    @classmethod
    def list_conversations(cls) -> list[dict[str, str]]:
        """List all saved conversations.

        Returns:
            List of conversation info dicts with keys: id, created_at, message_count, model
        """
        conversations_dir = cls.get_conversations_dir()
        conversations = []

        for json_file in conversations_dir.glob("*.json"):
            try:
                # Quick load to get basic info
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Extract basic info
                conv_id = data.get("conversation_id", json_file.stem)
                created_at = data.get("created_at", 0)
                message_count = len(data.get("messages", []))
                model = data.get("model", "unknown")

                # Format created_at as readable string
                import datetime

                created_str = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")

                conversations.append(
                    {
                        "id": conv_id,
                        "created_at": created_str,
                        "message_count": str(message_count),
                        "model": model,
                        "file": str(json_file),
                    }
                )

            except Exception:
                # Skip corrupted files
                continue

        # Sort by creation time (newest first)
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations

    def update_from_response(self, response: "Response") -> None:
        """Update conversation state from response object.

        This method transfers relevant information from a Response object
        to the ConversationState, including:
        - Token usage statistics
        - Model information

        Args:
            response: Response object from stream processing
        """
        # Handle usage information from response
        if response.usage:
            self.add_token_usage(response.usage)

        # Handle model information from response
        if response.model:
            # Only update if we don't have a model set or if it's different
            if not self.model or self.model != response.model:
                self.model = response.model

        # Add assistant message from response
        assistant_text = response.output_text
        if assistant_text:
            self.add_assistant_message(assistant_text)
            # Increment turn count when we successfully add an assistant message
            self.increment_turn_count()

    def save(self, path: Path) -> None:
        """Save conversation to a JSON file using Pydantic serialization."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            # Use Pydantic's model_dump for automatic serialization
            data = self.model_dump(mode="json")
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "ConversationState":
        """Load conversation from a JSON file using Pydantic validation."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # Use Pydantic's model_validate for automatic validation and type conversion
        return cls.model_validate(data)

    def new_request(self, content: str, config: "AppConfig") -> "Request":
        """Create a new typed request with conversation history and current content.

        This method automatically adds the new user message to the conversation history
        and creates a typed Request object ready for the API. It prioritizes conversation
        state settings over global config for tool enablement.

        Args:
            content: The new user message content
            config: AppConfig containing fallback tool and model settings

        Returns:
            A typed Request object ready for the API
        """
        from ..response._types import FileSearchTool, InputMessage, PageReaderTool, Request, WebSearchTool
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

        # Page reader tool - use conversation state if available, otherwise fall back to config
        page_reader_enabled = self.page_reader_enabled or "page-reader" in config.enabled_tools

        if page_reader_enabled:
            tools.append(PageReaderTool(type="page_reader"))

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
        instructions = config.build_instructions_json()
        if config.debug and instructions:
            print(f"Custom instructions: {instructions}")
            
        return Request(
            input=input_messages,
            model=config.model,
            tools=tools,
            temperature=config.temperature or 0.7,
            max_output_tokens=config.max_output_tokens or 2000,
            effort=config.effort or "low",
            instructions=instructions,
        )
