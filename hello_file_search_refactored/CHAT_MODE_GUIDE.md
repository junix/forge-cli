# Chat Mode User Guide

## Overview

The refactored hello-file-search now supports interactive multi-turn chat mode, allowing continuous conversations with context preservation.

## Starting Chat Mode

```bash
# Basic chat mode
uv run -m hello_file_search_refactored --chat

# Chat with specific tools
uv run -m hello_file_search_refactored -i -t file-search --vec-id vec_123

# Chat with model selection
uv run -m hello_file_search_refactored --chat --model gpt-4

# Full example with file and web search
uv run -m hello_file_search_refactored --chat -t file-search -t web-search --vec-id vec_123 vec_456
```

## Available Commands

Once in chat mode, you can use these commands:

| Command | Aliases | Description |
|---------|---------|-------------|
| `/help` | `/h`, `/?` | Show available commands |
| `/exit` | `/quit`, `/bye`, `/q` | Exit the chat |
| `/clear` | `/cls`, `/reset` | Clear conversation history |
| `/save [filename]` | `/s` | Save conversation to file |
| `/load <filename>` | `/l` | Load conversation from file |
| `/history [n]` | `/hist` | Show last n messages (default: 10) |
| `/model [name]` | `/m` | Show/change the model |
| `/tools [action]` | `/t` | Manage tools (add/remove) |
| `/new` | `/n` | Start new conversation |
| `/enable-web-search` | `/ews` | Enable web search tool |
| `/disable-web-search` | `/dws` | Disable web search tool |
| `/enable-file-search` | `/efs` | Enable file search tool |
| `/disable-file-search` | `/dfs` | Disable file search tool |

## Example Chat Session

```
╭─ Knowledge Forge Chat ─────────────────────────────────────╮
│ Model: qwen-max-latest                                      │
│ Tools: file-search, web-search                              │
│                                                             │
│ Type /help for available commands                           │
╰─────────────────────────────────────────────────────────────╯

You: What documents do you have about 云学堂?

🔄 Searching documents...

Assistant: I found the following document about 云学堂:

📄 **云学堂员工差旅管理办法 (V2.0)** - This document contains
the travel expense management policies including hotel standards,
transportation rules, and reimbursement procedures.

You: /save my_conversation

💾 Conversation saved to: my_conversation.json

You: What's the reimbursement process?

🔄 Searching in context...

Assistant: According to the document, the reimbursement process is:

1. Submit expense claims within 15 working days after returning
2. Department head must approve and verify the trip authenticity
3. Finance will review compliance and reasonableness of expenses
4. Non-compliant receipts may be rejected or amounts reduced

You: /exit

👋 Goodbye! Thanks for chatting.
```

## Command Examples

### Managing Tools
```
You: /tools
🛠️ Enabled tools: file-search
Available tools: file-search, web-search
Use: /tools add <tool> or /tools remove <tool>

You: /tools add web-search
✅ Added tool: web-search

You: /tools remove file-search
❌ Removed tool: file-search
```

### Conversation Management
```
You: /history 3
📜 Last 3 messages:

[1] You: What documents do you have?
[2] Assistant: I found the following document...
[3] You: What's the reimbursement process?

You: /clear
🧹 Conversation history cleared.

You: /new
🆕 Started new conversation.
```

## Features

1. **Context Preservation**: All messages are maintained in the conversation
2. **Tool Continuity**: Tool configurations persist across messages
3. **Session Management**: Save and load conversations
4. **Model Switching**: Change models mid-conversation
5. **Command System**: Rich set of commands for chat control

## Tips

- Use `/save` frequently to preserve important conversations
- Use `/history` to review previous messages
- Use `/tools` to enable/disable search capabilities
- Type `//` at the start of a message to escape command parsing
- Press Ctrl+C to exit gracefully

## Technical Details

- Conversations are saved in JSON format
- Message history is included in API requests for context
- Long conversations are automatically truncated to fit token limits
- Each session has a unique ID for tracking