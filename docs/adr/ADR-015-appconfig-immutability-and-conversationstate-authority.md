# ADR-015: AppConfig Immutability and ConversationState Authority

**Status**: Accepted  
**Date**: 2025-08-04  
**Decision Makers**: Development Team  
**Extends**: ADR-013 (Modular Chat Command System), ADR-014 (Chat Command Implementation Patterns)

## Context

The forge-cli application manages configuration at two levels: startup configuration (from CLI arguments and environment) and runtime configuration (modified during chat sessions). Previously, both `AppConfig` and `ConversationState` could be modified during runtime, leading to:

### Problems with Dual Configuration Sources

1. **State Inconsistency**: Commands modified both `AppConfig` and `ConversationState`, causing synchronization issues
2. **Unclear Authority**: Unclear which configuration source was authoritative for API calls
3. **Complex Logic**: `new_request()` required complex priority logic between config sources
4. **Persistence Issues**: Runtime changes could affect global configuration unexpectedly
5. **Testing Complexity**: Multiple mutable configuration sources made testing difficult

### Example of Previous Problematic Pattern

```python
# Commands modified both sources
controller.config.model = new_model          # Global config modified
controller.conversation.model = new_model    # Conversation state modified

# API calls had complex priority logic
def new_request(self, content: str, config: AppConfig) -> Request:
    # Which takes priority? Config or conversation state?
    model = self.model or config.model
    tools = self.enabled_tools if self.enabled_tools else config.enabled_tools
```

## Decision

**Establish AppConfig as immutable during runtime and ConversationState as the single authoritative source for all runtime configuration.**

### Core Principles

1. **AppConfig Immutability**: AppConfig is created once at startup and never modified during runtime
2. **ConversationState Authority**: ConversationState is the single source of truth for all runtime decisions
3. **Clear Initialization Flow**: Configuration flows unidirectionally from AppConfig to ConversationState
4. **Command Isolation**: All user commands modify only ConversationState
5. **API Simplification**: All API calls use only ConversationState configuration

## Implementation

### 1. AppConfig Role Redefinition

**Before (Mutable Global Config):**
```python
class AppConfig:
    model: str = "qwen-max-latest"
    enabled_tools: list[str] = Field(default_factory=list)
    
# Commands modified AppConfig during runtime
controller.config.model = "gpt-4"
controller.config.enabled_tools.append("web-search")
```

**After (Immutable Transfer Mechanism):**
```python
class AppConfig(BaseModel):
    """Immutable startup configuration - transfer mechanism only."""
    model: str = "qwen-max-latest"
    enabled_tools: list[ToolType] = Field(default_factory=lambda: ["file-search"])
    
    def apply_dataset_config(self, dataset, args) -> AppConfig:
        """Returns NEW instance - never modifies self."""
        if updates:
            return self.model_copy(update=updates)
        return self
```

### 2. ConversationState as Runtime Authority

**Enhanced ConversationState:**
```python
class ConversationState(BaseModel):
    # Original conversation fields
    messages: list[ResponseInputMessageItem] = Field(default_factory=list)
    
    # Runtime configuration (authoritative)
    model: str = Field(default=DEFAULT_MODEL)
    effort: str = Field(default="low")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1000, gt=0)
    enabled_tools: list[str] = Field(default_factory=list)
    current_vector_store_ids: list[str] = Field(default_factory=list)
    debug: bool = Field(default=False)
    
    @classmethod
    def from_config(cls, config: AppConfig) -> ConversationState:
        """Initialize from AppConfig - one-time transfer."""
        return cls(
            model=config.model,
            effort=config.effort,
            temperature=config.temperature,
            enabled_tools=config.enabled_tools.copy(),
            current_vector_store_ids=config.vec_ids.copy(),
            debug=config.debug,
            # ... all other fields
        )
```

### 3. Simplified API Design

**Before (Complex Priority Logic):**
```python
def new_request(self, content: str, config: AppConfig) -> Request:
    # Complex priority resolution
    model = self.model or config.model
    tools = []
    
    file_search_enabled = self.file_search_enabled or "file-search" in config.enabled_tools
    vector_store_ids = self.current_vector_store_ids if self.current_vector_store_ids else config.vec_ids
    
    return Request(
        model=model,
        tools=tools,
        temperature=config.temperature or 0.7,
        # ...
    )
```

**After (Single Source Authority):**
```python
def new_request(self, content: str) -> Request:
    """Create request using conversation state as single authority."""
    tools = []
    
    if self.file_search_enabled:
        tools.append(FileSearchTool(vector_store_ids=self.current_vector_store_ids))
    
    if self.web_search_enabled:
        tools.append(WebSearchTool())
    
    return Request(
        model=self.model,
        tools=tools,
        temperature=self.temperature,
        max_output_tokens=self.max_output_tokens,
        effort=self.effort,
    )
```

