# ADR-014: Configuration System Refactoring

**Status**: Accepted  
**Date**: 2025-06-17  
**Decision Makers**: Development Team  
**Supersedes**: Previous configuration approaches in ADR-001, ADR-005

## Context

The Forge CLI originally used a `SearchConfig` class that evolved organically as features were added. With the migration to chat-first architecture (ADR-012) and the adoption of typed-only APIs (ADR-007), the configuration system needed significant refactoring to:

### Original Configuration Problems

1. **Misleading Name**: `SearchConfig` didn't reflect the full scope of application configuration
2. **Weak Validation**: Manual validation with inconsistent error handling
3. **Type Safety Issues**: Mixed use of optional types and default values
4. **Poor Extensibility**: Difficult to add new configuration options
5. **Inconsistent Defaults**: Default values scattered across codebase
6. **Limited Validation**: No field-level or cross-field validation
7. **Poor Documentation**: Configuration options not self-documenting

### Growing Configuration Complexity

The application now requires configuration for:
- Model settings (model, effort, temperature, tokens)
- Tool management (enabled tools, vector store IDs)
- Display preferences (render format, debug, quiet mode)
- Chat functionality (conversation management, reasoning display)
- Server connectivity (URL, authentication)
- Web search location (country, city)
- Performance tuning (throttling, caching)

## Decision

**Refactor configuration system** from `SearchConfig` to `AppConfig` with comprehensive Pydantic validation, type safety, and self-documenting field definitions.

### 1. Rename and Restructure

**Before (`SearchConfig`):**
```python
class SearchConfig:
    def __init__(self, **kwargs):
        self.model = kwargs.get("model", "qwen-max-latest")
        self.vec_ids = kwargs.get("vec_ids", [])
        self.tools = kwargs.get("tools", [])
        # ... manual assignment and validation
```

**After (`AppConfig`):**
```python
class AppConfig(BaseModel):
    """Central configuration for the forge-cli application."""
    
    # Model settings with validation
    model: str = "qwen-max-latest"
    effort: EffortLevel = "low"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1000, gt=0)
    
    # Tool settings with aliases
    enabled_tools: list[ToolType] = Field(default_factory=lambda: ["file-search"], alias="tool")
    vec_ids: list[str] = Field(default_factory=lambda: DEFAULT_VEC_IDS.copy(), alias="vec_id")
```

### 2. Comprehensive Type Safety

```python
# Define precise types for configuration
EffortLevel = Literal["low", "medium", "high"]
ToolType = Literal[
    "file-search", "web-search", "code-analyzer", "function", 
    "computer", "list-documents", "file-reader", "page-reader"
]

class AppConfig(BaseModel):
    # All fields have precise types
    model: str = "qwen-max-latest"
    effort: EffortLevel = "low"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1000, gt=0)
    enabled_tools: list[ToolType] = Field(default_factory=lambda: ["file-search"])
    vec_ids: list[str] = Field(default_factory=lambda: DEFAULT_VEC_IDS.copy())
    render_format: str = Field(default="rich", alias="render")
    debug: bool = False
    quiet: bool = False
```

### 3. Advanced Validation

```python
class AppConfig(BaseModel):
    @field_validator("vec_ids")
    @classmethod
    def validate_vec_ids(cls, v: list[str]) -> list[str]:
        """Validate vector store IDs format."""
        for vec_id in v:
            if not vec_id or not isinstance(vec_id, str):
                raise ValueError(f"Invalid vector store ID: {vec_id}")
        return v

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        """Validate server URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Server URL must start with http:// or https://")
        return v.rstrip("/")

    @model_validator(mode="after")
    def validate_config_consistency(self) -> "AppConfig":
        """Validate configuration consistency."""
        # Cross-field validation
        if any(tool in ["file-search", "list-documents"] for tool in self.enabled_tools):
            if not self.vec_ids:
                raise ValueError("Vector store IDs required when file search tools are enabled")
        return self
```

### 4. Intelligent Configuration Creation

```python
class AppConfig(BaseModel):
    @classmethod
    def from_args(cls, args) -> "AppConfig":
        """Create config from command line arguments using Pydantic validation."""
        # Convert args namespace to dict and filter out None values
        args_dict = {k: v for k, v in vars(args).items() if v is not None}
        
        # Create config with validation - Pydantic handles aliases automatically
        return cls.model_validate(args_dict)

    def apply_dataset_config(self, dataset, args) -> "AppConfig":
        """Apply dataset configuration with proper tool enablement logic."""
        updates = {}
        
        # Use vectorstore ID from dataset if no command line vec_ids provided
        if dataset and dataset.vectorstore_id and not getattr(args, "vec_id", None):
            updates["vec_ids"] = [dataset.vectorstore_id]
            # Enable file-search tool when using dataset
            if "file-search" not in self.enabled_tools:
                updates["enabled_tools"] = self.enabled_tools + ["file-search"]
        
        # Return new instance with updates if any, otherwise return self
        if updates:
            return self.model_copy(update=updates)
        return self
```

