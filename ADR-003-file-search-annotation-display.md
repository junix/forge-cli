# ADR-003: File Search Annotation Display Architecture

**Status**: Accepted  
**Date**: 2025-01-26  
**Decision Makers**: Development Team  

## Context

The hello-file-search.py script needed to properly display file citations/annotations from the Knowledge Forge API response. The OpenAI-style Response API returns annotations with file search results, but the original implementation wasn't displaying these citations, making it difficult for users to verify the source of information.

A key architectural insight is that the streaming response events are **complete snapshots**, not deltas. Each event contains the full response state up to that point, which simplifies citation processing since we can extract all annotations from any single event without maintaining complex state.

### Problem Statement

1. File search responses contain valuable citation information that wasn't being displayed
2. Citations need to be shown in a user-friendly format with proper referencing
3. The server-side model lacks filename information, requiring client-side workarounds
4. Different display modes (Rich, color, plain) need consistent citation formatting
5. Snapshot-based streaming requires different handling than delta-based approaches

## Considered Options

### Option 1: Inline Citation Display Only
- Show citations inline with the text using markers like [1], [2]
- No separate reference section
- **Pros**: Simple, minimal screen space
- **Cons**: Users can't see source details without looking elsewhere

### Option 2: Footnote-Style References
- Show citation markers inline and list references at the bottom
- Display as a simple list
- **Pros**: Familiar academic style, clear separation
- **Cons**: Less structured for multiple attributes

### Option 3: Tabular Reference Display
- Show citation markers inline and display references in a markdown table
- Include columns for citation number, document name, page, and file ID
- **Pros**: Structured, easy to scan, professional appearance
- **Cons**: Takes more vertical space

## Decision

We chose **Option 3: Tabular Reference Display** with the following implementation details:

1. **Citation Processing** (Snapshot-based):
   - Extract annotations from each complete response snapshot
   - Each streaming event contains the full response state, not deltas
   - Convert 0-based page indices to 1-based for human readability
   - Build file ID to filename mapping from search results
   - Use array position to determine citation number

2. **Display Format**:
   - Inline citation markers: [1], [2], etc. within the text
   - Reference table with columns: Citation | Document | Page | File ID
   - Full file IDs displayed without truncation
   - Markdown table format for Rich display mode

3. **Architecture**:
   - Modular `FileSearchEventHandler` class for event processing
   - `process_snapshot_with_annotations()` function processes complete snapshots
   - `format_annotated_display()` function for unified display formatting
   - Text delta events are ignored in Rich mode since snapshots contain full content
   - Support for Rich, color, and plain text modes

## Consequences

### Positive
- Users can easily verify information sources
- Professional, academic-style citation display
- Consistent formatting across different display modes
- Modular architecture allows easy maintenance and extension
- Full file IDs enable precise source identification

### Negative
- Takes more vertical screen space than simple lists
- Requires client-side workaround for missing filename information
- Table format might not render well on very narrow terminals

### Technical Debt
- Client-side file ID to filename mapping is a workaround for server limitation
- Should be removed when server-side model includes filename in annotations

## Implementation Notes

### Snapshot-based Processing
```python
def process_snapshot_with_annotations(event_data: Dict[str, Any], ...):
    """
    Process a complete snapshot response with annotations.
    Since each event is a full snapshot, we can process it completely.
    """
    # Extract full text and all annotations from the snapshot
    # No need to maintain state between events
```

### Key Data Structures
```python
# Citation structure
citation = {
    'number': i + 1,  # 1-based citation number
    'page': page_index,  # Converted from 0-based to 1-based
    'filename': filename,  # From file_id mapping or annotation
    'file_id': file_id  # Full ID, not truncated
}

# Markdown table format
| Citation | Document | Page | File ID |
|----------|----------|------|---------|
| [1] | document.pdf | 5 | file_abc123def456... |
```

### Event Handling
```python
# Skip text delta events in Rich mode since we're using snapshots
if event_type == "response.output_text.delta" and use_rich:
    # In Rich mode, we handle everything through snapshots
    pass
```

## References

- OpenAI Response API documentation
- Knowledge Forge file search implementation
- ADR-001-commandline-design.md
- ADR-002-reasoning-event-handling.md

## Related Components

- `/commands/hello-file-search.py` - Main implementation
- `/knowledge_forge/response/_types/response_output_text.py` - Server-side annotation model
- `/knowledge_forge/service/response_service/low_effort.py` - Server-side citation processing