### 4. Command Pattern Standardization

**All commands follow the same pattern:**
```python
class ModelCommand(ChatCommand):
    async def execute(self, args: str, controller: ChatController) -> bool:
        if not args.strip():
            # Read from conversation state (authoritative)
            controller.display.show_status(f"🤖 Current model: {controller.conversation.model}")
        else:
            # Modify only conversation state
            controller.conversation.model = args.strip()
            controller.display.show_status(f"🤖 Model changed to: {args.strip()}")
        return True
```

### 5. Runtime Usage Pattern

**Session Management:**
```python
class ChatSessionManager:
    def __init__(self, config: AppConfig, display: Display):
        self.config = config  # Stored but never modified
        self.controller = ChatController(config, display)
    
    async def _handle_user_message(self, content: str) -> None:
        # Use conversation state for all runtime decisions
        request = self.controller.conversation.new_request(content)
        handler = TypedStreamHandler(self.display, debug=self.controller.conversation.debug)
        event_stream = astream_typed_response(request, debug=self.controller.conversation.debug)
```

## Benefits

### 1. Architectural Clarity

- **Single Responsibility**: AppConfig handles startup, ConversationState handles runtime
- **Clear Data Flow**: Unidirectional configuration transfer
- **Predictable Behavior**: No hidden configuration modifications

### 2. Simplified Implementation

- **Reduced Complexity**: No priority resolution logic needed
- **Fewer Parameters**: `new_request()` needs no config parameter
- **Consistent Commands**: All commands follow same modification pattern

### 3. Enhanced Reliability

- **State Consistency**: Only one mutable configuration source
- **Immutable Reference**: Original startup configuration preserved
- **Predictable Persistence**: Runtime changes saved with conversation, not globally

### 4. Improved Testability

- **Isolated Testing**: Each configuration source can be tested independently
- **Predictable State**: No unexpected configuration mutations
- **Clear Assertions**: Test exactly what should be modified

## Migration Impact

### Breaking Changes

1. **Command Implementation**: Commands must be updated to modify only ConversationState
2. **API Signatures**: `new_request()` no longer takes config parameter
3. **Runtime Access**: All runtime configuration must come from ConversationState

### Migration Steps

1. **Extend ConversationState**: Add all runtime configuration fields
2. **Update from_config()**: Copy all AppConfig fields to ConversationState
3. **Modify Commands**: Change all commands to modify only ConversationState
4. **Simplify APIs**: Remove config parameters from runtime methods
5. **Update Session Management**: Use ConversationState for all runtime decisions

## Validation

### Test Cases

```python
def test_appconfig_immutability():
    """Verify AppConfig is never modified during runtime."""
    original_config = AppConfig(model='gpt-4', tool=['web-search'])
    conversation = ConversationState.from_config(original_config)
    
    # Modify conversation
    conversation.model = 'claude-3'
    conversation.enable_tool('file-search')
    
    # Verify original config unchanged
    assert original_config.model == 'gpt-4'
    assert original_config.enabled_tools == ['web-search']

def test_conversation_authority():
    """Verify ConversationState is authoritative for API calls."""
    config = AppConfig(model='gpt-4', temperature=0.3)
    conversation = ConversationState.from_config(config)
    
    # Modify conversation differently from config
    conversation.model = 'claude-3'
    conversation.temperature = 0.8
    
    # API call should use conversation state
    request = conversation.new_request("test")
    assert request.model == 'claude-3'
    assert request.temperature == 0.8
```

## Related ADRs

- **ADR-013**: Modular Chat Command System (architectural foundation)
- **ADR-014**: Chat Command Implementation Patterns (command standardization)
- **ADR-007**: Typed-Only Architecture Migration (type safety requirements)

---

## Implementation Examples

### Configuration Flow Diagram

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   CLI Args +    │───▶│    AppConfig     │───▶│  ConversationState  │
│  Environment    │    │   (Immutable)    │    │    (Mutable)        │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                              │                           │
                              │                           ▼
                              │                  ┌─────────────────┐
                              │                  │  User Commands  │
                              │                  │ (Modify Only    │
                              │                  │ Conversation)   │
                              │                  └─────────────────┘
                              │                           │
                              │                           ▼
                              │                  ┌─────────────────┐
                              │                  │   API Calls     │
                              │                  │ (Use Only       │
                              │                  │ Conversation)   │
                              │                  └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Preserved as   │
                    │ Startup Reference│
                    └──────────────────┘
```

### Real-World Usage Examples

#### Startup Sequence
```python
# 1. Create immutable startup configuration
config = AppConfig.from_args(args)
config = config.apply_dataset_config(dataset, args)  # Returns new instance

