# Conversation State Tool Management & Resume Functionality

This document describes the enhanced conversation state management system that allows per-conversation tool configuration, vector store management, and conversation resumption by ID.

## Overview

The conversation state now maintains its own tool configuration that can be modified during chat sessions. This allows users to:

1. Enable/disable web search per conversation
2. Enable/disable file search per conversation
3. Set and modify vector store IDs per conversation
4. Persist these settings across save/load operations
5. Resume conversations by unique ID from command line
6. Automatic conversation management with ID-based file naming

## Conversation IDs

Each conversation now has a unique identifier:

- **Format**: `conv_xxxxxxxx` (8 hexadecimal characters)
- **Purpose**: Used for file naming, resuming conversations, and identification
- **Storage**: Conversations are saved as `<conversation_id>.json` in `~/.forge-cli/conversations/`
- **Backward Compatibility**: Old conversations without IDs get auto-generated IDs

## New Fields in ConversationState

The `ConversationState` class now includes these additional fields:

```python
@dataclass
class ConversationState:
    # ... existing fields ...

    # Unique conversation identifier
    conversation_id: ConversationId = field(default_factory=lambda: ConversationId(f"conv_{uuid.uuid4().hex[:8]}"))

    # Conversation-specific tool settings
    web_search_enabled: bool = False
    file_search_enabled: bool = False
    current_vector_store_ids: list[str] = field(default_factory=list)
```

## New Methods

### Tool Management Methods

```python
# Web search control
conversation.enable_web_search()
conversation.disable_web_search()
conversation.is_web_search_enabled() -> bool

# File search control
conversation.enable_file_search()
conversation.disable_file_search()
conversation.is_file_search_enabled() -> bool

# Vector store management
conversation.set_vector_store_ids(["vs_123", "vs_456"])
conversation.get_current_vector_store_ids() -> list[str]
```

## Command Line Options

### Resume Existing Conversation

```bash
# Resume a conversation by ID
forge-cli --resume conv_abc12345
forge-cli -r conv_abc12345

# Start new chat session
forge-cli --chat
```

## Chat Commands

### Conversation Management

```bash
# List all saved conversations
/conversations  # or /convs, /list

# Save current conversation (uses conversation ID as filename)
/save

# Save with custom filename
/save my_conversation

# Load conversation by ID or filename
/load conv_abc12345
/load my_conversation.json
```

### Vector Store Management (`/vectorstore`, `/vs`, `/vec`)

Manage vector store IDs for file search:

```bash
# Show current configuration
/vectorstore

# Set vector store IDs (replaces existing)
/vectorstore set vs_123 vs_456

# Add a vector store ID
/vectorstore add vs_789

# Remove a vector store ID
/vectorstore remove vs_456

# Clear all vector store IDs
/vectorstore clear
```

### Tool Toggle Commands

Enable/disable tools for the current conversation:

```bash
# Web search
/enable-web-search   # or /ews
/disable-web-search  # or /dws

# File search
/enable-file-search  # or /efs
/disable-file-search # or /dfs
```

## Priority System

The system uses a priority-based approach for tool configuration:

1. **Conversation State** (highest priority) - Settings modified during chat
2. **Global Config** (fallback) - Command-line arguments and defaults

When generating requests, the system:
- Uses conversation state settings if available
- Falls back to global config if conversation state is not set
- Combines both sources intelligently (e.g., conversation vector store IDs + global config max_results)

## Automatic Behaviors

### Auto-enable/disable

- Setting vector store IDs automatically enables file search if not already enabled
- Clearing all vector store IDs automatically disables file search if enabled
- Tool toggle commands update both global config and conversation state

### Backward Compatibility

- Old conversation files without new fields load with default values (disabled tools, empty vector store IDs)
- If `used_vector_store_ids` exists but `current_vector_store_ids` is empty, the system initializes `current_vector_store_ids` from `used_vector_store_ids`

## Persistence

All conversation-specific tool settings and IDs are automatically saved and loaded:

```json
{
  "conversation_id": "conv_abc12345",
  "session_id": "session_abc123",
  "web_search_enabled": true,
  "file_search_enabled": true,
  "current_vector_store_ids": ["vs_123", "vs_456"],
  // ... other fields
}
```

### File Storage

- **Location**: `~/.forge-cli/conversations/`
- **Naming**: `<conversation_id>.json`
- **Auto-creation**: Directory created automatically on first save
- **Examples**:
  - `conv_abc12345.json`
  - `conv_def67890.json`

## Example Usage

### During Chat Session

```bash
# Start new chat
forge-cli --chat

# Check current tools
/vectorstore
# Output: 📁 No vector store IDs configured
#         🔍 File search is disabled

# Configure file search
/vectorstore set vs_abc123 vs_def456
# Output: ✅ Set vector store IDs: vs_abc123, vs_def456
#         🔍 Auto-enabled file search

# Enable web search
/enable-web-search
# Output: ✅ Web search enabled

# Save conversation (uses conversation ID)
/save
# Output: 💾 Conversation saved as: conv_abc12345
#         📁 Location: ~/.forge-cli/conversations/conv_abc12345.json

# List all conversations
/conversations
# Output: 💬 Saved Conversations:
#         ID           Created             Msgs  Model
#         conv_abc12345 2025-06-16 10:30:15 4     qwen-max-latest

# Exit and resume later
/exit

# Resume the conversation
forge-cli --resume conv_abc12345
# Output: 📂 Resumed conversation conv_abc12345 with 4 messages
```

### Programmatic Usage

```python
from forge_cli.models.conversation import ConversationState
from forge_cli.config import AppConfig

# Create conversation
conversation = ConversationState()

# Configure tools
conversation.enable_web_search()
conversation.enable_file_search()
conversation.set_vector_store_ids(["vs_123"])

# Create request (conversation state takes priority)
config = AppConfig()  # May have different settings
request = conversation.new_request("Your question", config)

# Request will use conversation state settings
```

## Benefits

1. **Per-conversation Configuration**: Each conversation can have its own tool settings
2. **Dynamic Changes**: Modify tools during chat without restarting
3. **Persistence**: Settings survive save/load cycles
4. **Priority System**: Conversation-specific settings override global defaults
5. **Backward Compatibility**: Existing conversations continue to work
6. **User-friendly Commands**: Easy-to-use chat commands for configuration
7. **Conversation Resume**: Continue conversations from where you left off
8. **Automatic ID Management**: No need to manually name conversation files
9. **Centralized Storage**: All conversations organized in one directory
10. **Quick Access**: List and load conversations by ID
