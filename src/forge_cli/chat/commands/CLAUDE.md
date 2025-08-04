# Chat Commands - Modular Command System

## Overview

The chat commands module implements a modular command system for interactive chat mode, following ADR-013 (Modular Chat Command System). It provides 13+ built-in commands with auto-completion, extensible architecture, and comprehensive functionality for managing chat sessions, tools, and configuration.

## Directory Structure

```
commands/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Command exports and registry
├── base.py                      # Base command interface and utilities
├── config.py                    # Configuration management commands
├── conversation.py              # Conversation management commands
├── files.py                     # File management commands
├── info.py                      # Information and help commands
├── session.py                   # Session management commands
└── tool.py                      # Tool management commands
```

## Architecture & Design

### Modular Command Architecture (ADR-013)

The command system follows a modular design with:

1. **Base Command Interface**: Common functionality and patterns
2. **Category-Based Organization**: Commands grouped by functionality
3. **Registry Pattern**: Dynamic command registration and discovery
4. **Auto-Completion**: Built-in tab completion for commands and arguments
5. **Help System**: Comprehensive help and usage information

### Command Categories

#### Session Management (session.py)
- `/save` - Save conversation to file
- `/load` - Load conversation from file
- `/clear` - Clear conversation history
- `/exit` - Exit chat mode

#### Tool Management (tool.py)
- `/tools` - Show active tools
- `/enable-file-search` - Enable file search tool
- `/disable-file-search` - Disable file search tool
- `/enable-web-search` - Enable web search tool
- `/disable-web-search` - Disable web search tool
- `/enable-page-reader` - Enable page reader tool
- `/disable-page-reader` - Disable page reader tool

#### Configuration (config.py)
- `/config` - Show current configuration
- `/model` - Change AI model
- `/set` - Set configuration values

#### Information (info.py)
- `/help` - Show available commands
- `/info` - Show session information
- `/status` - Show system status

#### File Management (files.py)
- `/upload` - Upload files
- `/list-files` - List uploaded files
- `/create-vectorstore` - Create vector store

#### Conversation (conversation.py)
- `/history` - Show conversation history
- `/export` - Export conversation
- `/stats` - Show conversation statistics

## Base Command Interface

### Command Protocol

```python
from typing import Protocol, Optional
from forge_cli.models.conversation import Conversation

class ChatCommand(Protocol):
    """Protocol for chat commands."""
    
    name: str
    description: str
    usage: str
    
    def execute(self, args: list[str], conversation: Conversation) -> Optional[str]:
        """Execute the command with given arguments."""
        ...
    
    def get_completions(self, partial: str) -> list[str]:
        """Get auto-completion suggestions."""
        ...
```

### Base Command Implementation

```python
# base.py - Base command functionality
from abc import ABC, abstractmethod
from typing import Optional, List

class BaseCommand(ABC):
    """Base class for chat commands."""
    
    def __init__(self, name: str, description: str, usage: str):
        self.name = name
        self.description = description
        self.usage = usage
    
    @abstractmethod
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        """Execute the command."""
        pass
    
    def get_completions(self, partial: str) -> List[str]:
        """Default completion implementation."""
        return []
    
    def validate_args(self, args: List[str], min_args: int = 0, max_args: int = None) -> bool:
        """Validate command arguments."""
        if len(args) < min_args:
            return False
        if max_args is not None and len(args) > max_args:
            return False
        return True
    
    def format_error(self, message: str) -> str:
        """Format error message."""
        return f"Error: {message}\nUsage: {self.usage}"
```

## Command Implementations

### Session Management Commands

