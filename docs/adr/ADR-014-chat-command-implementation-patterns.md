# ADR-014: Chat Command Implementation Patterns and Design Standards

**Status**: Accepted  
**Date**: 2025-08-04  
**Decision Makers**: Development Team  
**Extends**: ADR-013 (Modular Chat Command System)

## Context

Following the successful implementation of the modular chat command system (ADR-013), we have gained significant experience with command implementation patterns across different domains. The system now includes 40+ commands across session management, configuration, conversation persistence, file operations, and tool management.

### Current Command Distribution

- **Session Commands** (4): `exit`, `clear`, `help`, `new`
- **Configuration Commands** (3): `model`, `tools`, `vectorstore`
- **Conversation Commands** (4): `save`, `load`, `history`, `list`
- **File Commands** (16+): Upload, document CRUD, collection management, utilities
- **Tool Commands** (8+): Dynamic enable/disable for various tools
- **Information Commands** (2): `inspect`, debugging utilities

### Implementation Quality Variance

Through implementation experience, we've identified patterns that work well and areas needing standardization:

**Excellent Implementations:**

- Upload command with async progress tracking and sophisticated error handling
- Configuration commands with consistent show/modify patterns
- Tool toggle commands with parameterized generic design

**Inconsistent Areas:**

- Argument parsing approaches vary significantly
- Error handling patterns differ across commands
- User feedback formatting lacks consistency
- Help text and usage examples are incomplete

## Decision

**Establish standardized implementation patterns and design guidelines** for chat command development to ensure consistency, maintainability, and excellent user experience across all commands.

### 1. Command Implementation Standards

#### Base Command Structure

```python
class ExampleCommand(ChatCommand):
    """Brief description of command purpose.
    
    Usage:
    - /command - Basic usage description
    - /command <arg> - Usage with arguments
    - /command --option - Usage with options
    """
    
    name = "command-name"
    description = "Brief description for help display"
    aliases = ["alias1", "alias2"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the command with standardized patterns."""
        # 1. Input validation
        # 2. Argument parsing
        # 3. Business logic
        # 4. User feedback
        # 5. Return continuation flag
        return True
```

#### Argument Parsing Patterns

```python
# Pattern 1: Simple flag-based parsing
def _parse_simple_args(self, args: str) -> tuple[str, dict[str, bool]]:
    """Parse simple arguments with flags."""
    parts = args.strip().split()
    main_arg = parts[0] if parts else ""
    flags = {
        "vectorize": "--vectorize" in parts,
        "force": "--force" in parts,
    }
    return main_arg, flags

# Pattern 2: Subcommand parsing
def _parse_subcommand_args(self, args: str) -> tuple[str, list[str]]:
    """Parse subcommand-style arguments."""
    parts = args.strip().split()
    action = parts[0].lower() if parts else ""
    remaining_args = parts[1:] if len(parts) > 1 else []
    return action, remaining_args
```

### 2. Error Handling Standards

#### Validation Pattern

```python
async def execute(self, args: str, controller: ChatController) -> bool:
    # Input validation with helpful messages
    if not args.strip():
        controller.display.show_error("Usage: /command <required_arg>")
        controller.display.show_status("Example: /command example_value")
        return True
    
    # Argument validation
    parsed_args = self._parse_args(args)
    if not self._validate_args(parsed_args):
        controller.display.show_error("Invalid arguments provided")
        return True
    
    # Business logic with exception handling
    try:
        result = await self._execute_business_logic(parsed_args, controller)
        self._show_success_feedback(result, controller)
    except ValidationError as e:
        controller.display.show_error(f"Validation failed: {str(e)}")
    except ConnectionError as e:
        controller.display.show_error(f"Connection error: {str(e)}")
    except Exception as e:
        controller.display.show_error(f"Unexpected error: {str(e)}")
    
    return True
```

### 3. User Feedback Standards

#### Status Message Patterns

```python
# Success messages with appropriate emojis
controller.display.show_status("✅ Operation completed successfully")
controller.display.show_status(f"📄 Document created: {document_id}")
controller.display.show_status(f"🔧 Configuration updated: {setting_name}")

# Progress indicators
controller.display.show_status("⏳ Processing request...")
controller.display.show_status("🔄 Uploading file...")
controller.display.show_status(f"📊 Progress: {percent}%")

# Information display
controller.display.show_status(f"🤖 Current model: {model_name}")
controller.display.show_status(f"🛠️ Enabled tools: {tools_list}")
```

#### Error Message Patterns

```python
# Clear, actionable error messages
controller.display.show_error("File not found: /path/to/file")
controller.display.show_error("Usage: /command <required_arg> [optional_arg]")
controller.display.show_error("Invalid model name. Available: gpt-4, claude-3")

# With helpful suggestions
controller.display.show_error("Unknown command: /typo")
controller.display.show_status("Did you mean: /help, /history, /tools?")
```

### 4. Async Operation Patterns

#### Progress Tracking Template

