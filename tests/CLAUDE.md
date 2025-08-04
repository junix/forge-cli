# Tests Directory - Comprehensive Test Suite

## Overview

The tests directory contains the comprehensive test suite for the Forge CLI project. It includes unit tests, integration tests, demonstration scripts, and testing utilities that ensure code quality, functionality, and reliability across all components of the system.

## Directory Structure

```
tests/
├── CLAUDE.md                           # This documentation file
├── core/                              # Core functionality tests
│   ├── __init__.py                    # Test package initialization
│   ├── test_chunk.py                  # Chunk data structure tests
│   ├── test_document.py               # Document handling tests
│   ├── test_document_content.py       # Document content processing tests
│   └── test_page.py                   # Page processing tests
├── display/                           # Display system tests and demos
│   ├── demo_file_reader_render.py     # File reader renderer demo
│   ├── demo_rendable_architecture.py  # Renderable architecture demo
│   ├── demo_tool_renderers.py         # Tool renderer demonstrations
│   ├── demo_welcome_renderer.py       # Welcome screen renderer demo
│   ├── test_builder_demo.py           # Builder pattern tests
│   ├── test_file_reader_render.py     # File reader rendering tests
│   ├── test_helper.py                 # Display helper function tests
│   ├── test_plaintext_modular.py      # Plaintext renderer tests
│   ├── test_rendable_classes.py       # Renderable class tests
│   ├── test_sliding_display.py        # Sliding display tests
│   ├── test_text_builder.py           # Text builder tests
│   ├── test_tool_renderers.py         # Tool renderer tests
│   ├── test_web_search_renderer.py    # Web search renderer tests
│   └── test_welcome_renderer.py       # Welcome renderer tests
└── response/                          # Response handling tests
    ├── __init__.py                    # Response test package
    └── test_type_guards.py            # TypeGuard function tests
```

## Test Categories

### Core Functionality Tests (core/)

#### Data Structure Tests

- **test_chunk.py**: Tests for chunk data structures and processing
  - Chunk creation and validation
  - Chunk metadata handling
  - Chunk serialization/deserialization
  - Edge cases and error conditions

- **test_document.py**: Document handling and processing tests
  - Document parsing and validation
  - Document metadata extraction
  - Document format support
  - Error handling for invalid documents

- **test_document_content.py**: Document content processing tests
  - Content extraction and formatting
  - Content validation and sanitization
  - Content type detection
  - Performance testing for large documents

- **test_page.py**: Page-level processing tests
  - Page extraction and numbering
  - Page content validation
  - Page metadata handling
  - Multi-page document processing

### Display System Tests (display/)

#### Renderer Tests

- **test_file_reader_render.py**: File reader renderer functionality
- **test_plaintext_modular.py**: Plaintext renderer modular design
- **test_tool_renderers.py**: Tool-specific renderer tests
- **test_web_search_renderer.py**: Web search result rendering
- **test_welcome_renderer.py**: Welcome screen rendering

#### Architecture Tests

- **test_rendable_classes.py**: Renderable class architecture
- **test_builder_demo.py**: Builder pattern implementation
- **test_text_builder.py**: Text building utilities
- **test_sliding_display.py**: Sliding display functionality
- **test_helper.py**: Display helper functions

#### Demonstration Scripts

- **demo_file_reader_render.py**: Interactive file reader demo
- **demo_rendable_architecture.py**: Architecture demonstration
- **demo_tool_renderers.py**: Tool renderer showcase
- **demo_welcome_renderer.py**: Welcome screen demo

### Response Handling Tests (response/)

#### Type Safety Tests

- **test_type_guards.py**: TypeGuard function validation
  - Type narrowing functionality
  - Type safety verification
  - Edge case handling
  - Performance testing

## Testing Philosophy

### Design Principles

1. **Comprehensive Coverage**: Test all critical functionality
2. **Type Safety Validation**: Verify type annotations and TypeGuards
3. **Edge Case Testing**: Test boundary conditions and error cases
4. **Performance Testing**: Ensure acceptable performance characteristics
5. **Integration Testing**: Test component interactions

### Testing Strategies

#### Unit Testing

- **Isolated Testing**: Test individual components in isolation
- **Mock Dependencies**: Use mocks for external dependencies
- **Pydantic Validation**: Test model validation and serialization
- **Error Conditions**: Test error handling and edge cases

#### Integration Testing

- **Component Interaction**: Test how components work together
- **End-to-End Workflows**: Test complete user workflows
- **API Integration**: Test SDK and API interactions
- **Display Integration**: Test display system with real data

#### Demonstration Testing

