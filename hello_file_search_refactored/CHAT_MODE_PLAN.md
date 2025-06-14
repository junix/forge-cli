# Multi-Turn Chat Mode Implementation Plan

## Overview

Transform the single-turn query tool into an interactive multi-turn chat application while maintaining backward compatibility.

## Requirements Analysis

### Functional Requirements
1. **Interactive Chat Loop**: Continuous conversation with the AI
2. **Context Preservation**: Maintain conversation history across turns
3. **Command System**: Built-in commands for chat control
4. **Display Management**: Clear visual separation of turns
5. **Session Management**: Save/load conversations
6. **Tool Persistence**: Maintain tool configuration across turns

### Non-Functional Requirements
1. **Backward Compatibility**: Single-turn mode still works
2. **Performance**: Efficient handling of long conversations
3. **User Experience**: Intuitive and responsive interface
4. **Error Recovery**: Graceful handling of failures

## Architecture Design

### New Components

#### 1. **Conversation Management** (`models/conversation.py`)
```python
@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str
    id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationState:
    messages: List[Message]
    session_id: str
    created_at: float
    model: str
    tools: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def add_message(self, message: Message) -> None: ...
    def to_api_format(self) -> List[Dict[str, Any]]: ...
    def clear(self) -> None: ...
    def save(self, path: Path) -> None: ...
    @classmethod
    def load(cls, path: Path) -> 'ConversationState': ...
```

#### 2. **Chat Controller** (`chat/controller.py`)
```python
class ChatController:
    def __init__(self, config: SearchConfig, display: BaseDisplay):
        self.conversation = ConversationState()
        self.commands = CommandRegistry()
        
    async def start_chat_loop(self) -> None: ...
    async def process_input(self, user_input: str) -> bool: ...
    async def handle_command(self, command: str, args: str) -> bool: ...
    async def send_message(self, content: str) -> None: ...
```

#### 3. **Command System** (`chat/commands.py`)
```python
class ChatCommand(ABC):
    name: str
    description: str
    aliases: List[str] = []
    
    @abstractmethod
    async def execute(self, args: str, controller: ChatController) -> bool: ...

class ExitCommand(ChatCommand):
    name = "exit"
    description = "Exit the chat"
    aliases = ["quit", "bye"]

class ClearCommand(ChatCommand):
    name = "clear"
    description = "Clear conversation history"

class SaveCommand(ChatCommand):
    name = "save"
    description = "Save conversation to file"

# Additional commands: /help, /model, /tools, /load, /history
```

#### 4. **Chat Display** (`display/chat_display.py`)
```python
class ChatDisplayMixin:
    """Mixin for chat-specific display functionality"""
    
    async def show_welcome(self, config: SearchConfig) -> None: ...
    async def show_user_message(self, message: str) -> None: ...
    async def show_assistant_message(self, message: str) -> None: ...
    async def show_conversation_history(self, messages: List[Message]) -> None: ...
    async def prompt_for_input(self) -> str: ...
```

### Modified Components

#### 1. **Main Entry Point** (`main.py`)
```python
async def main():
    # ... existing argument parsing ...
    
    # Add chat mode argument
    parser.add_argument(
        "--chat", "--interactive", "-i",
        action="store_true",
        help="Start interactive chat mode"
    )
    
    if args.chat:
        await start_chat_mode(config)
    else:
        # Existing single-turn mode
        await process_search(config, args.question)
```

#### 2. **Stream Handler Updates**
- Add support for message history in requests
- Handle conversation context in responses
- Track tool usage across turns

#### 3. **Display Updates**
- Add chat-specific methods to display classes
- Implement conversation rendering
- Handle input prompting

## Implementation Steps

### Phase 1: Core Infrastructure
1. Create conversation model classes
2. Implement basic chat controller
3. Add chat mode flag to CLI
4. Create simple chat loop

### Phase 2: Command System
1. Design command interface
2. Implement core commands (/exit, /clear, /help)
3. Add command registry and parser
4. Integrate with chat controller

### Phase 3: Display Enhancement
1. Update display interfaces for chat
2. Implement conversation rendering
3. Add rich formatting for chat mode
4. Handle long conversation display

### Phase 4: Advanced Features
1. Implement save/load functionality
2. Add conversation search
3. Tool management commands
4. Session persistence

### Phase 5: Testing & Polish
1. Test multi-turn conversations
2. Test command functionality
3. Performance optimization
4. Documentation updates

## User Interface Design

### Chat Mode Interface
```
╭─ Knowledge Forge Chat ─────────────────────────────────────╮
│ Model: qwen-max-latest | Tools: file-search, web-search    │
│ Session: 2024-01-14-001 | Messages: 0                      │
╰─────────────────────────────────────────────────────────────╯

Welcome to Knowledge Forge Chat! Type /help for commands.

You: What documents are available about 云学堂?

🔄 Searching documents...

Assistant: I found 1 document about 云学堂:

📄 **云学堂员工差旅管理办法 (V2.0)** - This document contains
the travel expense management policies for YunXueTang employees,
including hotel standards, transportation rules, and reimbursement
procedures.

You: /help

📋 Available Commands:
  /help, /h     - Show this help message
  /exit, /quit  - Exit the chat
  /clear        - Clear conversation history
  /save [file]  - Save conversation to file
  /load [file]  - Load conversation from file
  /model        - Show/change model
  /tools        - Show/manage tools
  /history      - Show conversation history
  /new          - Start new conversation

You: What's the reimbursement process?

🔄 Searching in context...
```

### Command Examples

```bash
# Start chat mode
uv run -m hello_file_search_refactored --chat

# Start chat with specific model
uv run -m hello_file_search_refactored --chat --model gpt-4

# Start chat with specific tools
uv run -m hello_file_search_refactored --chat -t file-search -t web-search

# Start chat with vector stores
uv run -m hello_file_search_refactored --chat --vec-id vec_123 vec_456
```

## Implementation Details

### Message History Management

The conversation state maintains full message history:

```python
# Convert to API format for requests
def to_api_format(self) -> List[Dict[str, Any]]:
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "id": msg.id or f"{msg.role}_msg_{i}"
        }
        for i, msg in enumerate(self.messages)
    ]
```

### Command Parsing

```python
def parse_command(input_text: str) -> tuple[str, str]:
    """Parse command and arguments from user input."""
    if not input_text.startswith('/'):
        return None, None
    
    parts = input_text[1:].split(' ', 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''
    return command, args
```

### Error Handling in Chat Mode

1. **Network Errors**: Retry with exponential backoff
2. **API Errors**: Display error message, maintain conversation
3. **Command Errors**: Show help for invalid commands
4. **Interrupt Handling**: Save conversation on Ctrl+C

## Benefits of Chat Mode

1. **Context Awareness**: Follow-up questions understand previous context
2. **Tool Continuity**: Search results available across turns
3. **Session Management**: Save and resume conversations
4. **Better UX**: Natural conversation flow
5. **Debugging**: Full conversation history for troubleshooting

## Technical Challenges and Solutions

### Challenge 1: Long Conversations
**Solution**: Implement conversation truncation with sliding window

### Challenge 2: Display Updates
**Solution**: Use Rich's Live display for smooth updates

### Challenge 3: State Persistence
**Solution**: JSON serialization with metadata preservation

### Challenge 4: Command Conflicts
**Solution**: Escape mechanism for messages starting with /

## Summary

The chat mode transformation enhances the tool from a single-query utility to a full conversational AI assistant, while maintaining the modular architecture that makes such enhancements straightforward.