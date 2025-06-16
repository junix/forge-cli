# ADR-001: Command-Line Interface Design

## Status
Accepted

## Context
The Knowledge Forge system requires command-line tools for developers to interact with the API server. These tools serve both as utilities for common tasks and as reference implementations for developers building applications with the Knowledge Forge API.

## Decision
We will implement command-line tools following these design principles:

### 1. SDK-First Approach
All command-line tools MUST use the centralized SDK (`sdk.py`) rather than making direct REST API calls. This ensures:
- Consistent error handling across all tools
- Centralized API logic that can be updated in one place
- Type safety and better IDE support
- Reusable async patterns

### 2. Async/Await Pattern
All tools use Python's async/await pattern for API operations:
- Enables efficient concurrent operations
- Aligns with modern Python best practices
- Supports streaming responses naturally
- Better performance for I/O-bound operations

### 3. Command-Line Interface Pattern
The system provides a unified CLI tool executed as:
```bash
# Primary CLI tool (via pyproject.toml console script)
forge-cli

# Module execution
python -m forge_cli

# Development execution
uv run forge-cli
```
This approach:
- Provides user-friendly command-line interface
- Ensures proper Python path resolution
- Works consistently across different environments
- Integrates well with the uv package manager

### 4. Unified Configuration System
Configuration is handled through a centralized `AppConfig` dataclass:
- Command-line arguments (primary)
- Environment variables: `KNOWLEDGE_FORGE_URL`
- Sensible defaults for all options
- Support for multiple tools, vector stores, and display modes

### 5. Modular Architecture Pattern
The system uses a modular design with registries:
```python
# Processor registry for event handling
ProcessorRegistry.register("file_search_call", FileSearchProcessor())

# Display registry for output strategies
DisplayRegistry.register("rich", RichDisplay)
DisplayRegistry.register("plain", PlainDisplay)
```

### 6. Multi-Modal Output System
- Strategy pattern for display implementations
- Rich terminal UI with live updates and markdown rendering
- Plain text output for basic terminals and automation
- JSON output for machine parsing and integration
- Interactive chat mode with conversation management

## Consequences

### Positive
- **Consistency**: All tools follow the same patterns and conventions
- **Maintainability**: SDK centralizes API logic, reducing duplication
- **Developer Experience**: Clear examples for API usage
- **Testability**: Async patterns make testing easier
- **Extensibility**: New commands can be added following established patterns

### Negative
- **Learning Curve**: Developers must understand async/await
- **Dependency**: All tools depend on the SDK module
- **Complexity**: Simple operations require async wrapper functions

## Examples

### Current CLI Usage Examples
```bash
# Basic file search
forge-cli -q "What information is in these documents?" --vec-id vs_123

# Multiple tools with web search
forge-cli -t file-search -t web-search -q "Compare internal docs with latest trends"

# Interactive chat mode
forge-cli --chat

# JSON output for automation
forge-cli -q "search query" --json --vec-id vs_123
```

### SDK Integration Pattern
```python
#!/usr/bin/env python3
import asyncio
from forge_cli.sdk import async_create_response, astream_response

async def main():
    # Streaming response with event processing
    async for event_type, event_data in astream_response(
        input_messages="Hello, Knowledge Forge!",
        model="qwen-max-latest"
    ):
        if event_type == "response.output_text.delta":
            print(event_data["text"], end="", flush=True)
        elif event_type == "done":
            break

if __name__ == "__main__":
    asyncio.run(main())
```

## Alternatives Considered

1. **Direct REST Calls**: Rejected due to code duplication and inconsistent error handling
2. **Synchronous API**: Rejected as it doesn't support streaming and concurrent operations well
3. **Shell Scripts**: Rejected as they lack type safety and complex data handling capabilities
4. **Click Framework**: Considered but argparse is sufficient and has no external dependencies

## References
- Python asyncio documentation: https://docs.python.org/3/library/asyncio.html
- Knowledge Forge API documentation: internal docs
- ADR template: https://github.com/joelparkerhenderson/architecture-decision-record