```python
async def _track_async_operation(self, controller: ChatController, operation_id: str):
    """Standard pattern for tracking long-running operations."""
    poll_interval = 2
    max_attempts = 150  # 5 minutes
    consecutive_errors = 0
    max_consecutive_errors = 3
    
    for attempt in range(max_attempts):
        try:
            status = await self._check_operation_status(operation_id)
            consecutive_errors = 0
            
            if status.is_complete:
                self._handle_completion(status, controller)
                return
            
            self._update_progress_display(status, controller)
            await asyncio.sleep(poll_interval)
            
        except (ConnectionError, TimeoutError) as e:
            consecutive_errors += 1
            if consecutive_errors >= max_consecutive_errors:
                controller.display.show_error("Too many errors, stopping tracking")
                return
            controller.display.show_error(f"Error (attempt {consecutive_errors}): {e}")

## Implementation Guidelines

### 5. Command Organization Patterns

#### File Command Module Structure
The file commands demonstrate excellent modular organization:

```text
src/forge_cli/chat/commands/files/
├── __init__.py              # Module exports and documentation
├── upload.py                # Core file upload with progress tracking
├── new_document.py          # Document creation
├── show_document.py         # Document display
├── delete_document.py       # Document deletion
├── new_collection.py        # Collection management
├── show_collections.py      # Collection listing
└── ...                      # One command per file
```

**Benefits:**

- Single responsibility per file
- Easy to locate and modify specific commands
- Clear import structure
- Independent testing capabilities

#### Command Registration Pattern

```python
# In base.py CommandRegistry._register_default_commands()
from .files import (
    DeleteCollectionCommand,
    DeleteDocumentCommand,
    DocumentsCommand,
    # ... all file commands
)

default_commands = [
    # Session commands
    ExitCommand(),
    ClearCommand(),
    # File commands
    UploadCommand(),
    NewDocumentCommand(),
    # ... automatic registration
]
```

### 6. Type Safety and Validation

#### Type-Safe Command Implementation

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...controller import ChatController

class TypedCommand(ChatCommand):
    """Example of type-safe command implementation."""

    async def execute(self, args: str, controller: ChatController) -> bool:
        # Type checker knows controller type
        # Full IDE support and validation
        return True
```

#### Argument Validation Helpers

```python
def _validate_file_path(self, path_str: str) -> Path | None:
    """Validate and resolve file path."""
    try:
        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            return None
        return path
    except (OSError, ValueError):
        return None

def _validate_model_name(self, model: str) -> bool:
    """Validate model name against known models."""
    valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3", "qwen-max-latest"]
    return model in valid_models
```

### 7. Testing Patterns

#### Command Unit Testing Template

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from forge_cli.chat.commands.example import ExampleCommand

@pytest.fixture
def mock_controller():
    controller = MagicMock()
    controller.display = MagicMock()
    controller.config = MagicMock()
    controller.conversation = MagicMock()
    return controller

@pytest.mark.asyncio
async def test_example_command_success(mock_controller):
    command = ExampleCommand()
    result = await command.execute("valid_args", mock_controller)

    assert result is True
    mock_controller.display.show_status.assert_called_once()

@pytest.mark.asyncio
async def test_example_command_validation_error(mock_controller):
    command = ExampleCommand()
    result = await command.execute("", mock_controller)

    assert result is True
    mock_controller.display.show_error.assert_called_once()
```

## Benefits of Standardized Patterns

### 1. Consistency Across Commands

- **Predictable User Experience**: Users know what to expect
- **Uniform Error Handling**: Consistent error messages and recovery
- **Standard Feedback**: Recognizable status indicators and emojis

### 2. Developer Productivity

- **Clear Templates**: New commands follow established patterns
- **Reduced Decision Fatigue**: Standard approaches for common tasks
- **Faster Implementation**: Copy-paste templates with modifications

### 3. Maintainability

- **Easier Debugging**: Consistent error handling patterns
- **Simplified Testing**: Standard test patterns and fixtures
- **Code Review Efficiency**: Reviewers know what to expect

### 4. Quality Assurance

- **Input Validation**: Standardized argument parsing and validation
- **Error Recovery**: Consistent exception handling
- **User Feedback**: Clear, helpful messages with appropriate formatting

## Implementation Status

### ✅ Well-Implemented Commands

- **Upload Command**: Excellent async progress tracking, error handling
- **Configuration Commands**: Consistent show/modify patterns
- **Session Commands**: Clean, simple implementations
- **Tool Commands**: Generic parameterized design

### 🚧 Commands Needing Standardization

- **File Commands**: Several placeholder implementations remain
- **Argument Parsing**: Inconsistent approaches across commands
- **Error Messages**: Varying levels of helpfulness
- **Help Documentation**: Incomplete usage examples

### 📋 Migration Tasks

1. Complete extraction of remaining file commands from `files_old.py`
2. Standardize argument parsing across all commands
3. Implement consistent error handling patterns
4. Add comprehensive help text and usage examples
5. Create command testing templates and fixtures

## Future Enhancements

### Plugin System Foundation

The standardized patterns enable future plugin capabilities:

```python
# Future: Plugin command template
class PluginCommand(ChatCommand):
    """Template for plugin-provided commands."""

    def __init__(self, plugin_config: dict):
        self.plugin_config = plugin_config
        # Standard initialization

    async def execute(self, args: str, controller: ChatController) -> bool:
        # Standard execution pattern
        return True
```

### Command Analytics

```python
# Future: Usage tracking
class AnalyticsCommand(ChatCommand):
    """Base class with usage analytics."""

    async def execute(self, args: str, controller: ChatController) -> bool:
        # Track command usage
        self._record_usage(args)
        result = await self._execute_impl(args, controller)
        self._record_completion(result)
        return result
```

## Related ADRs

- **ADR-013**: Modular Chat Command System (architectural foundation)
- **ADR-012**: Chat-First Architecture Migration (context for command importance)
- **ADR-007**: Typed-Only Architecture Migration (type safety requirements)

---

**Key Insight**: Standardized implementation patterns transform the modular command architecture into a consistent, maintainable, and user-friendly system that scales effectively as new commands are added.
