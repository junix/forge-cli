# Plaintext Renderer for V3 Display System

The Plaintext renderer provides beautiful, colorful terminal output using Rich's Live and Text components without panels or markdown components. It's perfect for environments where you want rich formatting but prefer a simpler, cleaner visual structure.

## Features

- **Rich Live Display**: Real-time updating display using Rich's Live component
- **Custom Text Styling**: Beautiful colors and formatting using Rich Text with custom styles
- **No Complex Components**: Avoids panels and markdown components for cleaner output
- **Configurable Appearance**: Extensive customization options for colors, separators, and layout
- **Inline Formatting**: Supports **bold**, *italic*, and `code` formatting
- **Smart Sectioning**: Organized sections with customizable separators
- **Pydantic Configuration**: Type-safe configuration with validation

## Configuration Options

```python
from forge_cli.display.v3.renderers.plaintext import PlaintextDisplayConfig

config = PlaintextDisplayConfig(
    show_reasoning=True,         # Show AI reasoning/thinking content
    show_citations=True,         # Show citation details
    show_tool_details=True,      # Show detailed tool information
    show_usage=True,            # Show token usage statistics
    show_metadata=False,        # Show response metadata
    show_status_header=True,    # Show status header
    max_text_preview=100,       # Max characters for text previews
    refresh_rate=10,            # Live display refresh rate (1-30 Hz)
    indent_size=2,              # Spaces for indentation (0-8)
    separator_char="─",         # Character for separators
    separator_length=60         # Length of separator lines
)
```

## Basic Usage

```python
from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer, PlaintextDisplayConfig
from forge_cli.display.v3.base import Display

# Create renderer with config
config = PlaintextDisplayConfig(separator_char="═", separator_length=50)
renderer = PlaintextRenderer(config=config)

# Create display
display = Display(renderer)

# Handle response (in real usage, response comes from API)
display.handle_response(response)
display.complete()
```

## Chat Mode Usage

```python
# Enable chat mode for interactive sessions
renderer = PlaintextRenderer(in_chat_mode=True)
display = Display(renderer, mode="chat")

# Show welcome message
renderer.render_welcome(config)

# Show request info
renderer.render_request_info({
    "question": "How does this work?",
    "model": "claude-3-sonnet",
    "tools": ["file_search", "web_search"]
})

# Handle responses
display.handle_response(response)
display.complete()
```

## Style Customization

The renderer uses a comprehensive style system that can be customized:

```python
renderer = PlaintextRenderer()

# Override default styles
renderer._styles.update({
    "header": "bold magenta",
    "content": "bright_white", 
    "separator": "dim cyan",
    "tool_icon": "bright_yellow",
    "citation_ref": "bold green",
    "status_completed": "bold bright_green",
    "reasoning": "italic dim cyan"
})
```

### Available Style Keys

- **Status Styles**: `status_completed`, `status_failed`, `status_in_progress`, `status_default`
- **Content Styles**: `header`, `content`, `model`, `id`, `separator`
- **Tool Styles**: `tool_icon`, `tool_name`, `tool_status_completed`, `tool_status_in_progress`, `tool_status_failed`
- **Citation Styles**: `citation_ref`, `citation_source`, `citation_text`
- **UI Styles**: `usage`, `usage_label`, `error`, `warning`, `info`, `success`
- **Reasoning Styles**: `reasoning`, `reasoning_header`

## Output Structure

The plaintext renderer creates organized, sectioned output:

```
🔥 Knowledge Forge Response
ID: resp_12345... │ Status: ✅ COMPLETED │ Model: claude-3-sonnet │ Updates: 1
────────────────────────────────────────────────────────────────

─────────────────────── RESPONSE ───────────────────────

🔸 Main Response Header
  ▸ Subheader
    • Sub-subheader

  • Bullet point with proper indentation
  • Another bullet point

1. Numbered list item
2. Another numbered item

Regular text with **bold formatting** and *italic text* and `code snippets`.

📎 References: [1], [2]

─────────────────────── TOOLS ───────────────────────

📄 File Search Call: ✅ completed │ Queries: 2 │ Results: 5
🌐 Web Search Call: ⏳ in_progress │ Queries: 1

─────────────────────── REASONING ───────────────────────

🤔 AI Thinking Process:
  I need to analyze the user's question and provide a comprehensive response...
  Let me break this down into key components...

─────────────────────── SOURCES ───────────────────────

[1] document.pdf (page 5)
    "This is a relevant quote from the source document..."

[2] website.com
    "Another relevant citation from a web source..."

─────────────────────── USAGE ───────────────────────

📊 Token Usage: Input: 150 │ Output: 75 │ Total: 225
```

## Inline Formatting Support

The renderer automatically handles simple markdown-like formatting:

- **Headers**: `# Header`, `## Subheader`, `### Sub-subheader`
- **Bold Text**: `**bold text**` → **bold text**
- **Italic Text**: `*italic text*` → *italic text*
- **Code**: `` `code` `` → `code`
- **Lists**: `- item` or `* item` → • item
- **Numbered Lists**: `1. item` → 1. item

## Icons and Visual Elements

The renderer uses contextual icons throughout:

- **Status Icons**: ✅ completed, ❌ failed, ⏳ in_progress, ⚠️ incomplete
- **Tool Icons**: 📄 file search, 🌐 web search, 🔍 document finder, 📖 file reader
- **Section Icons**: 🔥 main header, 🤔 reasoning, 📎 references, 📊 usage
- **Content Icons**: 🔸 headers, ▸ subheaders, • bullets

## Error Handling

The renderer gracefully handles errors with clear visual feedback:

```python
renderer.render_error("Connection timeout occurred")
# Output: ❌ ERROR: Connection timeout occurred
```

## Performance Features

- **Live Updates**: Efficient real-time display updates
- **Minimal Memory**: Text-based rendering with low memory footprint
- **Fast Rendering**: Optimized text composition and styling
- **Configurable Refresh**: Adjustable refresh rate (1-30 Hz)

## Use Cases

- **Development Environments**: Clean output for debugging and development
- **CI/CD Pipelines**: Readable logs with color coding
- **Terminal Applications**: Rich formatting without complex UI components
- **Accessibility**: Simple structure that works well with screen readers
- **Custom Styling**: Easy to customize colors and appearance
- **Live Monitoring**: Real-time updates for long-running processes

## Comparison with Other Renderers

| Feature | Plaintext | Rich | JSON |
|---------|-----------|------|------|
| Visual Complexity | Simple | Complex | None |
| Live Updates | ✅ | ✅ | ❌ |
| Customizable Styling | ✅ | ✅ | ❌ |
| Programmatic Processing | ❌ | ❌ | ✅ |
| Terminal Compatibility | ✅ | ✅ | ✅ |
| Memory Usage | Low | Medium | Low |
| Accessibility | High | Medium | High |

The Plaintext renderer strikes the perfect balance between visual appeal and simplicity, making it ideal for users who want beautiful, colorful output without the complexity of nested panels and components. 