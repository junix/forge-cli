# /inspect Command Implementation

## Overview

This document describes the implementation of the new `/inspect` command for the CLI application. The command displays comprehensive session state information including token usage, conversation metrics, vector store information, file usage tracking, and model configuration.

## Implementation Summary

### Files Modified

1. **`src/forge_cli/models/conversation.py`**
   - Added `accessed_files: set[str]` field to track files accessed during the session
   - Added `turn_count: int` field to track conversation turns
   - Added methods: `add_accessed_file()`, `add_accessed_files()`, `get_accessed_files()`, `increment_turn_count()`
   - Updated `save()` and `load()` methods to persist new fields

2. **`src/forge_cli/chat/commands.py`**
   - Added `InspectCommand` class with comprehensive state display functionality
   - Registered the command in `CommandRegistry` with aliases: `i`, `status`, `info`

3. **`src/forge_cli/chat/controller.py`**
   - Added turn count increment on each user message
   - Added file access tracking integration with stream handler

4. **`src/forge_cli/stream/handler_typed.py`**
   - Added `get_accessed_files()` method to retrieve files accessed during streaming

## Features Implemented

### 1. Token Usage Statistics
- **Display Format**: "Input: X tokens, Output: Y tokens, Total: Z tokens"
- **Source**: `ConversationState.usage` (ResponseUsage object)
- **Fallback**: "No token usage data available" if no usage data

### 2. Conversation Metrics
- **Display Format**: "Turn: X"
- **Source**: `ConversationState.turn_count`
- **Tracking**: Incremented on each user message in the main chat loop

### 3. Vector Store Information
- **Display Format**: "• [ID] - [Name]" (bulleted list)
- **Source**: `SearchConfig.vec_ids` with API lookup for names
- **Fallback**: Shows just IDs if API call fails, "None" if no vector stores configured

### 4. File Usage Tracking
- **Display Format**: Bulleted list with file paths relative to workspace root
- **Source**: `ConversationState.accessed_files`
- **Tracking**: Files accessed through file search tool calls during streaming
- **Fallback**: "No files accessed in this session" if no files

### 5. Model Configuration
- **Display Format**: "Model: [model-name]"
- **Source**: `ConversationState.model`

## Command Usage

```bash
/inspect
/i
/status
/info
```

All aliases provide the same functionality.

## Technical Details

### Data Flow

1. **File Access Tracking**:
   ```
   Stream Handler → extract file mappings → get_accessed_files() → 
   ChatController → add_accessed_files() → ConversationState.accessed_files
   ```

2. **Turn Counting**:
   ```
   User Message → main.py handle_user_message() → increment_turn_count() →
   ConversationState.turn_count
   ```

3. **Token Usage**:
   ```
   API Response → ResponseUsage → ConversationState.add_token_usage() → 
   ConversationState.usage
   ```

### State Persistence

The new fields are automatically saved and loaded with conversation state:
- `accessed_files` → saved as list, loaded as set
- `turn_count` → saved and loaded as integer
- Backward compatibility maintained with default values

### Error Handling

- **Missing Dependencies**: Graceful fallback for vector store API calls
- **No Data**: Appropriate "Not available" messages for missing information
- **API Failures**: Shows IDs only if vector store name lookup fails

## Display Format

The command uses Rich library components:
- **Table**: Organized display with categories and details
- **Panel**: Bordered container with title "Session Inspector"
- **Styling**: Color-coded categories (cyan headers, white content)

## Testing

A comprehensive test suite (`test_inspect_command.py`) validates:
- ✅ ConversationState new fields and methods
- ✅ InspectCommand definition and registration
- ✅ TypedStreamHandler file tracking
- ✅ ChatController integration

## Future Enhancements

Potential improvements for future versions:
1. **Performance Metrics**: Response times, API call latencies
2. **Memory Usage**: Track conversation memory consumption
3. **Tool Usage Statistics**: Count of tool calls by type
4. **Export Functionality**: Save session state to file
5. **Historical Data**: Compare with previous sessions

## Example Output

```
┌─────────────────── Session Inspector ───────────────────┐
│                📊 Session State Information              │
│                                                          │
│ 🔢 Token Usage      Input: 1,234 tokens, Output: 567    │
│                     tokens, Total: 1,801 tokens         │
│                                                          │
│ 💬 Conversation     Turn: 5                             │
│                                                          │
│ 🗂️ Vector Store     • vs_abc123 - Support Documents     │
│                     • vs_def456 - Knowledge Base        │
│                                                          │
│ 🤖 Model            Model: qwen-max-latest              │
│                                                          │
│ 📁 Files Accessed   • documents/user_guide.pdf         │
│                     • policies/privacy_policy.md       │
│                     • faq/common_questions.txt          │
└──────────────────────────────────────────────────────────┘
```

## Compatibility

- **Backward Compatible**: Existing conversations load correctly with default values
- **Type Safe**: All new code follows existing type annotation patterns
- **Error Resilient**: Graceful handling of missing data or API failures
