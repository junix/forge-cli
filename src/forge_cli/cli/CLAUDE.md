# CLI Module - Command Line Interface Components

## Overview

The CLI module provides the command-line interface components for the Forge CLI application. It handles argument parsing, command validation, and the translation of command-line arguments into internal data structures. This module implements the design principles established in ADR-001 for command-line interface design.

## Directory Structure

```
cli/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Module exports
└── parser.py                    # Command-line argument parsing
```

## Architecture & Design

### Design Principles

Following ADR-001 (Command-line Design), the CLI module implements:

1. **User-Friendly Interface**: Intuitive command structure and helpful error messages
2. **Flexible Tool Configuration**: Support for multiple tools and configurations
3. **Consistent Patterns**: Standardized argument naming and behavior
4. **Comprehensive Help**: Detailed help text and usage examples
5. **Type Safety**: Validated argument parsing with proper type conversion

### Core Components

#### parser.py - Argument Parsing

The main argument parser handles all command-line interface functionality:

**Key Features:**
- **Argument Validation**: Type checking and constraint validation
- **Tool Configuration**: Support for multiple tool types and configurations
- **Output Format Selection**: Multiple rendering options (rich, plain, json)
- **Configuration Integration**: Environment variable and config file support
- **Help System**: Comprehensive help text and usage examples

**Argument Categories:**

1. **Query Arguments**:
   - `-q, --query`: Main query text
   - `--input-messages`: Alternative input format

2. **Tool Configuration**:
   - `-t, --tools`: Tool selection (file-search, web-search, etc.)
   - `--vec-id`: Vector store IDs for file search
   - `--max-search-results`: Result limit configuration

3. **Model Configuration**:
   - `--model`: AI model selection
   - `--effort`: Processing effort level (low, medium, high)
   - `--temperature`: Response randomness control

4. **Output Control**:
   - `--render`: Output format (rich, plaintext, json)
   - `--debug`: Debug mode with detailed logging
   - `--quiet`: Minimal output mode

5. **Interactive Mode**:
   - `-i, --chat`: Interactive chat mode
   - `--load-conversation`: Load saved conversation

## Usage Patterns

### Basic Usage

```bash
# Simple query
forge-cli -q "What is machine learning?"

# Query with file search
forge-cli -q "Explain the documents" --vec-id vs_123

# Multiple tools
forge-cli -t file-search -t web-search --vec-id vs_123 -q "Compare docs with web"

# Custom model and settings
forge-cli -q "Complex analysis" --model gpt-4 --effort high --temperature 0.3
```

### Advanced Usage

```bash
# Interactive chat mode
forge-cli --chat

# Chat with initial configuration
forge-cli --chat -t file-search --vec-id vs_123

# Debug mode with detailed output
forge-cli --debug -q "Test query"

# JSON output for automation
forge-cli --render json -q "API query" > response.json

# Load saved conversation
forge-cli --chat --load-conversation session.json
```

### Tool Configuration

```bash
# File search with multiple vector stores
forge-cli -t file-search --vec-id vs_123 --vec-id vs_456 -q "Search query"

# Web search with location context
forge-cli -t web-search -q "Local news"

# Multiple tools with custom settings
forge-cli -t file-search -t web-search --vec-id vs_123 --max-search-results 20 -q "Comprehensive search"
```

## Implementation Details

### Argument Parser Structure

```python
def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="Modern CLI for Knowledge Forge API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  forge-cli -q "What is AI?"
  forge-cli -t file-search --vec-id vs_123 -q "Search docs"
  forge-cli --chat
        """
    )
    
    # Add argument groups
    query_group = parser.add_argument_group('Query Options')
    tool_group = parser.add_argument_group('Tool Configuration')
    model_group = parser.add_argument_group('Model Settings')
    output_group = parser.add_argument_group('Output Control')
    
    return parser
```

### Argument Validation

The parser includes comprehensive validation:

```python
def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments."""
    # Ensure query is provided for non-chat mode
    if not args.chat and not args.query:
        raise ValueError("Query required for non-interactive mode")
    
    # Validate tool configurations
    if 'file-search' in args.tools and not args.vector_store_ids:
        raise ValueError("Vector store IDs required for file search")
    
    # Validate model parameters
    if args.temperature < 0.0 or args.temperature > 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0")
```

### Configuration Integration

The CLI integrates with the configuration system:

```python
from ..config import AppConfig

def merge_config_and_args(args: argparse.Namespace) -> AppConfig:
    """Merge command-line arguments with configuration."""
    config = AppConfig()  # Load from environment/config file
    
    # Override with command-line arguments
    if args.model:
        config.model = args.model
    if args.temperature is not None:
        config.temperature = args.temperature
    if args.tools:
        config.tools = set(args.tools)
    
    return config
```

