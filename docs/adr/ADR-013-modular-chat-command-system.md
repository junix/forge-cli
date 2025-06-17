# ADR-013: Modular Chat Command System

**Status**: Accepted  
**Date**: 2025-06-17  
**Decision Makers**: Development Team  
**Complements**: ADR-005 (Interactive Chat Mode), ADR-012 (Chat-First Architecture)

## Context

The original chat command system in ADR-005 implemented all commands within a single `commands.py` file with a monolithic `CommandRegistry` class. As the chat functionality expanded and became the primary interface (ADR-012), this approach showed several limitations:

### Original Architecture Problems

1. **Monolithic Structure**: All commands in one file became unwieldy (500+ lines)
2. **Poor Separation of Concerns**: Session, configuration, and tool commands mixed together
3. **Limited Extensibility**: Adding new commands required modifying core registry code
4. **Testing Complexity**: Difficult to test individual command categories in isolation
5. **Code Organization**: Related functionality scattered across single large file
6. **Maintenance Burden**: Changes to one command type affected unrelated commands

### Growing Command Complexity

The chat system evolved to support:
- Session management (exit, clear, new, help)
- Conversation persistence (save, load, list, history)
- Configuration management (model, tools, vector stores)
- Tool toggling (enable/disable specific tools)
- Information and debugging (inspect, status)
- Future extensibility for plugins and custom commands

## Decision

**Implement a modular chat command system** with separate command modules organized by functional domain and a plugin-style architecture for extensibility.

### 1. Modular Command Architecture

Organize commands into logical modules:

```
src/forge_cli/chat/commands/
├── __init__.py          # Module exports and registry
├── base.py              # Abstract base classes and registry
├── session.py           # Session management commands
├── conversation.py      # Conversation persistence commands
├── config.py            # Configuration management commands
├── tool.py              # Tool management commands
└── info.py              # Information and debugging commands
```

