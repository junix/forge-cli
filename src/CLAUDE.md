# Source Directory - Main Implementation Code

## Overview

The `src/` directory contains the main implementation code for the Forge CLI project. It houses the complete Python package structure with all modules, components, and functionality that make up the Knowledge Forge API client and command-line interface.

## Directory Structure

```
src/
├── CLAUDE.md                    # This documentation file
└── forge_cli/                   # Main Python package
    ├── CLAUDE.md                # Package-level documentation
    ├── __init__.py              # Package initialization
    ├── main.py                  # CLI entry point
    ├── config.py                # Configuration management
    ├── chat.py                  # Interactive chat mode
    ├── cli/                     # Command-line interface components
    ├── common/                  # Common utilities and helpers
    ├── core/                    # Core functionality
    ├── models/                  # Data models and type definitions
    ├── response/                # Response handling and types
    ├── sdk/                     # Python SDK for Knowledge Forge API
    ├── display/                 # Display and rendering system
    ├── stream/                  # Stream processing
    ├── chat/                    # Chat mode implementation
    ├── style/                   # Styling and formatting
    └── utils/                   # Utility functions
```

## Architecture Overview

### Package Organization

The source code is organized following modern Python package structure principles:

1. **Single Package Root**: All code under `forge_cli/` package
2. **Modular Design**: Clear separation of concerns across modules
3. **Type Safety**: Comprehensive type annotations throughout
4. **Import Conventions**: Consistent relative/absolute import patterns
5. **Documentation**: Each module has its own CLAUDE.md file

### Core Components

#### Entry Points

- **main.py**: Primary CLI entry point with argument parsing
- **chat.py**: Interactive chat mode entry point
- **config.py**: Configuration management and environment setup

#### Core Functionality

- **sdk/**: Complete Python SDK for Knowledge Forge API
- **response/**: Response type definitions and processing
- **models/**: Internal data models and state management
- **core/**: Core business logic and functionality

#### User Interface

- **cli/**: Command-line interface components
- **display/**: V3 snapshot-based display architecture
- **chat/**: Interactive chat mode with command system
- **style/**: Styling and formatting utilities

#### Supporting Modules

- **stream/**: Event stream processing and handling
- **common/**: Shared utilities and common functionality
- **utils/**: General utility functions

## Key Design Principles

### Type Safety First

The entire codebase uses comprehensive type annotations:

```python
# Pydantic models for data validation
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    model: str = "qwen-max-latest"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    tools: set[str] = Field(default_factory=set)

# TypeGuard functions for safe type narrowing
from typing import TypeGuard
from forge_cli.response._types.response import ResponseOutputItem

def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    return hasattr(item, 'type') and item.type == "file_search_call"
```

### Modular Architecture

Each module has a clear, single responsibility:

- **SDK**: API communication and data handling
- **Display**: User interface and output formatting
- **Models**: Data structures and validation
- **Response**: API response processing
- **Chat**: Interactive user experience

### Import Conventions

The codebase follows strict import conventions:

```python
# Top-level modules use absolute imports
from forge_cli.sdk import async_create_typed_response
from forge_cli.models import StreamState
from forge_cli.display.v3.base import Display

# Subdirectory modules use relative imports
from .base import BaseProcessor
from ..models.state import StreamState
from ...response._types.response import Response
```

## Development Guidelines

### Adding New Modules

When adding new functionality:

1. **Choose Appropriate Location**: Place code in the most logical module
2. **Follow Naming Conventions**: Use clear, descriptive module names
3. **Create Documentation**: Add CLAUDE.md file for new directories
4. **Use Type Annotations**: Comprehensive type hints throughout
5. **Follow Import Patterns**: Use established import conventions

### Module Structure

Standard module structure:

```python
"""
Module description and purpose.

This module provides...
"""

from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel

if TYPE_CHECKING:
    # Type-only imports to avoid circular dependencies
    from forge_cli.response._types.response import Response

class ModuleClass(BaseModel):
    """Class documentation."""
    field: str
    optional_field: Optional[int] = None

def module_function(param: str) -> bool:
    """Function documentation."""
    # Implementation
    return True
```

### Testing Strategy

Each module should have corresponding tests:

```
src/forge_cli/module/
├── __init__.py
├── implementation.py
└── tests/
    ├── __init__.py
    └── test_implementation.py
```

## Package Dependencies

### Core Dependencies

- **pydantic>=2.0.0**: Data validation and serialization
- **aiohttp>=3.8.0**: Async HTTP client for API communication
- **rich>=12.0.0**: Rich terminal UI components
- **loguru>=0.6.0**: Advanced logging with structured output

### Optional Dependencies

- **prompt-toolkit>=3.0.0**: Interactive command line features
- **requests>=2.25.0**: Fallback HTTP client for compatibility

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Static type checking
- **ruff**: Fast Python linter

## Build and Distribution

### Package Configuration

The package is configured in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "forge-cli"
version = "1.0.0"
description = "Modern CLI for Knowledge Forge API"
dependencies = [
    "pydantic>=2.0.0",
    "aiohttp>=3.8.0",
    "rich>=12.0.0",
    "loguru>=0.6.0"
]
```

### Entry Points

CLI entry points are defined for easy installation:

```toml
[project.scripts]
forge-cli = "forge_cli.main:main"
```

## Quality Assurance

### Code Quality Tools

- **Type Checking**: mypy for static type analysis
- **Linting**: ruff for fast, comprehensive linting
- **Formatting**: black for consistent code formatting
- **Testing**: pytest with comprehensive test coverage

### CI/CD Integration

The source code integrates with continuous integration:

1. **Automated Testing**: Run test suite on all changes
2. **Type Checking**: Verify type annotations
3. **Code Quality**: Lint and format checking
4. **Documentation**: Verify documentation completeness

## Related Documentation

- **Package Documentation** (`forge_cli/CLAUDE.md`) - Detailed package overview
- **API Reference** (`../docs/api_reference/`) - API documentation
- **ADRs** (`../docs/adr/`) - Architectural decisions
- **Examples** (`../scripts/`) - Usage examples

## Best Practices

### Code Organization

1. **Single Responsibility**: Each module has one clear purpose
2. **Clear Dependencies**: Minimize coupling between modules
3. **Type Safety**: Use Pydantic models and type annotations
4. **Documentation**: Document all public interfaces
5. **Testing**: Comprehensive test coverage

### Development Workflow

1. **Follow Conventions**: Use established patterns and naming
2. **Write Tests**: Test-driven development approach
3. **Type Check**: Verify type annotations with mypy
4. **Document Changes**: Update documentation with code changes
5. **Review Code**: Peer review for quality assurance

The source directory represents the complete implementation of the Forge CLI project, demonstrating modern Python development practices with comprehensive type safety, modular design, and excellent developer experience.