## Error Handling

### User-Friendly Error Messages

The CLI provides clear, actionable error messages:

```python
def handle_cli_error(error: Exception) -> None:
    """Handle CLI errors with user-friendly messages."""
    if isinstance(error, ValueError):
        print(f"Error: {error}")
        print("Use --help for usage information")
    elif isinstance(error, FileNotFoundError):
        print(f"Error: Configuration file not found: {error.filename}")
    else:
        print(f"Unexpected error: {error}")
        print("Use --debug for detailed error information")
```

### Validation Feedback

```python
def validate_vector_store_ids(ids: list[str]) -> list[str]:
    """Validate vector store ID format."""
    valid_ids = []
    for id_str in ids:
        if not id_str.startswith('vs_'):
            print(f"Warning: Vector store ID '{id_str}' should start with 'vs_'")
        valid_ids.append(id_str)
    return valid_ids
```

## Help System

### Comprehensive Help Text

The CLI provides detailed help information:

```python
def add_help_examples(parser: argparse.ArgumentParser) -> None:
    """Add comprehensive help examples."""
    parser.epilog = """
Examples:
  Basic usage:
    forge-cli -q "What is machine learning?"
    
  File search:
    forge-cli -t file-search --vec-id vs_123 -q "Search documents"
    
  Multiple tools:
    forge-cli -t file-search -t web-search --vec-id vs_123 -q "Compare sources"
    
  Interactive chat:
    forge-cli --chat
    forge-cli --chat -t file-search --vec-id vs_123
    
  Custom settings:
    forge-cli -q "Analysis" --model gpt-4 --effort high --temperature 0.3
    
  Output formats:
    forge-cli -q "Query" --render json > output.json
    forge-cli -q "Query" --render plaintext
    
  Debug mode:
    forge-cli --debug -q "Test query"
    """
```

### Context-Sensitive Help

```python
def show_tool_help(tool_name: str) -> None:
    """Show help for specific tools."""
    help_text = {
        'file-search': """
File Search Tool:
  Searches through uploaded documents using vector similarity.
  
  Required: --vec-id (vector store ID)
  Optional: --max-search-results (default: 10)
  
  Example: forge-cli -t file-search --vec-id vs_123 -q "search term"
        """,
        'web-search': """
Web Search Tool:
  Searches the web for current information.
  
  No additional configuration required.
  
  Example: forge-cli -t web-search -q "latest AI news"
        """
    }
    print(help_text.get(tool_name, f"No help available for tool: {tool_name}"))
```

## Integration Points

### Main Application Integration

The CLI module integrates with the main application:

```python
# In main.py
from .cli.parser import create_parser, validate_args, merge_config_and_args

def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        validate_args(args)
        config = merge_config_and_args(args)
        
        # Launch appropriate mode
        if args.chat:
            from .chat import start_chat_mode
            start_chat_mode(config)
        else:
            from .main import run_query
            run_query(args.query, config)
            
    except Exception as e:
        handle_cli_error(e)
        sys.exit(1)
```

### Configuration System Integration

```python
from ..config import AppConfig

def create_config_from_args(args: argparse.Namespace) -> AppConfig:
    """Create configuration from parsed arguments."""
    return AppConfig(
        model=args.model or "qwen-max-latest",
        temperature=args.temperature or 0.7,
        tools=set(args.tools) if args.tools else set(),
        vector_store_ids=args.vector_store_ids or [],
        render_format=args.render or "rich",
        debug_mode=args.debug or False
    )
```

## Related Components

- **Main Application** (`../main.py`) - Uses CLI parser for argument processing
- **Configuration** (`../config.py`) - Integrates with CLI argument parsing
- **Chat Mode** (`../chat/`) - Launched from CLI interactive mode
- **Display System** (`../display/`) - Uses CLI render format selection

## Best Practices

### CLI Design

1. **Intuitive Commands**: Use clear, memorable argument names
2. **Consistent Patterns**: Follow established CLI conventions
3. **Helpful Defaults**: Provide sensible default values
4. **Clear Error Messages**: Give actionable feedback on errors
5. **Comprehensive Help**: Include examples and detailed explanations

### Implementation

1. **Type Safety**: Use proper type annotations for arguments
2. **Validation**: Validate arguments early with clear error messages
3. **Configuration Integration**: Merge CLI args with config files
4. **Error Handling**: Provide user-friendly error handling
5. **Testing**: Include comprehensive tests for argument parsing

The CLI module provides a robust, user-friendly command-line interface that follows modern CLI design principles and integrates seamlessly with the rest of the Forge CLI application.
