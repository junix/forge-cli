# JSON Renderer for V3 Display System

The JSON renderer provides structured JSON output for Knowledge Forge responses, making it perfect for programmatic processing, logging, and integration with other systems.

## Features

- **Pure JSON Output**: Clean, structured JSON formatting of complete Response snapshots
- **Configurable Options**: Control pretty-printing, metadata inclusion, and output destination
- **File Output Support**: Write JSON directly to files with append/overwrite modes
- **Error Handling**: Graceful error handling with JSON error messages
- **Pydantic Configuration**: Type-safe configuration with validation
- **Logging Integration**: Uses loguru logger for internal diagnostics

## Configuration Options

```python
from forge_cli.display.v3.renderers.json import JsonDisplayConfig

config = JsonDisplayConfig(
    pretty_print=True,          # Format with indentation
    indent=2,                   # Spaces for indentation (0-8)
    include_metadata=False,     # Include renderer metadata
    include_usage=True,         # Include token usage stats
    include_timing=False,       # Include timing information
    output_file=None,          # Output file path (None = stdout)
    append_mode=False          # Append to file vs overwrite
)
```

## Basic Usage

```python
from forge_cli.display.v3.renderers.json import JsonRenderer, JsonDisplayConfig
from forge_cli.display.v3.base import Display

# Create renderer with config
config = JsonDisplayConfig(pretty_print=True, include_usage=True)
renderer = JsonRenderer(config=config)

# Create display
display = Display(renderer)

# Handle response (in real usage, response comes from API)
display.handle_response(response)
display.complete()
```

## Output to File

```python
config = JsonDisplayConfig(
    pretty_print=True,
    output_file="responses.json",
    append_mode=True  # Append multiple responses
)
renderer = JsonRenderer(config=config)
display = Display(renderer)

display.handle_response(response)
display.complete()  # File is automatically closed
```

## Output to String Buffer

```python
import io

output_buffer = io.StringIO()
renderer = JsonRenderer(output_stream=output_buffer)
display = Display(renderer)

display.handle_response(response)
display.complete()

json_output = output_buffer.getvalue()
# Process JSON string...
```

## JSON Structure

The renderer outputs structured JSON with the following format:

```json
{
  "id": "resp_12345",
  "status": "completed",
  "model": "claude-3-sonnet",
  "output": [
    {
      "type": "message",
      "content": [
        {
          "type": "output_text",
          "text": "Response text here...",
          "annotations": [
            {
              "type": "file_citation",
              "file_name": "document.pdf",
              "page_number": 5,
              "text": "Cited text"
            }
          ]
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50,
    "total_tokens": 150
  }
}
```

## Additional Methods

The JSON renderer supports all Display interface methods:

- `render_error(error)` - Outputs error as JSON
- `render_welcome(config)` - Outputs welcome message as JSON  
- `render_request_info(info)` - Outputs request info as JSON
- `render_status(message)` - Outputs status updates as JSON

## Use Cases

- **API Integration**: Process responses programmatically
- **Logging**: Store structured response logs  
- **Data Analysis**: Analyze conversation patterns
- **Testing**: Capture and validate response data
- **Debugging**: Inspect complete response structure

## Error Handling

The renderer handles errors gracefully, outputting JSON error messages:

```json
{
  "error": "JSON rendering failed",
  "message": "Serialization error details...",
  "response_id": "resp_12345"
}
```

## Performance

- Efficient JSON serialization with custom serializer for complex objects
- Streaming output with immediate flushing
- Minimal memory usage for large responses
- Optional metadata tracking for diagnostics 