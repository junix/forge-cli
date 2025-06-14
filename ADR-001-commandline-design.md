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

### 3. Module Execution Pattern
Commands are executed as Python modules using:
```bash
uv run -m commands.<command_name>
```
This approach:
- Ensures proper Python path resolution
- Works consistently across different environments
- Integrates well with the uv package manager

### 4. Configuration via Environment Variables
Primary configuration through environment variables:
- `KNOWLEDGE_FORGE_URL`: API server URL (default: http://localhost:9999)
- `OPENAI_API_KEY`: Optional API key for authentication
- `PYTHONPATH`: Set to knowledge_forge directory

### 5. Subcommand Pattern for Complex Tools
Tools with multiple operations use argparse subcommands:
```python
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')
upload_parser = subparsers.add_parser('upload')
delete_parser = subparsers.add_parser('delete')
```

### 6. Consistent Output Formatting
- Use `rich` library for enhanced terminal output
- JSON output option for machine parsing
- Progress indicators for long-running operations
- Clear error messages with actionable information

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

### Basic Command Structure
```python
#!/usr/bin/env python3
import asyncio
from commands.sdk import async_create_response

async def main():
    response = await async_create_response(
        input_messages="Hello, Knowledge Forge!",
        model="qwen-max-latest"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming Response Pattern
```python
async for event_type, event_data in astream_response(messages):
    if event_type == "response.output_text.delta":
        print(event_data["text"], end="", flush=True)
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