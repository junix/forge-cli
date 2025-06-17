# ADR-005: Interactive Chat Mode Implementation

**Status**: Accepted (Updated 2025-06-17)
**Date**: 2025-01-27 (Updated 2025-06-17)
**Decision Makers**: Development Team
**Updates**: Chat-first architecture, modular command system, ChatSessionManager, typed API integration

## Context

The Forge CLI initially supported only single-turn query processing. To provide a more natural and efficient user experience, especially for iterative research and exploration tasks, the system needed an interactive chat mode that maintains conversation context across multiple turns.

The challenge was to implement this chat functionality while maintaining the existing modular architecture and ensuring compatibility with all existing features (file search, web search, multiple display modes).

**2025-06-17 Update**: Chat mode has evolved from an optional feature to the primary interface. The system now defaults to chat mode, with a sophisticated modular command system and session management architecture.

## Decision

We implemented a comprehensive interactive chat mode with the following design decisions:

### 1. **Chat-First Architecture with Session Management**

- `ChatSessionManager` orchestrates the entire chat experience
- `ChatController` handles user interaction and command processing
- Integration with typed API (`astream_typed_response`) for streaming
- Seamless conversation resumption with `--resume` functionality

### 2. **Modular Command System**

- Modular command architecture with separate command modules:
  - `session.py`: Exit, clear, help, new conversation commands
  - `conversation.py`: Save, load, list, history commands
  - `config.py`: Model, tools, vector store configuration commands
  - `info.py`: Inspection and debugging commands
  - `tool.py`: Dynamic tool toggling commands
- Abstract `ChatCommand` base class for extensibility
- `CommandRegistry` with automatic command discovery and registration
- Alias support for improved usability (e.g., `/h` for `/help`, `/q` for `/quit`)

### 3. **Enhanced Conversation State Management**

- `ConversationState` Pydantic model with full type safety
- Typed message handling using `ResponseInputMessageItem`
- Persistent conversation state with JSON serialization and ID-based loading
- Context preservation across multiple API calls with proper token usage tracking
- Tool configuration persistence (web search, file search, vector stores)

### 4. **Advanced Input System**

- `InputHandler` with `prompt_toolkit` integration for enhanced UX
- `CommandCompleter` for intelligent auto-completion
- Command history persistence across sessions
- Graceful fallback to basic input when `prompt_toolkit` unavailable
- Keyboard interrupt handling (Ctrl+C) with conversation preservation

## Implementation Details

### Core Architecture

```python
class ChatSessionManager:
    """Manages chat sessions including conversation flow and message processing."""

    def __init__(self, config: AppConfig, display: Display):
        self.config = config
        self.display = display
        self.controller = ChatController(config, display)

    async def start_session(
        self,
        initial_question: str | None = None,
        resume_conversation_id: str | None = None
    ) -> None:
        """Start interactive chat session with typed API."""
        # Resume existing conversation if requested
        if resume_conversation_id:
            self.controller.conversation = ConversationState.load_by_id(resume_conversation_id)

        # Show welcome and handle initial question
        self.controller.show_welcome()
        if initial_question:
            await self._handle_user_message(initial_question)

        # Main chat loop with command parsing
        while self.controller.running:
            user_input = await self.controller.get_user_input()
            command_name, args = self.controller.commands.parse_command(user_input)

            if command_name is not None:
                continue_chat = await self.controller.handle_command(command_name, args)
                if not continue_chat:
                    break
            else:
                await self._handle_user_message(user_input)
```

### Modular Command System

```python
class ChatCommand(ABC):
    """Abstract base class for chat commands."""
    name: str = ""
    description: str = ""
    aliases: list[str] = []

    @abstractmethod
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute command and return whether to continue chat."""
        pass

class CommandRegistry:
    """Manages and provides access to chat commands."""

    def __init__(self):
        self.commands: dict[str, ChatCommand] = {}
        self.aliases: dict[str, str] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """Register all predefined default chat commands."""
        from .session import ExitCommand, ClearCommand, HelpCommand, NewCommand
        from .conversation import SaveCommand, LoadCommand, ListConversationsCommand
        from .config import ModelCommand, ToolsCommand, VectorStoreCommand
        # ... register all commands
```

### Enhanced Conversation State

```python
class ConversationState(BaseModel):
    """Manages the state of a multi-turn conversation using typed API."""

    messages: list[ResponseInputMessageItem] = Field(default_factory=list)
    conversation_id: ConversationId = Field(default_factory=lambda: ConversationId(f"conv_{uuid.uuid4().hex[:8]}"))
    model: str = Field(default=DEFAULT_MODEL)
    tools: list[Tool] = Field(default_factory=list)
    usage: ResponseUsage | None = Field(default=None)

    def new_request(self, content: str, config: AppConfig) -> Request:
        """Create typed request with full conversation history."""
        # Add user message and create Request object

    def update_from_response(self, response: Response) -> None:
        """Update conversation state from response object."""
        # Extract assistant message and update usage
```

## Command Set

The chat mode provides a comprehensive set of modular commands:

### Session Management Commands

| Command | Aliases | Module | Description |
|---------|---------|--------|-------------|
| `/help` | `/h`, `/?` | session | Show available commands with descriptions |
| `/exit` | `/quit`, `/bye`, `/q` | session | Exit chat mode gracefully |
| `/clear` | `/c` | session | Clear conversation history |
| `/new` | `/n` | session | Start new conversation |

