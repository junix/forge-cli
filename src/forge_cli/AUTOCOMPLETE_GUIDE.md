# Auto-completion Guide for Chat Mode

## Overview

The chat mode supports auto-completion for all commands when `prompt_toolkit` is installed. This provides a better user experience with tab completion and command suggestions.

## Installation

To enable auto-completion, install prompt_toolkit:

```bash
pip install prompt_toolkit
```

## Features

- **Tab Completion**: Press TAB to complete commands
- **Live Suggestions**: See available completions while typing
- **Case Insensitive**: Commands complete regardless of case
- **Alias Support**: All command aliases are included in completions

## Usage

### Basic Auto-completion

1. Type `/` - suggestions will appear automatically as you type
2. Continue typing to filter suggestions:
   - Type `/e` → shows `/enable-file-search`, `/enable-web-search`, `/exit`, etc.
   - Type `/ews` → shows `/enable-web-search`
   - Type `/d` → shows `/disable-file-search`, `/disable-web-search`
3. Press TAB to accept the highlighted suggestion
4. Use arrow keys to navigate through suggestions

### Navigation

- Use arrow keys to navigate through suggestions
- Press TAB multiple times to cycle through options
- Press ENTER to select a completion

## Available Commands for Completion

| Command | Aliases |
|---------|---------|
| `/help` | `/h`, `/?` |
| `/exit` | `/quit`, `/bye`, `/q` |
| `/clear` | `/cls`, `/reset` |
| `/save` | `/s` |
| `/load` | `/l` |
| `/history` | `/hist` |
| `/model` | `/m` |
| `/tools` | `/t` |
| `/new` | `/n` |
| `/enable-web-search` | `/ews` |
| `/disable-web-search` | `/dws` |
| `/enable-file-search` | `/efs` |
| `/disable-file-search` | `/dfs` |

## Fallback Behavior

If prompt_toolkit is not installed, the chat mode will fall back to:
1. Rich library prompt (if using RichDisplay)
2. Basic Python input() function

The functionality remains the same, but without auto-completion support.

## Troubleshooting

- **No auto-completion**: Ensure prompt_toolkit is installed with `pip install prompt_toolkit`
- **Terminal compatibility**: Some terminals may not support all features
- **SSH sessions**: Auto-completion works best in local terminal sessions