```python
# session.py - Session management
class SaveCommand(BaseCommand):
    """Save conversation to file."""
    
    def __init__(self):
        super().__init__(
            name="save",
            description="Save conversation to file",
            usage="/save [filename]"
        )
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        filename = args[0] if args else f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            conversation.save_to_file(filename)
            return f"Conversation saved to {filename}"
        except Exception as e:
            return self.format_error(f"Failed to save: {e}")
    
    def get_completions(self, partial: str) -> List[str]:
        # File completion logic
        return [f for f in os.listdir('.') if f.startswith(partial) and f.endswith('.json')]

class LoadCommand(BaseCommand):
    """Load conversation from file."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        if not self.validate_args(args, min_args=1, max_args=1):
            return self.format_error("Filename required")
        
        filename = args[0]
        try:
            conversation.load_from_file(filename)
            return f"Conversation loaded from {filename}"
        except Exception as e:
            return self.format_error(f"Failed to load: {e}")
```

### Tool Management Commands

```python
# tool.py - Tool management
class ToolsCommand(BaseCommand):
    """Show active tools."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        active_tools = conversation.get_active_tools()
        if not active_tools:
            return "No tools currently active"
        
        result = "Active tools:\n"
        for tool in active_tools:
            result += f"  - {tool.name}: {tool.description}\n"
        return result

class EnableFileSearchCommand(BaseCommand):
    """Enable file search tool."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        vector_store_ids = args if args else []
        
        if not vector_store_ids:
            return self.format_error("Vector store IDs required")
        
        conversation.enable_file_search(vector_store_ids)
        return f"File search enabled with vector stores: {', '.join(vector_store_ids)}"
    
    def get_completions(self, partial: str) -> List[str]:
        # Vector store ID completion
        return [vs_id for vs_id in get_available_vector_stores() if vs_id.startswith(partial)]
```

### Configuration Commands

```python
# config.py - Configuration management
class ConfigCommand(BaseCommand):
    """Show current configuration."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        config = conversation.get_config()
        result = "Current configuration:\n"
        result += f"  Model: {config.model}\n"
        result += f"  Temperature: {config.temperature}\n"
        result += f"  Tools: {', '.join(config.tools)}\n"
        return result

class ModelCommand(BaseCommand):
    """Change AI model."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        if not self.validate_args(args, min_args=1, max_args=1):
            return self.format_error("Model name required")
        
        model = args[0]
        conversation.set_model(model)
        return f"Model changed to: {model}"
    
    def get_completions(self, partial: str) -> List[str]:
        available_models = ["gpt-4", "gpt-3.5-turbo", "qwen-max-latest"]
        return [model for model in available_models if model.startswith(partial)]
```

### Information Commands

```python
# info.py - Information and help
class HelpCommand(BaseCommand):
    """Show available commands."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        from . import get_all_commands
        
        commands = get_all_commands()
        result = "Available commands:\n"
        
        for category, cmds in commands.items():
            result += f"\n{category}:\n"
            for cmd in cmds:
                result += f"  /{cmd.name} - {cmd.description}\n"
        
        result += "\nType /help <command> for detailed usage information."
        return result

class InfoCommand(BaseCommand):
    """Show session information."""
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        stats = conversation.get_statistics()
        result = "Session Information:\n"
        result += f"  Messages: {stats.message_count}\n"
        result += f"  Tokens used: {stats.total_tokens}\n"
        result += f"  Session duration: {stats.duration}\n"
        result += f"  Active tools: {len(stats.active_tools)}\n"
        return result
```

## Command Registry

### Dynamic Registration