### Conversation Management Commands

| Command | Aliases | Module | Description |
|---------|---------|--------|-------------|
| `/save [name]` | `/s` | conversation | Save conversation to file |
| `/load <name>` | `/l` | conversation | Load conversation from file |
| `/list` | `/ls` | conversation | List all saved conversations |
| `/history` | `/hist` | conversation | Show conversation message history |

### Configuration Commands

| Command | Aliases | Module | Description |
|---------|---------|--------|-------------|
| `/model [name]` | `/m` | config | Show/change AI model |
| `/tools` | `/t` | config | Show enabled tools |
| `/vectorstore [id]` | `/vs`, `/vec` | config | Show/change vector store IDs |

### Tool Management Commands

| Command | Aliases | Module | Description |
|---------|---------|--------|-------------|
| `/toggle <tool>` | `/tog` | tool | Toggle specific tools on/off |

### Information Commands

| Command | Aliases | Module | Description |
|---------|---------|--------|-------------|
| `/inspect` | `/i` | info | Show detailed conversation state |

## Integration with Existing Architecture

### 1. **V3 Display Architecture Integration**

- Chat mode uses V3 snapshot-based display system
- All display renderers (Rich, Plain, JSON) support chat functionality
- Display factory creates appropriate renderer based on configuration
- Chat-specific status messages and welcome screens

### 2. **Typed API Integration**

- Full integration with `astream_typed_response` for streaming
- `TypedStreamHandler` processes response snapshots
- Conversation state uses typed `ResponseInputMessageItem` messages
- Proper token usage tracking with `ResponseUsage`

### 3. **Configuration System Integration**

- `AppConfig` Pydantic model provides type-safe configuration
- Tool configurations persist across chat turns via conversation state
- Dynamic reconfiguration via chat commands updates conversation state
- Seamless integration with CLI argument parsing

## Consequences

### Positive

- **Chat-First Experience**: Natural conversation interface as primary mode
- **Enhanced User Experience**: Sophisticated command system with auto-completion
- **Modular Architecture**: Easy to add new commands and functionality
- **Type Safety**: Full Pydantic validation and typed API integration
- **Session Management**: Robust conversation persistence and resumption
- **Context Preservation**: Complete conversation history with token usage tracking
- **Flexible Tool Management**: Dynamic tool configuration via commands
- **Display Integration**: Seamless integration with V3 display architecture

### Negative

- **Memory Usage**: Conversation history and state grows over time
- **Complexity**: Sophisticated state management and command processing
- **Dependencies**: Optional dependency on `prompt_toolkit` for enhanced input
- **Learning Curve**: Users need to learn command system

### Mitigation Strategies

1. **Memory Management**: Efficient conversation state with optional truncation
2. **Graceful Degradation**: Fallback input methods when dependencies unavailable
3. **Error Recovery**: Robust error handling with conversation preservation
4. **User Experience**: Comprehensive help system and command auto-completion

## Usage Examples

### Starting Chat Mode (Default Behavior)

```bash
# Default chat mode (no flags needed)
forge-cli

# Chat with specific tools and vector stores
forge-cli -t file-search --vec-id vs_123

# Chat with initial question
forge-cli -q "Hello, what can you help me with?"

# Resume existing conversation
forge-cli --resume conv_abc123
```

### In-Chat Commands

```
You: What documents do you have about machine learning?
Assistant: [Provides response with file search]

You: /save ml_research
💾 Saved conversation to ml_research.json

You: /toggle web-search
✅ Enabled web-search tool

You: What are the latest ML trends?
Assistant: [Provides response with web search]

You: /list
📋 Saved conversations:
  - ml_research (3 messages, 2025-06-17)
  - project_notes (15 messages, 2025-06-16)

You: /exit
👋 Goodbye! Thanks for chatting.
```

## Future Enhancements

1. **Conversation Branching**: Save/restore conversation checkpoints
2. **Multi-modal Input**: Support for image uploads in chat
3. **Collaborative Features**: Shared conversation sessions
4. **Advanced Search**: Search within conversation history
5. **Template System**: Pre-defined conversation templates
6. **Plugin System**: Third-party command extensions

## Related ADRs

- **ADR-001**: Command-Line Interface Design (updated for chat-first approach)
- **ADR-007**: Typed-Only Architecture Migration (enables current implementation)
- **ADR-008**: V3 Response Snapshot Display Architecture (display integration)
- **ADR-012**: Chat-First Architecture Migration (documents default chat mode)
- **ADR-013**: Modular Chat Command System (documents command architecture)
- **ADR-014**: Configuration System Refactoring (AppConfig integration)

## Related Components

- `src/forge_cli/chat/session.py` - Chat session manager
- `src/forge_cli/chat/controller.py` - Chat controller and coordination
- `src/forge_cli/chat/commands/` - Modular command system
- `src/forge_cli/chat/inputs.py` - Enhanced input handling
- `src/forge_cli/models/conversation.py` - Conversation state management
- `src/forge_cli/display/v3/` - V3 display architecture integration
- `src/forge_cli/main.py` - Main entry point with session management

---

**Key Changes in 2025-06-17 Update**: Chat mode has evolved from an optional feature to the primary interface with sophisticated session management, modular command system, and full integration with the typed API and V3 display architecture.