## Implementation Benefits

### 1. Self-Documenting Configuration

```python
class AppConfig(BaseModel):
    """Central configuration for the forge-cli application."""
    
    # Model settings
    model: str = "qwen-max-latest"  # AI model to use for responses
    effort: EffortLevel = "low"     # Computational effort level
    temperature: float = Field(     # Response randomness (0.0-2.0)
        default=0.7, 
        ge=0.0, 
        le=2.0,
        description="Controls response randomness"
    )
    
    # Tool settings
    enabled_tools: list[ToolType] = Field(
        default_factory=lambda: ["file-search"],
        alias="tool",
        description="List of enabled tools for the session"
    )
```

### 2. Automatic CLI Integration

```python
# CLI parser automatically works with Pydantic aliases
parser.add_argument("--tool", "-t", action="append", ...)      # Maps to enabled_tools
parser.add_argument("--vec-id", action="append", ...)          # Maps to vec_ids  
parser.add_argument("--render", choices=["json", "rich"], ...) # Maps to render_format

# Configuration creation is seamless
config = AppConfig.from_args(args)  # Automatic validation and type conversion
```

### 3. Environment Variable Integration

```python
class AppConfig(BaseModel):
    server_url: str = Field(
        default_factory=lambda: os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
        alias="server",
        description="Knowledge Forge server URL"
    )
    
    # Pydantic can also integrate with pydantic-settings for full env var support
```

### 4. Configuration Serialization

```python
# Easy serialization for debugging and persistence
config = AppConfig.from_args(args)

# JSON serialization
config_json = config.model_dump_json(indent=2)

# Dictionary for API calls
config_dict = config.model_dump(exclude_none=True)

# Partial updates
updated_config = config.model_copy(update={"model": "gpt-4"})
```

## Migration Impact

### Breaking Changes
1. **Class Name**: `SearchConfig` → `AppConfig`
2. **Import Path**: Configuration class location may change
3. **Validation**: Stricter validation may reject previously accepted values
4. **Field Names**: Some internal field names standardized

### Compatibility Measures
1. **Gradual Migration**: Old and new config can coexist during transition
2. **Validation Messages**: Clear error messages for invalid configurations
3. **Default Preservation**: All existing defaults maintained
4. **Alias Support**: CLI arguments remain unchanged via Pydantic aliases

### Migration Example

```python
# Old approach
try:
    config = SearchConfig(
        model=args.model,
        vec_ids=args.vec_id or [],
        tools=args.tool or [],
        debug=args.debug
    )
    # Manual validation
    if config.tools and not config.vec_ids:
        raise ValueError("Vector IDs required for file search")
except Exception as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# New approach
try:
    config = AppConfig.from_args(args)  # Automatic validation
except ValidationError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

## Advanced Features

### 1. Configuration Profiles

```python
# Future: Configuration profiles
class AppConfig(BaseModel):
    @classmethod
    def load_profile(cls, profile_name: str) -> "AppConfig":
        """Load predefined configuration profile."""
        profiles = {
            "research": cls(
                model="gpt-4",
                enabled_tools=["file-search", "web-search"],
                show_reasoning=True
            ),
            "coding": cls(
                model="claude-3",
                enabled_tools=["code-analyzer", "file-search"],
                render_format="plaintext"
            )
        }
        return profiles.get(profile_name, cls())
```

### 2. Dynamic Configuration Updates

```python
# Configuration can be updated during chat sessions
class ConversationState(BaseModel):
    def update_config(self, **updates) -> None:
        """Update configuration during conversation."""
        # Validate updates
        updated_config = self.config.model_copy(update=updates)
        self.config = updated_config
```

## Consequences

### ✅ Positive
1. **Type Safety**: Complete type checking and IDE support
2. **Validation**: Comprehensive field and cross-field validation
3. **Documentation**: Self-documenting configuration with descriptions
4. **Maintainability**: Easy to add new configuration options
5. **Error Messages**: Clear, helpful validation error messages
6. **Serialization**: Built-in JSON serialization and deserialization
7. **Extensibility**: Easy to extend with new fields and validation

### ⚠️ Considerations
1. **Dependency**: Adds Pydantic as a core dependency
2. **Learning Curve**: Developers need to understand Pydantic patterns
3. **Migration Effort**: Existing code needs updates for new class name

### 🔄 Mitigation Strategies
1. **Documentation**: Comprehensive examples and migration guide
2. **Gradual Adoption**: Phased migration approach
3. **Testing**: Extensive test coverage for configuration validation

## Related ADRs

- **ADR-001**: Command-Line Interface Design (updated for AppConfig)
- **ADR-005**: Interactive Chat Mode Implementation (uses AppConfig)
- **ADR-007**: Typed-Only Architecture Migration (enables Pydantic adoption)
- **ADR-012**: Chat-First Architecture Migration (requires configuration updates)

---

**Key Insight**: The migration to `AppConfig` with Pydantic transforms configuration from a source of bugs and confusion into a robust, self-documenting, and type-safe foundation for the entire application.
