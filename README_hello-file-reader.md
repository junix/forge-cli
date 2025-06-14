# Knowledge Forge File Reader

A command-line utility for interacting with the Knowledge Forge API to create document-grounded conversations with AI models.

## Features

- Query documents stored in Knowledge Forge using natural language
- Support for multiple file IDs
- Two streaming methods: callback-based and async iterator-based
- Rich display of document information
- Configurable parameters (model, effort level, etc.)
- JSON output mode for programmatic use
- Support for saving responses to files
- Throttling options for controlling output flow

## Installation

The script requires Python 3.7+ and the `aiohttp` library.

If `colorama` is available, colored output will be enabled automatically.

## Usage

Basic usage:

```bash
python -m commands.hello-file-reader -q "Summarize this document"
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--file-id FILE_ID [FILE_ID ...]` | File ID(s) to read from (can specify multiple) |
| `--question`, `-q` | Question to ask about the file content |
| `--model`, `-m` | Model to use for the response (default: qwen-max-latest) |
| `--effort`, `-e` | Effort level: low, medium, high, dev (default: low) |
| `--method` | Method to use for streaming: callback or stream (default: stream) |
| `--server` | Server URL (default: from env or http://localhost:9999) |
| `--debug`, `-d` | Enable debug output with detailed event information |
| `--info`, `-i` | Only display file information without sending a query |
| `--no-color` | Disable colored output |
| `--json` | Output the response as JSON |
| `--throttle` | Throttle the output by adding a delay between tokens (in milliseconds) |
| `--save` | Save the response to a file |
| `--quiet`, `-Q` | Quiet mode - minimal output (implies --no-color) |
| `--version`, `-v` | Show version information and exit |

### Examples

Query with a specific question:
```bash
python -m commands.hello-file-reader -q "What are the key findings in this document?"
```

Use specific file IDs and model:
```bash
python -m commands.hello-file-reader --file-id file_id1 file_id2 --model qwen-max --effort medium
```

Use development effort level with enhanced debugging:
```bash
python -m commands.hello-file-reader --file-id file_id1 --effort dev --debug
```

Use callback streaming method with debug output:
```bash
python -m commands.hello-file-reader --method callback --debug
```

Show only file information without querying:
```bash
python -m commands.hello-file-reader --info
```

Output as JSON for programmatic use:
```bash
python -m commands.hello-file-reader -q "Summarize" --json
```

Save response to a file:
```bash
python -m commands.hello-file-reader -q "Extract key points" --save output.txt
```

## Environment Variables

- `KNOWLEDGE_FORGE_URL`: Sets the server URL (can be overridden with `--server`)

## Credits

Part of the Knowledge Forge SDK toolkit.