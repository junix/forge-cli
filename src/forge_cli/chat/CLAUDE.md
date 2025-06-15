# Chat Module - Interactive Chat Mode System

## Overview

The chat module implements a sophisticated interactive chat mode for the Forge CLI, enabling multi-turn conversations with context preservation, command system, and session management. It provides a rich, terminal-based chat experience similar to modern chat applications while maintaining the power and flexibility of command-line tools.

## Directory Structure

```
chat/
├── __init__.py      # Module exports
├── controller.py    # Main chat session controller
└── commands.py      # Command system and handlers
```

## Architecture & Design

### Design Principles

1. **Stateful Conversations**: Maintain full conversation history
2. **Command-Driven**: Rich command system for chat control
3. **Extensible**: Easy to add new commands and features
4. **User-Friendly**: Intuitive interface with helpful feedback
5. **Persistent**: Save and load conversation sessions

### Chat Flow Architecture

```
User Input
    ↓
Command Parser (check for /)
    ├─ Command → Command Handler
    └─ Message → Conversation Manager
                      ↓
                 StreamHandler
                      ↓
                 Display Update
                      ↓
                 Save to History
```

## Component Details

### controller.py - Chat Controller

The `ChatController` manages the entire chat session lifecycle:

```python
class ChatController:
    """Main controller for interactive chat sessions."""
    
    def __init__(self, config: SearchConfig, display: BaseDisplay):
        self.config = config
        self.display = display
        self.conversation = Conversation()
        self.command_handler = CommandHandler(self)
        self.stream_handler = StreamHandler(display)
        self.session_file = None
        self.running = True
```

#### Key Methods

##### run()

Main chat loop:

```python
async def run(self):
    """Run the interactive chat session."""
    # Welcome message
    self._show_welcome()
    
    # Process initial query if provided
    if self.config.query:
        await self._process_message(self.config.query)
    
    # Main loop
    while self.running:
        try:
            # Get user input
            user_input = await self._get_user_input()
            
            if not user_input:
                continue
            
            # Process input (command or message)
            await self._process_input(user_input)
            
        except KeyboardInterrupt:
            self._handle_interrupt()
        except Exception as e:
            self._handle_error(e)
```

##### _process_input()

Routes input to command or message handler:

```python
async def _process_input(self, user_input: str):
    """Process user input as command or message."""
    
    # Check for command
    if user_input.startswith("/"):
        command, args = self._parse_command(user_input)
        await self.command_handler.execute(command, args)
    else:
        # Process as message
        await self._process_message(user_input)
```

##### _process_message()

Handles regular chat messages:

```python
async def _process_message(self, message: str):
    """Process a chat message."""
    # Add to conversation
    self.conversation.add_message(Message(
        role="user",
        content=message,
        timestamp=datetime.now()
    ))
    
    # Prepare API request
    messages = self.conversation.to_api_format()
    
    # Stream response
    stream = astream_response(
        input_messages=messages,
        model=self.config.model,
        tools=self._get_enabled_tools(), # This would now also potentially include 'code-analyzer'
        **self._get_api_params()
    )
    
    # Process stream
    self.display.handle_chat_start()
    state = await self.stream_handler.handle_stream(stream, message)
    
    # Save assistant response
    self.conversation.add_message(Message(
        role="assistant",
        content=state.get_complete_text(),
        metadata=state.to_dict()
    ))
    
    self.display.handle_chat_complete()
```

#### Session Management

```python
def save_session(self, filepath: str):
    """Save conversation to file."""
    session_data = {
        "conversation": self.conversation.to_dict(),
        "config": self.config.to_dict(),
        "metadata": {
            "created_at": self.conversation.created_at,
            "message_count": len(self.conversation.messages),
            "model": self.config.model,
            "tools": list(self.config.tools)
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def load_session(self, filepath: str):
    """Load conversation from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    self.conversation = Conversation.from_dict(
        session_data["conversation"]
    )
    # Restore config settings
    self._restore_config(session_data.get("config", {}))
```

### commands.py - Command System

Implements a comprehensive command system with aliases and help:

```python
class CommandHandler:
    """Handles chat commands and their execution."""
    
    def __init__(self, controller: ChatController):
        self.controller = controller
        self.commands = self._build_command_registry()
```

#### Command Registry