```python
# __init__.py - Command registry
from typing import Dict, List, Type
from .base import BaseCommand

class CommandRegistry:
    """Registry for chat commands."""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
        self._categories: Dict[str, List[BaseCommand]] = {}
    
    def register(self, command: BaseCommand, category: str = "General") -> None:
        """Register a command."""
        self._commands[command.name] = command
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(command)
    
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """Get command by name."""
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, List[BaseCommand]]:
        """Get all commands by category."""
        return self._categories.copy()
    
    def get_completions(self, partial: str) -> List[str]:
        """Get command name completions."""
        return [name for name in self._commands.keys() if name.startswith(partial)]

# Global registry instance
_registry = CommandRegistry()

def register_command(command: BaseCommand, category: str = "General") -> None:
    """Register a command globally."""
    _registry.register(command, category)

def get_command(name: str) -> Optional[BaseCommand]:
    """Get command by name."""
    return _registry.get_command(name)

# Register built-in commands
def _register_builtin_commands():
    """Register all built-in commands."""
    # Session commands
    register_command(SaveCommand(), "Session")
    register_command(LoadCommand(), "Session")
    register_command(ClearCommand(), "Session")
    
    # Tool commands
    register_command(ToolsCommand(), "Tools")
    register_command(EnableFileSearchCommand(), "Tools")
    register_command(DisableFileSearchCommand(), "Tools")
    
    # Configuration commands
    register_command(ConfigCommand(), "Configuration")
    register_command(ModelCommand(), "Configuration")
    
    # Information commands
    register_command(HelpCommand(), "Help")
    register_command(InfoCommand(), "Help")

# Initialize built-in commands
_register_builtin_commands()
```

## Auto-Completion System

### Completion Engine

```python
class CompletionEngine:
    """Auto-completion engine for chat commands."""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
    
    def get_completions(self, text: str) -> List[str]:
        """Get completions for input text."""
        if not text.startswith('/'):
            return []
        
        parts = text[1:].split(' ')
        command_name = parts[0]
        
        if len(parts) == 1:
            # Complete command name
            return [f"/{name}" for name in self.registry.get_completions(command_name)]
        else:
            # Complete command arguments
            command = self.registry.get_command(command_name)
            if command:
                partial_arg = parts[-1]
                return command.get_completions(partial_arg)
        
        return []
```

## Usage Examples

### Command Execution

```python
# In chat controller
def execute_command(self, input_text: str) -> Optional[str]:
    """Execute a chat command."""
    if not input_text.startswith('/'):
        return None
    
    parts = input_text[1:].split()
    command_name = parts[0]
    args = parts[1:]
    
    command = get_command(command_name)
    if not command:
        return f"Unknown command: /{command_name}. Type /help for available commands."
    
    try:
        return command.execute(args, self.conversation)
    except Exception as e:
        return f"Command error: {e}"
```

### Custom Command

```python
class CustomCommand(BaseCommand):
    """Example custom command."""
    
    def __init__(self):
        super().__init__(
            name="custom",
            description="Custom command example",
            usage="/custom <arg1> [arg2]"
        )
    
    def execute(self, args: List[str], conversation: Conversation) -> Optional[str]:
        if not self.validate_args(args, min_args=1):
            return self.format_error("At least one argument required")
        
        # Custom logic here
        return f"Custom command executed with args: {args}"
    
    def get_completions(self, partial: str) -> List[str]:
        # Custom completion logic
        return ["option1", "option2", "option3"]

# Register custom command
register_command(CustomCommand(), "Custom")
```

## Related Components

- **Chat Controller** (`../controller.py`) - Uses commands for chat interaction
- **Conversation Models** (`../../models/conversation.py`) - Data structures used by commands
- **Configuration** (`../../config.py`) - Configuration management
- **SDK** (`../../sdk/`) - API operations used by commands

## Best Practices

### Command Development

1. **Follow Protocol**: Implement the BaseCommand interface consistently
2. **Validate Arguments**: Use validate_args for argument checking
3. **Error Handling**: Provide clear error messages with usage information
4. **Auto-Completion**: Implement meaningful auto-completion
5. **Documentation**: Include comprehensive help and usage information

### Registry Management

1. **Category Organization**: Group related commands in categories
2. **Name Consistency**: Use clear, consistent command naming
3. **Conflict Resolution**: Handle command name conflicts appropriately
4. **Dynamic Loading**: Support dynamic command registration
5. **Testing**: Include comprehensive tests for all commands

The chat commands module provides a flexible, extensible foundation for interactive chat functionality with comprehensive built-in commands and easy customization options.
