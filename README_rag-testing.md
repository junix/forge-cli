# RAG Testing Framework

A comprehensive testing framework for the Knowledge Forge RAG (Retrieval-Augmented Generation) system, designed to ensure all API options and configurations work correctly.

## Overview

This testing framework provides:
- **JSON-based test specification** for defining test cases
- **Automated test runner** for executing tests
- **Programmatic API** for custom test workflows
- **Comprehensive coverage** of all RAG system features

## Components

### 1. Test Specification (`rag-test-spec.json`)

The test specification defines all test cases in a structured JSON format:

```json
{
  "version": "1.0.0",
  "defaults": {
    "base_url": "${KNOWLEDGE_FORGE_URL:-http://localhost:9999}",
    "vector_store_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "file_id": "f8e5d7c6-b9a8-4321-9876-543210abcdef",
    "model": "qwen3-235b-a22b",
    "effort": "low"
  },
  "test_suites": [
    {
      "name": "smoke_tests",
      "tests": [...]
    }
  ]
}
```

### 2. Test Runner (`rag-test-runner.py`)

Automated test execution with filtering and reporting:

```bash
# Run all tests
python rag-test-runner.py

# Run specific suite
python rag-test-runner.py --suite smoke_tests

# Run specific test
python rag-test-runner.py --test file_search

# Save results
python rag-test-runner.py --save-results
```

### 3. Test Loader API (`rag-test-example.py`)

Programmatic access to test cases for custom workflows:

```python
from rag_test_example import TestCaseLoader

loader = TestCaseLoader()
test = loader.get_test_by_id("smoke_file_search")
request = loader.build_request(test)
```

## Test Coverage

### Task Types
- **Plain Chat**: Basic conversational AI without tools
- **File Search**: Vector store document search
- **Web Search**: Real-time web information retrieval
- **File Reader**: Direct file content analysis
- **Multi-Tool**: Combinations of the above

### Configuration Options
- **Models**: Multiple LLM providers (Qwen, DeepSeek, etc.)
- **Effort Levels**: `dev`, `low`, `medium`, `high`
- **Tool Choice**: `auto`, `none`, `required`, or specific tool selection
- **Custom Queries**: User-defined prompts for each test

### Edge Cases
- Invalid IDs (vector store, file)
- Conflicting configurations
- Empty inputs
- Network timeouts
- Error responses

## Test Structure

Each test case includes:

```json
{
  "id": "unique_test_id",
  "name": "Human-readable name",
  "description": "What this test validates",
  "request": {
    "task_type": "file-search",
    "parameters": {
      "model": "qwen3-235b-a22b",
      "effort": "medium",
      "query": "Search query",
      "tool_choice": "auto"
    }
  },
  "expected": {
    "status_code": 200,
    "required_events": ["response.created", "response.done"],
    "tool_calls": ["file_search"],
    "response_contains": ["expected", "terms"]
  }
}
```

## Validation Rules

Tests validate:
- **Status Codes**: Expected HTTP response codes
- **Event Sequences**: Required SSE events in correct order
- **Tool Execution**: Proper tool calls and completions
- **Response Content**: Keywords, length, language
- **Performance**: Response time limits per task type

## Usage Examples

### Running Smoke Tests
```bash
# Quick validation of core functionality
python rag-test-runner.py --suite smoke_tests
```

### Testing Specific Features
```bash
# Test all file search variations
python rag-test-runner.py --test file_search

# Test tool choice configurations
python rag-test-runner.py --suite tool_choice_tests
```

### Custom Test Execution
```python
#!/usr/bin/env python3
from rag_test_example import TestCaseLoader
import requests

loader = TestCaseLoader()

# Get high-effort tests
high_effort_tests = [
    test for test in loader.test_index.values()
    if test["request"]["parameters"].get("effort") == "high"
]

# Execute with custom logic
for test in high_effort_tests:
    request = loader.build_request(test)
    # Custom execution and validation
```

## Extending the Framework

### Adding New Test Cases

1. Add to appropriate suite in `rag-test-spec.json`:
```json
{
  "id": "new_test_case",
  "name": "New Feature Test",
  "request": {...},
  "expected": {...}
}
```

2. Define validation criteria in `expected` section

3. Run the test:
```bash
python rag-test-runner.py --test new_test_case
```

### Creating New Test Suites

```json
{
  "name": "performance_tests",
  "description": "Performance and load testing",
  "tests": [
    {
      "id": "perf_large_query",
      "name": "Large Query Performance",
      "request": {...},
      "expected": {
        "max_response_time": 5000
      }
    }
  ]
}
```

## Best Practices

1. **Comprehensive Coverage**: Test all parameter combinations
2. **Clear Naming**: Use descriptive test IDs and names
3. **Validation Specificity**: Define precise expected outcomes
4. **Maintainability**: Group related tests in suites
5. **Documentation**: Include descriptions for complex tests

## Integration with CI/CD

```yaml
# Example GitHub Actions workflow
name: RAG Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run smoke tests
        run: python rag-test-runner.py --suite smoke_tests
      - name: Run full test suite
        run: python rag-test-runner.py --save-results
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: rag-test-results.json
```

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure server is running at configured URL
2. **Missing IDs**: Verify vector store and file IDs exist
3. **Timeout Errors**: Increase timeout in test spec defaults
4. **Validation Failures**: Check expected criteria match actual behavior

### Debug Mode

```bash
# Enable verbose logging
python rag-test-runner.py --verbose

# Test single case with detailed output
python rag-test-runner.py --test specific_test_id -v
```

## Future Enhancements

- [ ] Performance benchmarking
- [ ] Load testing capabilities
- [ ] Visual test report generation
- [ ] Test data generation utilities
- [ ] Integration with monitoring systems

## Contributing

When adding new tests:
1. Follow existing patterns in the spec
2. Test locally before committing
3. Update this documentation if needed
4. Consider edge cases and error scenarios