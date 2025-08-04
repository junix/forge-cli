# Scripts Directory - Utility Scripts and Examples

## Overview

The scripts directory contains utility scripts and example programs that demonstrate various aspects of the Forge CLI and Knowledge Forge API. These scripts serve as both practical tools for development and testing, as well as educational examples for developers learning to use the API.

## Directory Structure

```
scripts/
├── CLAUDE.md                           # This documentation file
├── __init__.py                         # Python package initialization
├── create-and-query-vectorstore.py    # Complete vector store workflow
├── create-files.py                     # File upload and management examples
├── create-fix-dataset.py               # Dataset creation and processing
├── create-vectorstore.py               # Vector store creation examples
├── debug.py                            # Debugging and testing utilities
├── join-file.py                        # File joining to vector stores
└── query-vectorstore.py                # Vector store querying examples
```

## Script Categories

### Vector Store Management

#### create-vectorstore.py
- **Purpose**: Demonstrates vector store creation with files
- **Features**:
  - File upload and processing
  - Vector store creation with metadata
  - Error handling and validation
  - Progress tracking
- **Usage**: `python scripts/create-vectorstore.py`
- **Example Use Cases**:
  - Setting up knowledge bases
  - Batch processing documents
  - Testing vector store functionality

#### query-vectorstore.py
- **Purpose**: Shows how to perform semantic searches
- **Features**:
  - Vector store querying with filters
  - Result ranking and processing
  - Multiple query strategies
  - Result formatting
- **Usage**: `python scripts/query-vectorstore.py --vs-id <id> --query "search term"`
- **Example Use Cases**:
  - Testing search quality
  - Benchmarking query performance
  - Exploring semantic search capabilities

#### create-and-query-vectorstore.py
- **Purpose**: Complete end-to-end vector store workflow
- **Features**:
  - File upload → vector store creation → querying
  - Comprehensive error handling
  - Performance measurement
  - Result validation
- **Usage**: `python scripts/create-and-query-vectorstore.py --files file1.pdf file2.txt`
- **Example Use Cases**:
  - Full workflow testing
  - Integration testing
  - Performance benchmarking

#### join-file.py
- **Purpose**: Add files to existing vector stores
- **Features**:
  - File upload and validation
  - Vector store file joining
  - Batch operations
  - Status monitoring
- **Usage**: `python scripts/join-file.py --vs-id <id> --file <path>`
- **Example Use Cases**:
  - Expanding existing knowledge bases
  - Incremental document addition
  - Testing file compatibility

### File Management

#### create-files.py
- **Purpose**: File upload and management examples
- **Features**:
  - Multiple file format support
  - Metadata extraction and validation
  - Async processing with tasks
  - Error handling and retry logic
- **Usage**: `python scripts/create-files.py --files file1.pdf file2.docx`
- **Example Use Cases**:
  - Testing file upload functionality
  - Validating file processing
  - Batch file operations

### Development and Testing

#### debug.py
- **Purpose**: Debugging utilities and API testing
- **Features**:
  - API endpoint testing
  - Response validation
  - Error reproduction
  - Performance profiling
- **Usage**: `python scripts/debug.py --test-api`
- **Example Use Cases**:
  - API troubleshooting
  - Response format validation
  - Performance analysis

#### create-fix-dataset.py
- **Purpose**: Dataset creation and processing utilities
- **Features**:
  - Data validation and cleaning
  - Format conversion
  - Batch processing
  - Quality assurance
- **Usage**: `python scripts/create-fix-dataset.py --input data.json --output fixed.json`
- **Example Use Cases**:
  - Data preparation
  - Quality assurance
  - Format standardization

## Usage Guidelines

### Running Scripts

#### Prerequisites
```bash
# Ensure environment is set up
export KNOWLEDGE_FORGE_URL=http://localhost:9999
export OPENAI_API_KEY=your-api-key  # if required

# Install dependencies
uv sync
# or
pip install -e .
```

#### Basic Usage Patterns
```bash
# Vector store creation
python scripts/create-vectorstore.py

# File upload
python scripts/create-files.py --files document.pdf

# Query existing vector store
python scripts/query-vectorstore.py --vs-id vs_123 --query "machine learning"

# Complete workflow
python scripts/create-and-query-vectorstore.py --files doc1.pdf doc2.txt
```