```python
def _build_command_registry(self) -> Dict[str, Command]:
    """Build the command registry with all available commands."""
    return {
        "help": Command(
            name="help",
            aliases=["h", "?"],
            description="Show available commands",
            handler=self._cmd_help
        ),
        "save": Command(
            name="save",
            aliases=["s"],
            description="Save conversation to file",
            handler=self._cmd_save,
            usage="/save [filename]"
        ),
        "load": Command(
            name="load",
            aliases=["l"],
            description="Load conversation from file",
            handler=self._cmd_load,
            usage="/load <filename>"
        ),
        "clear": Command(
            name="clear",
            aliases=["c", "new"],
            description="Clear conversation history",
            handler=self._cmd_clear
        ),
        "history": Command(
            name="history",
            aliases=["hist"],
            description="Show conversation history",
            handler=self._cmd_history
        ),
        "tools": Command(
            name="tools",
            aliases=["t"],
            description="Manage enabled tools",
            handler=self._cmd_tools,
            usage="/tools [list|enable|disable] [tool_name]"
        ),
        "model": Command(
            name="model",
            aliases=["m"],
            description="Change or show AI model",
            handler=self._cmd_model,
            usage="/model [model_name]"
        ),
        "retry": Command(
            name="retry",
            aliases=["r"],
            description="Retry last message",
            handler=self._cmd_retry
        ),
        "exit": Command(
            name="exit",
            aliases=["quit", "q"],
            description="Exit chat mode",
            handler=self._cmd_exit
        ),
        # Quick tool toggles
        "web": Command(
            name="web",
            aliases=["w"],
            description="Toggle web search",
            handler=self._cmd_toggle_web
        ),
        "file": Command(
            name="file",
            aliases=["f"],
            description="Toggle file search",
            handler=self._cmd_toggle_file
        ),
        "analyze": Command( # Or a more suitable short command
            name="analyze",
            aliases=["ca", "code"],
            description="Toggle code analyzer tool",
            handler=self._cmd_toggle_code_analyzer # Assumes a new handler _cmd_toggle_code_analyzer
        ),
        # Advanced commands
        "export": Command(
            name="export",
            aliases=["e"],
            description="Export conversation as markdown",
            handler=self._cmd_export
        ),
        "config": Command(
            name="config",
            aliases=["cfg"],
            description="Show current configuration",
            handler=self._cmd_config
        )
    }
```

#### Command Handlers

Example command implementations:

```python
async def _cmd_tools(self, args: List[str]):
    """Manage enabled tools."""
    if not args or args[0] == "list":
        # Show current tools
        enabled = self.controller.config.tools
        available = ["file-search", "web-search", "file-reader", "code-analyzer"]
        
        self.display.show_info("Available tools:")
        for tool in available:
            status = "✓" if tool in enabled else "✗"
            self.display.show_info(f"  {status} {tool}")
    
    elif args[0] == "enable" and len(args) > 1:
        tool = args[1]
        if tool not in self.controller.config.tools:
            self.controller.config.tools.add(tool)
            self.display.show_success(f"Enabled {tool}")
    
    elif args[0] == "disable" and len(args) > 1:
        tool = args[1]
        if tool in self.controller.config.tools:
            self.controller.config.tools.remove(tool)
            self.display.show_success(f"Disabled {tool}")

async def _cmd_history(self, args: List[str]):
    """Show conversation history."""
    if not self.controller.conversation.messages:
        self.display.show_info("No messages in history")
        return
    
    # Format history
    for i, msg in enumerate(self.controller.conversation.messages, 1):
        role_color = "blue" if msg.role == "user" else "green"
        self.display.show_message(
            f"[{role_color}][{i}] {msg.role.upper()}[/{role_color}]: "
            f"{msg.content[:100]}..."
        )
```

### Auto-completion Support

When `prompt_toolkit` is available, provides rich auto-completion:

```python
class ChatCompleter(Completer):
    """Auto-completion for chat commands."""
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        if text.startswith("/"):
            # Complete commands
            cmd_part = text[1:].lower()
            for cmd_name, command in self.commands.items():
                if cmd_name.startswith(cmd_part):
                    yield Completion(
                        cmd_name,
                        start_position=-len(cmd_part),
                        display_meta=command.description
                    )
```

## Usage Guidelines

### For Language Models

When working with the chat module:

1. **Starting a chat session**:

```python
from forge_cli.chat.controller import ChatController
from forge_cli.display.rich_display import RichDisplay
from forge_cli.config import SearchConfig

config = SearchConfig(
    model="gpt-4",
    tools={"file-search", "web-search"}
)
display = RichDisplay(config)
controller = ChatController(config, display)

# Run chat
await controller.run()
```

2. **Programmatic conversation**:

```python
# Add messages programmatically
controller.conversation.add_message(Message(
    role="system",
    content="You are a helpful assistant."
))

# Process a message
await controller._process_message("Hello!")

# Get conversation history
history = controller.conversation.to_api_format()
```

3. **Custom commands**:

```python
# Add custom command
async def custom_command_handler(args: List[str]):
    # Custom logic
    pass

controller.command_handler.register_command(Command(
    name="custom",
    description="My custom command",
    handler=custom_command_handler
))
```

## Development Guidelines

### Adding New Commands

1. **Define command in registry**:

```python
"new_command": Command(
    name="new_command",
    aliases=["nc", "new"],
    description="Description of command",
    handler=self._cmd_new_command,
    usage="/new_command <required> [optional]"
)
```

2. **Implement handler**:

```python
async def _cmd_new_command(self, args: List[str]):
    """Handle new command."""
    if not args:
        self.display.show_error("Missing required argument")
        return
    
    # Command logic
    result = await process_command(args[0])
    self.display.show_success(f"Command executed: {result}")
```

3. **Add to help system**:
The command automatically appears in `/help` output.

### Extending Chat Features

#### Custom Input Processing

```python
class CustomChatController(ChatController):
    async def _process_input(self, user_input: str):
        # Pre-process input
        if self._is_special_syntax(user_input):
            user_input = self._transform_syntax(user_input)
        
        # Call parent
        await super()._process_input(user_input)
```

#### Message Filtering

```python
def _prepare_messages(self) -> List[dict]:
    """Prepare messages for API with filtering."""
    messages = []
    
    for msg in self.conversation.messages:
        # Filter system messages older than 10 turns
        if msg.role == "system" and msg.age > 10:
            continue
            
        messages.append(msg.to_api_format())
    
    return messages
```

#### Context Management

```python
def _manage_context_window(self):
    """Manage conversation context to fit token limits."""
    total_tokens = self.conversation.estimate_tokens()
    
    if total_tokens > self.config.max_context_tokens:
        # Summarize old messages
        summary = self._summarize_old_messages()
        self.conversation.compress_history(summary)
```

## Best Practices

### Conversation Management

1. **Memory efficiency**:

```python
# Periodically clean old metadata
def cleanup_metadata(self):
    for msg in self.conversation.messages[:-10]:  # Keep last 10
        msg.metadata = {}  # Clear heavy metadata
```

2. **Error recovery**:

```python
async def _process_message_safe(self, message: str):
    try:
        await self._process_message(message)
    except Exception as e:
        # Save state before error
        self._autosave()
        
        # Show error to user
        self.display.show_error(f"Error: {e}")
        
        # Offer recovery
        self.display.show_info("Type /retry to try again")
```

3. **Auto-save**:

```python
def _autosave(self):
    """Auto-save conversation periodically."""
    if len(self.conversation.messages) % 10 == 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_session(f".chat_autosave_{timestamp}.json")
```

### User Experience

1. **Helpful prompts**:

```python
def _show_welcome(self):
    """Show welcome message with tips."""
    self.display.show_panel(
        "[bold]Welcome to Forge CLI Chat Mode[/bold]\n\n"
        "Tips:\n"
        "• Type /help for available commands\n"
        "• Use /web and /file to toggle search tools\n"
        "• Press Ctrl+C to cancel current operation\n"
        "• Type /exit to quit"
    )
```

2. **Progress indicators**:

```python
async def _process_message(self, message: str):
    # Show typing indicator
    self.display.show_typing_indicator()
    
    try:
        # Process message
        await self._actual_process(message)
    finally:
        # Clear indicator
        self.display.clear_typing_indicator()
```

## Testing Chat Components

```python
import pytest
from unittest.mock import Mock, AsyncMock

async def test_chat_controller():
    # Mock dependencies
    config = Mock(spec=SearchConfig)
    display = Mock(spec=BaseDisplay)
    
    # Create controller
    controller = ChatController(config, display)
    
    # Test message processing
    with patch('forge_cli.sdk.astream_response') as mock_stream:
        mock_stream.return_value = async_generator([
            ("response.output_text.delta", {"text": "Hello"})
        ])
        
        await controller._process_message("Hi")
        
        # Verify conversation updated
        assert len(controller.conversation.messages) == 2
        assert controller.conversation.messages[0].content == "Hi"
        assert controller.conversation.messages[1].content == "Hello"

async def test_command_execution():
    controller = ChatController(Mock(), Mock())
    handler = CommandHandler(controller)
    
    # Test help command
    await handler.execute("help", [])
    assert controller.display.show_info.called
```

## Integration Points

### With Stream Handler

Chat controller uses stream handler for responses:

```python
state = await self.stream_handler.handle_stream(stream, message)
# Extract response for conversation
response_text = state.get_complete_text()
```

### With Display Strategies

Chat mode enhances display with special methods:

```python
# Rich display shows chat-specific UI
display.handle_chat_start()  # Show assistant typing
display.handle_chat_complete()  # Finalize response
display.show_conversation_panel()  # Show history
```

### With Configuration

Chat respects and modifies configuration:

```python
# Tools can be toggled during chat
self.config.tools.add("web-search")
self.config.tools.remove("file-search")

# Model can be changed
self.config.model = "gpt-4-turbo"
```

## Future Enhancements

1. **Conversation Branching**: Save/restore conversation checkpoints
2. **Multi-modal Support**: Handle image inputs in chat
3. **Plugin System**: Custom processors for chat messages
4. **Rich Formatting**: Support for tables, code blocks in input
5. **Voice Input**: Integration with speech recognition
6. **Collaborative Mode**: Multiple users in same session

The chat module transforms the Forge CLI into a powerful conversational interface, providing users with an intuitive way to interact with the Knowledge Forge API while maintaining the flexibility and power of command-line tools.
