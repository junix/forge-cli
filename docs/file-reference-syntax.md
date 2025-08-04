# File Reference Syntax (@)

The forge-cli chat system supports **@ file reference syntax** for directly referencing and questioning specific files in your conversations.

## Overview

Instead of using vector search or collection queries, you can directly reference files using the `@` symbol followed by a file ID. This creates a more natural and direct way to ask questions about specific documents.

## Syntax

```
@<file_id> <your question here>
```

### Examples

```bash
# Single file reference
@file_123 What are the main conclusions in this document?

# Multiple file references
Compare @doc_abc and @doc_xyz for similarities

# Complex queries with multiple files
Based on @report_2024, @analysis_data, and @summary_q3, what are the key trends?
```

## How It Works

### 1. **Auto-Completion**
When you type `@` in the chat, the system automatically provides auto-completion for available files:

- **File ID completion**: Shows matching file IDs as you type
- **Filename display**: Shows the actual filename for context
- **Smart matching**: Matches both file IDs and filenames

### 2. **Message Processing**
When you send a message with file references:

1. **Parsing**: The system detects `@file_id` patterns
2. **File Input Creation**: Creates `input_file` entries for each referenced file
3. **API Request**: Sends a structured request with both file inputs and text

### 3. **API Request Format**
A message like `@file_123 What is this about?` becomes:

```json
{
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_file", "file_id": "file_123"},
        {"type": "input_text", "text": "What is this about?"}
      ]
    }
  ]
}
```

## Usage Examples

### Basic File Questioning
```bash
@file_123 Summarize this document
@report_2024 What are the key findings?
@analysis_pdf Extract the methodology section
```

### Comparative Analysis
```bash
Compare @doc_a and @doc_b for differences
What are the similarities between @file1, @file2, and @file3?
Analyze the trends across @q1_report, @q2_report, @q3_report
```

### Complex Queries
```bash
Based on @financial_report and @market_analysis, what's the outlook?
Using @methodology_paper and @results_data, validate the conclusions
Cross-reference @policy_doc with @implementation_guide for gaps
```

## File Discovery

### Finding Available Files

Use these commands to discover files you can reference:

```bash
/documents          # Show uploaded documents in current conversation
/show-collections   # Show available vector store collections
/show-documents     # Show all accessible documents
```

### File ID Format

File IDs typically follow these patterns:
- `file_123456789` - Standard uploaded files
- `doc_abcdef123` - Document files
- Custom IDs if specified during upload

## Auto-Completion Features

### Interactive Completion
- **Trigger**: Type `@` to start file completion
- **Filtering**: Continue typing to filter matches
- **Display**: Shows both file ID and filename
- **Selection**: Use arrow keys and Enter to select

### Smart Matching
The auto-completion matches:
- **File ID**: `@file` matches `file_123`, `file_456`
- **Filename**: `@report` matches files with "report" in filename
- **Partial matches**: `@doc` matches `doc_abc`, `document_xyz`

## Implementation Details

### Components

1. **FileReferenceParser** (`src/forge_cli/chat/file_reference_parser.py`)
   - Parses `@file_id` patterns in messages
   - Creates structured input content for API requests
   - Handles multiple file references in single messages

2. **CommandCompleter** (`src/forge_cli/chat/command_completer.py`)
   - Extended to support `@` file completion
   - Integrates with conversation state for file lists
   - Provides rich completion with file metadata

3. **ConversationState** (`src/forge_cli/models/conversation.py`)
   - Enhanced `new_request()` method to detect file references
   - Creates appropriate API requests with file inputs
   - Maintains conversation history with file context

### Message Flow

```
User Input: "@file_123 What is this about?"
     ↓
FileReferenceParser.parse()
     ↓
create_file_input_message()
     ↓
ConversationState.new_request()
     ↓
API Request with input_file + input_text
     ↓
AI Response with file context
```

## Benefits

### Direct File Access
- **No search required**: Direct file reference without vector search
- **Precise targeting**: Ask questions about specific documents
- **Multiple files**: Reference several files in one query

### Enhanced UX
- **Auto-completion**: Easy file discovery and selection
- **Natural syntax**: Intuitive `@` reference pattern
- **Rich feedback**: Clear indication of referenced files

### API Efficiency
- **Structured requests**: Proper `input_file` usage
- **Context preservation**: Files loaded directly into AI context
- **Type safety**: Uses typed API with proper validation

## Limitations

### File Availability
- Only works with uploaded files in current conversation
- Requires valid file IDs (auto-completion helps avoid errors)
- Files must be accessible to the current user

### Syntax Rules
- File IDs must be alphanumeric with underscores/hyphens
- No spaces allowed in file references
- Case-sensitive matching

## Future Enhancements

### Planned Features
- **Vector store file completion**: Auto-complete files from vector stores
- **Filename aliases**: Use `@"filename.pdf"` syntax
- **File metadata display**: Show file info in completion menu
- **Batch file operations**: Enhanced multi-file processing

### Integration Opportunities
- **Command integration**: Combine with `/topk` and other commands
- **History tracking**: Remember frequently referenced files
- **Smart suggestions**: Suggest relevant files based on context

## Troubleshooting

### Common Issues

**Auto-completion not working**:
- Ensure `prompt_toolkit` is installed
- Check that files are uploaded to current conversation
- Verify interactive terminal environment

**File not found errors**:
- Use `/documents` to verify file availability
- Check file ID spelling (case-sensitive)
- Ensure file upload completed successfully

**No completions shown**:
- Type `@` and wait for completion menu
- Check conversation has uploaded documents
- Verify terminal supports interactive input

### Debug Tips

```bash
# Check available files
/documents

# Test file reference parsing
python -c "
from src.forge_cli.chat.file_reference_parser import FileReferenceParser
print(FileReferenceParser.parse('@file_123 test'))
"
```

This file reference syntax makes it easy to have focused conversations about specific documents while maintaining the natural flow of chat interactions.
