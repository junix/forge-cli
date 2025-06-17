# Dynamic Prompt with Tool Icons Implementation

## Overview

The Forge CLI chat prompt now dynamically displays icons based on which tools are enabled in the conversation. This provides immediate visual feedback about the active tools.

## Implementation Details

### Modified Files

1. **`src/forge_cli/chat/inputs.py`**
   - Added `ConversationState` import
   - Modified `__init__` to accept conversation state
   - Enhanced `_get_interactive_input()` to build dynamic prompts with icons
   - Added color styling for different tool types

2. **`src/forge_cli/chat/controller.py`**
   - Updated `InputHandler` initialization to pass conversation state

### Prompt Styles

The prompt displays different icons based on enabled tools:

| Tools Enabled | Prompt Display | Description |
|--------------|----------------|-------------|
| None | `>> ` | Default prompt with no tools |
| Web Search | `[🌐] >> ` | Globe icon in green |
| File Search | `[📁] >> ` | Folder icon in yellow |
| Both | `[🌐 📁] >> ` | Both icons with space between |

### Color Scheme

```python
style = Style.from_dict({
    "prompt": "bold cyan",      # Main prompt chevrons
    "tool_web": "bold green",   # Web search icon
    "tool_file": "bold yellow", # File search icon
    "tool_bracket": "bold white", # Brackets around icons
    "": "#ffffff",              # Default text color
})
```

### How It Works

1. When creating the prompt, the `InputHandler` checks:
   - `conversation.web_search_enabled` for web search status
   - `conversation.file_search_enabled` for file search status

2. Based on enabled tools, it builds a `FormattedText` list with:
   - Opening bracket `[` (if any tools enabled)
   - Tool icons with appropriate colors
   - Closing bracket `]` (if any tools enabled)
   - Standard prompt `>> `

3. The prompt updates automatically when tools are toggled using commands like:
   - `/enable-web` or `/disable-web`
   - `/enable-files` or `/disable-files`
   - `/vectorstore set <id>` (auto-enables file search)

## Usage Examples

### Starting with Tools

```bash
# Start with web search enabled
python -m forge_cli.main -t web-search
# Prompt: [🌐] >> 

# Start with file search enabled
python -m forge_cli.main -t file-search --vec-id vec_123
# Prompt: [📁] >> 

# Start with both tools
python -m forge_cli.main -t web-search -t file-search --vec-id vec_123
# Prompt: [🌐 📁] >> 
```

### Dynamic Toggle in Chat

```
>> /enable-web
✓ Web search enabled
[🌐] >> /enable-files
✓ File search enabled
[🌐 📁] >> /disable-web
✓ Web search disabled
[📁] >> 
```

## Benefits

1. **Visual Feedback**: Users instantly see which tools are active
2. **Color Coding**: Different colors help distinguish tool types
3. **Clean Design**: Icons only appear when tools are enabled
4. **Accessibility**: Icons are accompanied by color for better visibility

## Future Enhancements

1. **More Tool Icons**: Add icons for additional tools (e.g., 🔍 for code analyzer)
2. **Customizable Icons**: Allow users to configure their preferred icons
3. **Status Indicators**: Show connection status or error states in prompt
4. **Animation**: Pulse or animate icons during tool execution