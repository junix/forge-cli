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
```
