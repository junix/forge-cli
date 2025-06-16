# ADR-005: Interactive Chat Mode Implementation

**Status**: Accepted  
**Date**: 2025-01-27  
**Decision Makers**: Development Team  

## Context

The Forge CLI initially supported only single-turn query processing. To provide a more natural and efficient user experience, especially for iterative research and exploration tasks, the system needed an interactive chat mode that maintains conversation context across multiple turns.

The challenge was to implement this chat functionality while maintaining the existing modular architecture and ensuring compatibility with all existing features (file search, web search, multiple display modes).

## Decision

We implemented a comprehensive interactive chat mode with the following design decisions:

### 1. **Conversation State Management**
- `Conversation` class manages message history with role-based messages
- Persistent conversation state with JSON serialization
- Context preservation across multiple API calls
- Session management with save/load functionality

### 2. **Command System Architecture**
- Prefix-based command system (commands start with `/`)
- `CommandRegistry` with extensible command handlers
- Alias support for improved usability (e.g., `/h` for `/help`)
- Rich help system with command descriptions and usage

### 3. **Chat Controller Design**
- `ChatController` orchestrates chat sessions
- Integration with existing `StreamHandler` and processor architecture
- Tool configuration persistence across chat turns
- Graceful error handling and recovery

### 4. **Enhanced Input System**
- `prompt_toolkit` integration for enhanced input experience
- Auto-completion for commands and aliases
- Fallback to basic input if `prompt_toolkit` unavailable
- Keyboard interrupt handling (Ctrl+C)

## Implementation Details

### Core Architecture

```python
class ChatController:
    """Main controller for interactive chat sessions."""
    
    def __init__(self, config: SearchConfig, display: BaseDisplay):
        self.config = config
        self.display = display
        self.conversation = Conversation()
        self.command_registry = CommandRegistry()
        self.stream_handler = StreamHandler(display)
        
    async def run(self):
        """Main chat loop with command processing."""
        while self.running:
            user_input = await self._get_user_input()
            
            if user_input.startswith("/"):
                await self._handle_command(user_input)
            else:
                await self._process_message(user_input)
```

### Command System

```python
class CommandRegistry:
    """Registry for chat commands with aliases."""
    
    COMMANDS = {
        "help": Command(name="help", aliases=["h", "?"], 
                       handler=self._cmd_help),
        "save": Command(name="save", aliases=["s"], 
                       handler=self._cmd_save),
        "load": Command(name="load", aliases=["l"], 
                       handler=self._cmd_load),
        "clear": Command(name="clear", aliases=["c"], 
                        handler=self._cmd_clear),
        # ... more commands
    }
```

### Enhanced Display Integration

```python
class RichDisplay(BaseDisplay):
    def show_chat_welcome(self, config: SearchConfig):
        """Display chat mode welcome screen."""
        # ASCII art logo, configuration display, tips
        
    def show_chat_complete(self):
        """Finalize assistant response display."""
        # Ensure response remains visible after streaming
```

## Command Set

The chat mode provides a comprehensive set of commands:

| Command | Aliases | Description |
|---------|---------|-------------|
| `/help` | `/h`, `/?` | Show available commands |
| `/save [file]` | `/s` | Save conversation to file |
| `/load <file>` | `/l` | Load conversation from file |
| `/clear` | `/c` | Clear conversation history |
| `/exit` | `/quit`, `/q` | Exit chat mode |
| `/tools` | `/t` | Manage enabled tools |
| `/model` | `/m` | Show/change AI model |
| `/history` | `/hist` | Show conversation history |
| `/web` | `/w` | Toggle web search |
| `/file` | `/f` | Toggle file search |

## Integration with Existing Architecture

### 1. **Processor Compatibility**
- Chat mode uses the same processor registry as single-turn mode
- All existing processors work seamlessly in chat context
- Citation processing and tool execution identical across modes

### 2. **Display Strategy Integration**
- All display modes (Rich, Plain, JSON) support chat functionality
- Chat-specific methods added to base display interface
- Backwards compatibility maintained for non-chat usage

### 3. **Configuration Preservation**
- Tool configurations persist across chat turns
- Model and search settings maintained throughout session
- Dynamic reconfiguration via chat commands

## Consequences

### Positive
- **Enhanced User Experience**: Natural conversation flow for iterative tasks
- **Context Preservation**: Full conversation history maintained
- **Extensible Commands**: Easy to add new chat functionality
- **Consistent Architecture**: Leverages existing processor and display systems
- **Flexible Tool Management**: Dynamic enable/disable of search tools
- **Session Persistence**: Save/restore conversations for later use

### Negative
- **Memory Usage**: Conversation history grows over time
- **Complexity**: Additional state management and command processing
- **Dependencies**: Optional dependency on `prompt_toolkit` for enhanced input

### Mitigation Strategies
1. **Memory Management**: Conversation truncation for very long chats
2. **Graceful Degradation**: Fallback input methods when dependencies unavailable
3. **Error Recovery**: Robust error handling with conversation preservation

## Usage Examples

### Starting Chat Mode
```bash
# Basic chat mode
forge-cli --chat

# Chat with specific tools and vector stores
forge-cli --chat -t file-search --vec-id vs_123

# Chat with initial question
forge-cli --chat -q "Hello, what can you help me with?"
```

### In-Chat Commands
```
You: What documents do you have about machine learning?
Assistant: [Provides response with file search]

You: /save ml_research
💾 Saved conversation to ml_research.json

You: /web
✅ Enabled web search tool

You: What are the latest ML trends?
Assistant: [Provides response with web search]

You: /exit
👋 Goodbye!
```

## Future Enhancements

1. **Conversation Branching**: Save/restore conversation checkpoints
2. **Multi-modal Input**: Support for image uploads in chat
3. **Collaborative Features**: Shared conversation sessions
4. **Advanced Search**: Search within conversation history
5. **Template System**: Pre-defined conversation templates

## References

- ADR-001-commandline-design.md - CLI design principles
- ADR-002-reasoning-event-handling.md - Event processing architecture
- ADR-004-snapshot-based-streaming-design.md - Streaming implementation
- prompt_toolkit documentation - Enhanced input library

## Related Components

- `src/forge_cli/chat/controller.py` - Main chat controller
- `src/forge_cli/chat/commands.py` - Command system implementation
- `src/forge_cli/models/conversation.py` - Conversation state management
- `src/forge_cli/display/` - Chat mode display enhancements
- `src/forge_cli/main.py` - Chat mode entry point integration