### 2. Abstract Base Class Design

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
```

### 3. Automatic Command Registration

```python
class CommandRegistry:
    """Manages and provides access to chat commands."""
    
    def __init__(self):
        self.commands: dict[str, ChatCommand] = {}
        self.aliases: dict[str, str] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all predefined default chat commands."""
        from .session import ExitCommand, ClearCommand, HelpCommand, NewCommand
        from .conversation import SaveCommand, LoadCommand, ListConversationsCommand, HistoryCommand
        from .config import ModelCommand, ToolsCommand, VectorStoreCommand
        from .info import InspectCommand
        from .tool import ToggleToolCommand
        
        # Register all commands automatically
        for command_class in [ExitCommand, ClearCommand, HelpCommand, NewCommand,
                             SaveCommand, LoadCommand, ListConversationsCommand, HistoryCommand,
                             ModelCommand, ToolsCommand, VectorStoreCommand,
                             InspectCommand, ToggleToolCommand]:
            self.register(command_class())
```

## Implementation Details

### Session Management Commands (`session.py`)

```python
class ExitCommand(ChatCommand):
    name = "exit"
    description = "Exit the chat"
    aliases = ["quit", "bye", "q"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        if not controller.config.quiet:
            controller.display.show_status("👋 Goodbye! Thanks for chatting.")
        return False

class ClearCommand(ChatCommand):
    name = "clear"
    description = "Clear conversation history"
    aliases = ["c"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        controller.conversation.clear_messages()
        controller.display.show_status("🧹 Conversation history cleared.")
        return True

class HelpCommand(ChatCommand):
    name = "help"
    description = "Show available commands"
    aliases = ["h", "?"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        # Display comprehensive help with command categories
        controller.display.show_help(controller.commands)
        return True
```

### Conversation Management Commands (`conversation.py`)

```python
class SaveCommand(ChatCommand):
    name = "save"
    description = "Save conversation to file"
    aliases = ["s"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        filename = args.strip() or f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        controller.conversation.save(filename)
        controller.display.show_status(f"💾 Saved conversation as {filename}.json")
        return True

class LoadCommand(ChatCommand):
    name = "load"
    description = "Load conversation from file"
    aliases = ["l"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        if not args.strip():
            controller.display.show_error("Usage: /load <filename>")
            return True
        
        try:
            controller.conversation = ConversationState.load(args.strip())
            controller.display.show_status(f"📂 Loaded conversation from {args.strip()}.json")
        except FileNotFoundError:
            controller.display.show_error(f"Conversation file {args.strip()}.json not found")
        return True
```

### Configuration Management Commands (`config.py`)

```python
class ModelCommand(ChatCommand):
    name = "model"
    description = "Show or change AI model"
    aliases = ["m"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        if not args.strip():
            # Show current model
            controller.display.show_status(f"🤖 Current model: {controller.conversation.model}")
        else:
            # Change model
            controller.conversation.model = args.strip()
            controller.display.show_status(f"🤖 Changed model to: {args.strip()}")
        return True

class ToolsCommand(ChatCommand):
    name = "tools"
    description = "Show enabled tools"
    aliases = ["t"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        enabled_tools = controller.conversation.get_enabled_tools()
        if enabled_tools:
            tools_list = ", ".join(enabled_tools)
            controller.display.show_status(f"🔧 Enabled tools: {tools_list}")
        else:
            controller.display.show_status("🔧 No tools currently enabled")
        return True
```

## Benefits of Modular Architecture

### 1. Separation of Concerns
- **Session Commands**: Focus purely on chat session lifecycle
- **Conversation Commands**: Handle persistence and history management
- **Configuration Commands**: Manage settings and tool configuration
- **Tool Commands**: Dynamic tool management
- **Info Commands**: Debugging and inspection utilities

### 2. Improved Maintainability
- **Focused Files**: Each module handles one domain of functionality
- **Clear Responsibilities**: Easy to understand what each module does
- **Isolated Changes**: Modifications to one command type don't affect others
- **Easier Testing**: Test each command category independently

### 3. Enhanced Extensibility
- **Plugin Architecture**: New command modules can be added easily
- **Third-Party Extensions**: External packages can provide additional commands
- **Custom Commands**: Users can create project-specific commands
- **Dynamic Loading**: Commands can be loaded at runtime

### 4. Better Code Organization
- **Logical Grouping**: Related commands are co-located
- **Consistent Patterns**: Each module follows the same structure
- **Clear Interfaces**: Abstract base class defines contract
- **Type Safety**: Full type hints and validation

## Command Discovery and Registration

### Automatic Registration Pattern

```python
# In __init__.py
from .base import ChatCommand, CommandRegistry
from .session import ExitCommand, ClearCommand, HelpCommand, NewCommand
from .conversation import SaveCommand, LoadCommand, ListConversationsCommand, HistoryCommand
from .config import ModelCommand, ToolsCommand, VectorStoreCommand
from .info import InspectCommand
from .tool import ToggleToolCommand

__all__ = [
    # Base classes
    "ChatCommand", "CommandRegistry",
    # All command classes for external use
    "ExitCommand", "ClearCommand", "HelpCommand", "NewCommand",
    "SaveCommand", "LoadCommand", "ListConversationsCommand", "HistoryCommand",
    "ModelCommand", "ToolsCommand", "VectorStoreCommand",
    "InspectCommand", "ToggleToolCommand",
]
```

### Registry Intelligence

```python
class CommandRegistry:
    def get_commands_by_category(self) -> dict[str, list[ChatCommand]]:
        """Group commands by their module/category for help display."""
        categories = {
            "Session": ["exit", "clear", "help", "new"],
            "Conversation": ["save", "load", "list", "history"],
            "Configuration": ["model", "tools", "vectorstore"],
            "Tools": ["toggle"],
            "Information": ["inspect"],
        }
        
        result = {}
        for category, command_names in categories.items():
            result[category] = [self.commands[name] for name in command_names if name in self.commands]
        
        return result
```

## Future Extensibility

### Plugin System Foundation

The modular architecture enables future plugin capabilities:

```python
# Future: Plugin loading
class CommandRegistry:
    def load_plugin_commands(self, plugin_module: str):
        """Load commands from external plugin modules."""
        # Dynamic import and registration
        pass
    
    def register_custom_command(self, command: ChatCommand):
        """Register custom user-defined commands."""
        self.register(command)
```

### Third-Party Command Example

```python
# External plugin: my_custom_commands.py
class ProjectCommand(ChatCommand):
    name = "project"
    description = "Manage project-specific settings"
    aliases = ["proj"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        # Custom project management logic
        return True
```

## Testing Strategy

### Modular Testing

Each command module can be tested independently:

```python
# test_session_commands.py
def test_exit_command():
    command = ExitCommand()
    assert command.name == "exit"
    assert "quit" in command.aliases
    
    # Test execution
    result = await command.execute("", mock_controller)
    assert result is False  # Should exit chat

# test_conversation_commands.py
def test_save_command():
    command = SaveCommand()
    result = await command.execute("test_save", mock_controller)
    assert result is True
    # Verify file was saved
```

## Consequences

### ✅ Positive
1. **Maintainability**: Much easier to maintain and extend
2. **Code Organization**: Clear separation of concerns
3. **Testing**: Isolated, focused unit tests
4. **Extensibility**: Plugin architecture foundation
5. **Developer Experience**: Easy to add new commands
6. **Type Safety**: Full type checking and validation

### ⚠️ Considerations
1. **File Count**: More files to manage (but better organized)
2. **Import Complexity**: More import statements needed
3. **Learning Curve**: Developers need to understand module structure

### 🔄 Migration Impact
1. **Backward Compatibility**: All existing commands work identically
2. **User Experience**: No changes to user-facing command interface
3. **Development**: New commands follow modular pattern

## Related ADRs

- **ADR-005**: Interactive Chat Mode Implementation (updated for modular commands)
- **ADR-012**: Chat-First Architecture Migration (enables command system importance)
- **ADR-007**: Typed-Only Architecture Migration (provides type safety foundation)

---

**Key Insight**: The modular command system transforms chat commands from a monolithic structure into a maintainable, extensible architecture that scales with the growing importance of chat as the primary interface.