# 2. Initialize conversation with startup config
conversation = ConversationState.from_config(config)

# 3. Config is now immutable reference, conversation is mutable runtime state
session = ChatSessionManager(config, display)  # Config stored but never modified
```

#### Runtime Command Execution
```python
# User executes: /model gpt-4
class ModelCommand(ChatCommand):
    async def execute(self, args: str, controller: ChatController) -> bool:
        # ✅ CORRECT: Modify only conversation state
        controller.conversation.model = args.strip()

        # ❌ WRONG: Never modify AppConfig during runtime
        # controller.config.model = args.strip()  # This would break immutability
```

#### API Request Generation
```python
# Before: Complex priority logic
def old_new_request(self, content: str, config: AppConfig) -> Request:
    model = self.model if self.model else config.model  # Which takes priority?
    temp = config.temperature or 0.7  # Fallback logic

# After: Single source of truth
def new_request(self, content: str) -> Request:
    return Request(
        model=self.model,           # Always from conversation state
        temperature=self.temperature, # Always from conversation state
        # No ambiguity, no fallback logic needed
    )
```

### Tool Management Example

```python
# User executes: /tools add web-search
class ToolsCommand(ChatCommand):
    async def execute(self, args: str, controller: ChatController) -> bool:
        if action == "add":
            # ✅ CORRECT: Modify conversation state only
            if not controller.conversation.is_tool_enabled(tool_name):
                controller.conversation.enable_tool(tool_name)

            # ❌ WRONG: Don't modify AppConfig
            # controller.config.enabled_tools.append(tool_name)
```

### Persistence Behavior

```python
# Conversation state includes all runtime configuration
conversation_data = {
    "messages": [...],
    "model": "claude-3",           # User changed from startup "gpt-4"
    "temperature": 0.9,            # User changed from startup 0.7
    "enabled_tools": ["web-search", "file-search"],  # User added tools
    "current_vector_store_ids": ["vs_123", "vs_456"],
    # ... all runtime state
}

# When conversation is resumed:
loaded_conversation = ConversationState.load(path)
# All user modifications are preserved
# Original AppConfig remains unchanged as startup reference
```

## Error Prevention Patterns

### 1. Immutability Enforcement

```python
# AppConfig methods return new instances
def apply_dataset_config(self, dataset, args) -> AppConfig:
    """Never modifies self - always returns new instance."""
    if updates:
        return self.model_copy(update=updates)  # Pydantic immutable copy
    return self  # Return self only if no changes needed

# Commands follow strict pattern
async def execute(self, args: str, controller: ChatController) -> bool:
    # ✅ Read from conversation state
    current_value = controller.conversation.some_field

    # ✅ Modify conversation state
    controller.conversation.some_field = new_value

    # ❌ Never access controller.config for modification
    # controller.config.some_field = new_value  # FORBIDDEN
```

### 2. Testing Immutability

```python
def test_config_immutability():
    """Ensure AppConfig is never modified during runtime operations."""
    original = AppConfig(model="gpt-4", tool=["web-search"])

    # Create conversation and modify it
    conversation = ConversationState.from_config(original)
    conversation.model = "claude-3"
    conversation.enable_tool("file-search")

    # Original config must remain unchanged
    assert original.model == "gpt-4"
    assert original.enabled_tools == ["web-search"]

    # Conversation has the changes
    assert conversation.model == "claude-3"
    assert "file-search" in conversation.enabled_tools
```

## Troubleshooting Guide

### Common Anti-Patterns to Avoid

1. **Modifying AppConfig during runtime**
   ```python
   # ❌ WRONG
   controller.config.model = "new-model"

   # ✅ CORRECT
   controller.conversation.model = "new-model"
   ```

2. **Using AppConfig for runtime decisions**
   ```python
   # ❌ WRONG
   if controller.config.debug:
       print("Debug info")

   # ✅ CORRECT
   if controller.conversation.debug:
       print("Debug info")
   ```

3. **Complex priority logic**
   ```python
   # ❌ WRONG - No longer needed
   model = conversation.model or config.model

   # ✅ CORRECT - Single source
   model = conversation.model
   ```

### Migration Checklist

- [ ] All commands modify only ConversationState
- [ ] No runtime assignments to AppConfig fields
- [ ] API methods use only ConversationState
- [ ] Session management uses ConversationState for runtime decisions
- [ ] Tests verify AppConfig immutability
- [ ] Documentation updated to reflect new patterns

---

**Key Insight**: Separating immutable startup configuration from mutable runtime state eliminates complexity, improves reliability, and creates a more maintainable architecture where each component has a single, clear responsibility.
