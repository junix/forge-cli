# Chat Mode Fix for Typed API

## Problem

When running `python -m forge_cli --chat`, the error occurred:
```
❌ Fatal error: AttributeError: 'ChatController' object has no attribute 'process_message'
```

## Root Causes

1. The main.py was trying to patch a non-existent `process_message` method
2. The actual method in ChatController is `send_message`
3. The ConversationState class has `to_api_format()` not `to_messages_list()`

## Solution

Fixed the `start_chat_mode` function in main.py to:

1. **Correctly patch the `send_message` method** instead of `process_message`
2. **Use the correct method** `to_api_format()` for getting conversation history
3. **Properly handle the typed API integration** in chat mode

### Key Changes

```python
# Before (incorrect)
original_process = controller.process_message  # ❌ Method doesn't exist

# After (correct)
original_send_message = controller.send_message  # ✅ Correct method

# Before (incorrect)
messages = controller.conversation.to_messages_list()  # ❌ Method doesn't exist

# After (correct)
messages = controller.conversation.to_api_format()  # ✅ Correct method
```

## Current Status

✅ Chat mode now works with the typed API:
- Can start chat mode: `python -m forge_cli --chat`
- Commands work: `/help`, `/exit`, etc.
- Messages can be sent and processed
- No AttributeError or other errors

## Implementation Details

The chat mode integration with typed API:

1. **Patches the send_message method** to use `astream_typed_response`
2. **Creates typed Request objects** with proper tools
3. **Uses TypedStreamHandler** for processing events
4. **Extracts assistant responses** from the typed state

## Testing

```bash
# Start chat mode
python -m forge_cli --chat

# With tools
python -m forge_cli --chat -t file-search --vec-id vs_123

# With initial question
python -m forge_cli --chat -q "Hello"
```

All modes now work correctly with the typed API!