- **Interactive Demos**: Scripts that demonstrate functionality
- **Visual Testing**: Manual verification of display output
- **Performance Demos**: Scripts showing performance characteristics
- **Usage Examples**: Practical examples of component usage

## Test Implementation Patterns

### Standard Test Structure

```python
"""
Test module for [component name].

Tests cover:
- Basic functionality
- Edge cases and error conditions
- Type safety and validation
- Performance characteristics
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from forge_cli.component import ComponentClass
from forge_cli.models import DataModel

class TestComponentClass:
    """Test suite for ComponentClass."""
    
    def test_basic_functionality(self):
        """Test basic component functionality."""
        component = ComponentClass()
        result = component.process("test input")
        assert result is not None
    
    def test_validation_error(self):
        """Test validation error handling."""
        with pytest.raises(ValidationError):
            DataModel(invalid_field="invalid")
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async component functionality."""
        component = ComponentClass()
        result = await component.async_process("test input")
        assert result is not None
```

### TypeGuard Testing

```python
"""Test TypeGuard functions for type safety."""

from forge_cli.response.type_guards.output_items import is_file_search_call
from forge_cli.response._types.response import ResponseFileSearchToolCall

def test_file_search_type_guard():
    """Test file search TypeGuard function."""
    # Valid file search call
    valid_call = ResponseFileSearchToolCall(
        type="file_search_call",
        id="search_123",
        queries=["test query"],
        status="completed"
    )
    assert is_file_search_call(valid_call)
    
    # Invalid call
    invalid_call = {"type": "other_call"}
    assert not is_file_search_call(invalid_call)
```

### Display Testing

```python
"""Test display components with mock data."""

from forge_cli.display.v3.renderers.rich import RichRenderer
from forge_cli.response._types.response import Response

def test_rich_renderer():
    """Test Rich renderer with sample response."""
    renderer = RichRenderer()
    
    # Mock response data
    response = Response(
        id="resp_123",
        output_text="Test response",
        output=[]
    )
    
    # Test rendering (capture output for verification)
    with patch('builtins.print') as mock_print:
        renderer.render_response(response)
        mock_print.assert_called()
```

## Running Tests

### Test Execution

```bash
# Run all tests
python -m pytest tests/

# Run specific test directory
python -m pytest tests/core/
python -m pytest tests/display/
python -m pytest tests/response/

# Run specific test file
python -m pytest tests/core/test_chunk.py

# Run with coverage
python -m pytest tests/ --cov=forge_cli --cov-report=html

# Run with verbose output
python -m pytest tests/ -v

# Run only failed tests
python -m pytest tests/ --lf
```

### Demo Scripts

```bash
# Run display demos
python tests/display/demo_file_reader_render.py
python tests/display/demo_tool_renderers.py
python tests/display/demo_welcome_renderer.py

# Run architecture demos
python tests/display/demo_rendable_architecture.py
```

## Test Configuration

### pytest Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = src/forge_cli
omit = 
    */tests/*
    */test_*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Quality Assurance

### Test Quality Standards

1. **Clear Test Names**: Descriptive test function names
2. **Comprehensive Coverage**: Test all critical code paths
3. **Isolated Tests**: Tests don't depend on each other
4. **Fast Execution**: Tests run quickly for rapid feedback
5. **Reliable Results**: Tests are deterministic and stable

### Continuous Integration

Tests integrate with CI/CD pipeline:

1. **Automated Execution**: Run on every commit
2. **Coverage Reporting**: Track test coverage metrics
3. **Performance Monitoring**: Track test execution time
4. **Quality Gates**: Prevent merging if tests fail

## Related Components

- **Source Code** (`../src/forge_cli/`) - Code being tested
- **SDK Tests** (`../src/forge_cli/sdk/tests/`) - SDK-specific tests
- **Documentation** (`../docs/`) - Test documentation and examples
- **Scripts** (`../scripts/`) - Utility scripts for testing

## Best Practices

### Writing Tests

1. **Test Behavior**: Focus on what the code should do
2. **Use Fixtures**: Share common test setup
3. **Mock External Dependencies**: Isolate units under test
4. **Test Edge Cases**: Include boundary conditions
5. **Keep Tests Simple**: One concept per test

### Maintaining Tests

1. **Update with Code**: Keep tests in sync with implementation
2. **Refactor Tests**: Improve test quality over time
3. **Remove Obsolete Tests**: Clean up tests for removed features
4. **Monitor Coverage**: Maintain high test coverage
5. **Review Test Failures**: Investigate and fix failing tests promptly

The test suite ensures the reliability, correctness, and maintainability of the Forge CLI project through comprehensive testing strategies and quality assurance practices.
