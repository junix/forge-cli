# ADR-005: File Q&A via @ Symbol Syntax

## Status
Accepted

## Context

Users frequently need to ask questions about specific documents in their vector stores or uploaded files. The current workflow requires either:
1. Using vector search tools that may return irrelevant results
2. Manually specifying file IDs in complex command syntax
3. Relying on the AI to search through all available documents

This creates friction in the user experience and makes it difficult to have focused conversations about specific documents. Users expressed a need for a more intuitive way to reference and question specific files directly.

## Decision

We will implement a **@ symbol syntax** for direct file referencing in chat messages, similar to social media mentions or Slack's @ mentions. This allows users to directly reference specific files and ask questions about them.

### Syntax Design
- **Format**: `@<file_id> <question>`
- **Examples**:
  - `@file_123 What are the main conclusions?`
  - `Compare @doc_abc and @doc_xyz for similarities`
  - `Based on @report_2024, what are the trends?`

### Technical Implementation
1. **File Reference Parser**: Regex-based parsing of `@file_id` patterns
2. **Auto-Completion**: Real-time file ID completion with metadata display
3. **API Integration**: Automatic conversion to `input_file` + `input_text` format
4. **Conversation State**: Enhanced request creation with file context

## Consequences

### Positive
- **Intuitive UX**: Familiar @ mention pattern from social platforms
- **Direct File Access**: No ambiguity about which files to reference
- **Auto-Completion**: Discoverable file IDs with rich metadata
- **Multi-File Support**: Can reference multiple files in one message
- **Type Safety**: Uses structured API format with proper validation
- **Conversation Flow**: Natural integration with existing chat interface

### Negative
- **File ID Complexity**: Users need to know or discover file IDs
- **Vector Store Dependency**: Requires working vector store integration
- **Completion Performance**: May be slow with large file collections
- **Cache Management**: Needs file list synchronization and refresh
- **Error Handling**: Complex failure modes (invalid IDs, inaccessible files)

### Neutral
- **Learning Curve**: Users need to learn the @ syntax
- **Implementation Complexity**: Multiple components need coordination
- **Maintenance Overhead**: File cache and completion system upkeep

## Implementation Details

### Architecture Components

```
User Input: "@file_123 What is this about?"
     ↓
FileReferenceParser.parse()
     ↓
create_file_input_message()
     ↓
ConversationState.new_request()
     ↓
API Request: {
  "input": [{
    "role": "user",
    "content": [
      {"type": "input_file", "file_id": "file_123"},
      {"type": "input_text", "text": "What is this about?"}
    ]
  }]
}
```

### Key Files
- `src/forge_cli/chat/file_reference_parser.py` - Core parsing logic
- `src/forge_cli/chat/command_completer.py` - Auto-completion system
- `src/forge_cli/models/conversation.py` - Request generation
- `src/forge_cli/chat/inputs.py` - Input handler integration

### Auto-Completion System
- **Trigger**: Typing `@` character
- **Data Source**: Vector stores + uploaded documents
- **Display**: File ID + filename with metadata
- **Filtering**: Real-time matching on ID and filename
- **Caching**: File list cached for performance

### API Request Format
Messages with file references are converted to structured input:
- `input_file` entries for each referenced file
- `input_text` entry for the cleaned question text
- Maintains conversation history and context

## Alternatives Considered

### 1. Command-Based Approach
```bash
/ask-file file_123 "What is this about?"
```
**Rejected**: Less natural, requires command syntax knowledge

### 2. Filename-Based References
```bash
@"document.pdf" What is this about?
```
**Rejected**: Filename conflicts, special character handling complexity

### 3. Collection-Based Queries
```bash
/query collection_name "question about documents"
```
**Rejected**: Less precise, doesn't allow specific file targeting

### 4. GUI File Picker
**Rejected**: Breaks chat flow, not suitable for CLI interface

## Migration Strategy

### Phase 1: Core Implementation ✅
- File reference parser
- Basic auto-completion
- API request generation
- Conversation state integration

### Phase 2: Vector Store Integration (In Progress)
- Real-time file list fetching
- Cache management
- Error handling for inaccessible files

### Phase 3: Enhanced Features (Future)
- Fuzzy file matching
- File metadata in completion
- Recent files prioritization
- Batch file operations

## Monitoring and Success Metrics

### Technical Metrics
- Auto-completion response time < 500ms
- File reference parsing accuracy > 99%
- Vector store query success rate > 95%
- Cache hit rate > 80%

### User Experience Metrics
- @ syntax adoption rate
- File reference usage frequency
- User error rates with invalid file IDs
- Support ticket reduction for file-related queries

### Performance Benchmarks
- File list cache refresh time
- Completion menu rendering speed
- Memory usage with large file collections
- Network requests for file metadata

## Risks and Mitigations

### Risk: Vector Store API Failures
**Mitigation**: Graceful degradation with cached file lists, clear error messages

### Risk: File ID Discoverability
**Mitigation**: Rich auto-completion, `/show-documents` command integration

### Risk: Performance with Large File Collections
**Mitigation**: Pagination, lazy loading, intelligent caching

### Risk: User Confusion with Syntax
**Mitigation**: Clear documentation, helpful error messages, examples in help

## Future Considerations

### Potential Enhancements
- **File Aliases**: `@"my-report" -> file_123`
- **Folder References**: `@folder/subfolder/` for multiple files
- **File Type Filtering**: `@*.pdf` for all PDF files
- **Recent Files**: `@recent` for recently accessed files
- **Shared References**: `@shared:file_123` for team files

### Integration Opportunities
- **Command Combination**: `@file_123 /summarize`
- **Batch Processing**: `@file_* analyze all`
- **Export Features**: `@file_123 /export-summary`
- **Collaboration**: Share file references between users

## Conclusion

The @ symbol syntax provides an intuitive and powerful way for users to directly reference and question specific files. While it introduces some complexity in implementation and user learning, the benefits of direct file access and natural conversation flow outweigh the costs.

The implementation follows established patterns from social media and collaboration tools, making it familiar to users. The technical architecture is extensible and allows for future enhancements while maintaining backward compatibility.

This feature significantly improves the user experience for document-focused conversations and reduces the friction in accessing specific file content within the chat interface.