#### Advanced Usage
```bash
# Debug mode with detailed logging
python scripts/debug.py --test-api --verbose

# Batch processing with custom settings
python scripts/create-vectorstore.py --batch-size 10 --timeout 300

# Query with filters and ranking
python scripts/query-vectorstore.py --vs-id vs_123 --query "AI" --filters '{"type": "research"}' --top-k 20
```

### Development Patterns

#### Error Handling
All scripts implement comprehensive error handling:
```python
try:
    result = await async_operation()
    if result is None:
        logger.error("Operation failed")
        return False
except Exception as e:
    logger.error(f"Error: {e}")
    return False
```

#### Logging and Debug Output
Scripts use structured logging:
```python
from loguru import logger

logger.info("Starting operation")
logger.debug(f"Parameters: {params}")
logger.error(f"Operation failed: {error}")
```

#### Configuration Management
Scripts support environment variables and command-line arguments:
```python
import argparse
from forge_cli.config import AppConfig

parser = argparse.ArgumentParser()
parser.add_argument("--vs-id", help="Vector store ID")
args = parser.parse_args()

config = AppConfig()  # Loads from environment
```

## Educational Value

### Learning the SDK

Scripts demonstrate key SDK patterns:

1. **File Operations**: Upload, processing, metadata handling
2. **Vector Stores**: Creation, querying, management
3. **Error Handling**: Robust error handling patterns
4. **Async Programming**: Proper async/await usage
5. **Configuration**: Environment and argument handling

### API Integration Examples

Scripts show real-world API usage:

1. **Authentication**: API key and endpoint configuration
2. **Request Patterns**: Proper request formatting
3. **Response Handling**: Processing API responses
4. **Streaming**: Handling streaming responses
5. **Error Recovery**: Retry logic and error handling

### Best Practices

Scripts demonstrate:

1. **Type Safety**: Using Pydantic models and type hints
2. **Validation**: Input validation and error checking
3. **Logging**: Structured logging for debugging
4. **Testing**: Validation and testing patterns
5. **Documentation**: Clear code documentation

## Development Guidelines

### Adding New Scripts

When creating new scripts:

1. **Follow Patterns**: Use existing scripts as templates
2. **Include Documentation**: Add docstrings and comments
3. **Handle Errors**: Implement comprehensive error handling
4. **Use SDK**: Always use the official SDK functions
5. **Add Examples**: Include usage examples in docstrings

### Script Structure

Standard script structure:
```python
#!/usr/bin/env python3
"""
Script description and purpose.

Usage:
    python script_name.py [options]

Examples:
    python script_name.py --example
"""

import argparse
import asyncio
from loguru import logger
from forge_cli.sdk import sdk_functions

async def main():
    """Main script logic."""
    # Implementation here
    pass

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Script description")
    # Add arguments
    
    args = parser.parse_args()
    
    # Run async main
    asyncio.run(main())
```

### Testing Scripts

Scripts should be tested for:

1. **Functionality**: Core operations work correctly
2. **Error Handling**: Graceful error handling
3. **Edge Cases**: Boundary conditions and edge cases
4. **Performance**: Reasonable performance characteristics
5. **Documentation**: Clear usage instructions

## Related Components

- **SDK** (`../src/forge_cli/sdk/`) - API functions used by scripts
- **Main CLI** (`../src/forge_cli/main.py`) - CLI implementation
- **Configuration** (`../src/forge_cli/config.py`) - Configuration management
- **Examples** (`../src/forge_cli/scripts/`) - Additional example scripts

## Best Practices

### Script Development

1. **Use SDK Functions**: Always use official SDK rather than direct HTTP calls
2. **Handle Errors Gracefully**: Implement proper error handling and logging
3. **Validate Inputs**: Check arguments and environment variables
4. **Document Usage**: Include clear usage instructions and examples
5. **Follow Conventions**: Use established patterns and naming conventions

### Maintenance

1. **Keep Updated**: Ensure scripts work with latest SDK version
2. **Test Regularly**: Verify scripts work with current API
3. **Update Documentation**: Keep usage instructions current
4. **Monitor Dependencies**: Ensure all required packages are available
5. **Review Periodically**: Remove obsolete scripts and update examples

The scripts directory serves as both a practical toolkit for development and a comprehensive set of examples for learning the Knowledge Forge API and Forge CLI SDK.
