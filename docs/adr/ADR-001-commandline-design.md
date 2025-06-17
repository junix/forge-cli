# ADR-001: Command-Line Interface Design

**Status**: Accepted (Updated 2025-06-17)
**Date**: 2025-01-15 (Updated 2025-06-17)
**Decision Makers**: Development Team
**Updates**: Chat-first architecture, modular CLI parser, configuration system refactoring

## Context

The Knowledge Forge system requires command-line tools for developers to interact with the API server. These tools serve both as utilities for common tasks and as reference implementations for developers building applications with the Knowledge Forge API.

The CLI has evolved from a single-turn query tool to a sophisticated interactive chat system that serves as the primary interface for Knowledge Forge interactions.

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

### 3. Chat-First Architecture

The CLI now defaults to interactive chat mode, providing a natural conversation interface:

```bash
# Default behavior - starts interactive chat
forge-cli

# Chat with initial question
forge-cli -q "What information is in these documents?"

# Chat with specific tools enabled
forge-cli -t file-search --vec-id vs_123

# Resume existing conversation
forge-cli --resume conv_123
```

### 4. Modular CLI Parser System

The CLI uses a modular parser architecture with `CLIParser` class:

- Centralized argument definition and validation
- Automatic help generation with examples
- Version handling and graceful error messages
- Support for multiple execution methods (module, script, development)

### 5. Unified Configuration System

Configuration is handled through a centralized `AppConfig` Pydantic model:

- Command-line arguments (primary)
- Environment variables: `KNOWLEDGE_FORGE_URL`
- Sensible defaults optimized for chat mode
- Support for multiple tools, vector stores, and display modes
- Automatic validation and type conversion

### 6. Modular Architecture Pattern

The system uses a modular design with factory patterns and clean separation:

```python
# Display factory for renderer selection
display = DisplayFactory.create_display(config)

# Chat command system with modular handlers
from forge_cli.chat.commands import CommandRegistry
registry = CommandRegistry()

# Session management with typed API integration
session_manager = ChatSessionManager(config, display)
```

### 7. Multi-Modal Output System

- V3 snapshot-based display architecture with pluggable renderers
- Rich terminal UI with live updates, syntax highlighting, and panels
- Plain text output for basic terminals and automation
- JSON output with Rich syntax highlighting for machine parsing
- Interactive chat mode with persistent conversation management
- Configuration-driven renderer selection

## Consequences

### Positive

- **Chat-First Experience**: Natural conversation interface as default
- **Consistency**: All tools follow the same patterns and conventions
- **Maintainability**: SDK centralizes API logic, reducing duplication
- **Developer Experience**: Interactive chat with command system
- **Testability**: Async patterns and modular design make testing easier
- **Extensibility**: New chat commands and renderers easily added
- **Type Safety**: Pydantic configuration with validation

### Negative

- **Learning Curve**: Developers must understand async/await and chat paradigm
- **Dependency**: All tools depend on the SDK module
- **Memory Usage**: Chat mode maintains conversation history

## Examples

### Current CLI Usage Examples

```bash
# Default interactive chat mode
forge-cli

# Chat with initial question
forge-cli -q "What information is in these documents?"

# Chat with file search enabled
forge-cli -t file-search --vec-id vs_123

# Chat with web search
forge-cli -t web-search

# Resume existing conversation
forge-cli --resume conv_123

# JSON output for automation (still in chat mode)
forge-cli --render json --vec-id vs_123
```

### SDK Integration Pattern (Typed API)

```python
#!/usr/bin/env python3
import asyncio
from forge_cli.sdk.typed_api import astream_typed_response, create_typed_request
from forge_cli.response._types import InputMessage

async def main():
    # Create typed request
    request = create_typed_request(
        input_messages="Hello, Knowledge Forge!",
        model="qwen-max-latest"
    )

    # Stream typed response with snapshot-based processing
    async for event_type, response in astream_typed_response(request):
        if response is not None:
            # Process complete response snapshot
            print(response.output_text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

## Alternatives Considered

1. **Direct REST Calls**: Rejected due to code duplication and inconsistent error handling
2. **Synchronous API**: Rejected as it doesn't support streaming and concurrent operations well
3. **Shell Scripts**: Rejected as they lack type safety and complex data handling capabilities
4. **Click Framework**: Considered but argparse is sufficient and has no external dependencies
5. **Single-Turn Only**: Rejected in favor of chat-first approach for better user experience
6. **Separate Chat Tool**: Rejected in favor of unified CLI with chat as default mode

## Related ADRs

- **ADR-005**: Interactive Chat Mode Implementation (updated for current architecture)
- **ADR-007**: Typed-Only Architecture Migration (enables current SDK patterns)
- **ADR-008**: V3 Response Snapshot Display Architecture (current display system)
- **ADR-012**: Chat-First Architecture Migration (documents default chat mode)
- **ADR-014**: Configuration System Refactoring (AppConfig Pydantic model)

## References

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Pydantic documentation](https://docs.pydantic.dev/)
- Knowledge Forge API documentation: internal docs
- [ADR template](https://github.com/joelparkerhenderson/architecture-decision-record)

---

**Key Changes in 2025-06-17 Update**: The CLI has evolved from a single-turn query tool to a chat-first interactive system with modular architecture, typed APIs, and sophisticated display capabilities. The `--chat` flag has been removed as chat mode is now the default behavior.
