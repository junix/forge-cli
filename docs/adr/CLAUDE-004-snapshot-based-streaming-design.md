# ADR-004: Snapshot-based Streaming Response Design

**Status**: Accepted  
**Date**: 2025-01-26  
**Decision Makers**: Development Team  

## Context

When implementing streaming responses in the Knowledge Forge SDK, a fundamental architectural decision was needed regarding how to transmit response data over the event stream. The two primary approaches are delta-based (incremental updates) and snapshot-based (complete state) streaming.

### Background

The Knowledge Forge Response API uses Server-Sent Events (SSE) to stream responses to clients. As the server processes a request (especially with file search and reasoning), it needs to send updates to the client about the current state of the response.

### Problem Statement

1. Clients need real-time updates about response progress
2. Responses can include complex nested structures (text, citations, reasoning, search results)
3. Network interruptions or missed events shouldn't corrupt the client state
4. The solution should be simple to implement and debug
5. Performance considerations for both bandwidth and processing

## Considered Options

### Option 1: Delta-based Streaming
Send only the changes between events.

**Example**:
```json
// Event 1
{"type": "text.delta", "text": "Based on"}
// Event 2
{"type": "text.delta", "text": " the documents"}
// Event 3
{"type": "annotation.added", "index": 0, "annotation": {...}}
```

**Pros**:
- Minimal bandwidth usage
- Fine-grained updates
- Similar to OpenAI's streaming approach

**Cons**:
- Complex state management on client
- Missed events can corrupt state
- Difficult to debug
- Requires careful ordering and sequencing
- Complex to handle nested structure updates

### Option 2: Snapshot-based Streaming
Send the complete response state with each event.

**Example**:
```json
// Event 1
{"output": [{"type": "message", "content": [{"type": "output_text", "text": "Based on"}]}]}
// Event 2
{"output": [{"type": "message", "content": [{"type": "output_text", "text": "Based on the documents"}]}]}
// Event 3
{"output": [{"type": "message", "content": [{"type": "output_text", "text": "Based on the documents", "annotations": [...]}}]}]}
```

**Pros**:
- Simple client implementation
- Resilient to missed events
- Easy to debug (each event is self-contained)
- No state synchronization issues
- Natural fit for complex nested structures

**Cons**:
- Higher bandwidth usage
- Redundant data transmission
- Potentially larger event payloads

### Option 3: Hybrid Approach
Use deltas for text content and snapshots for structural changes.

**Pros**:
- Balanced bandwidth usage
- Optimized for common cases

**Cons**:
- Most complex to implement
- Two different processing paths
- Inconsistent mental model

## Decision

We chose **Option 2: Snapshot-based Streaming** for the following reasons:

1. **Simplicity**: Client implementation is straightforward - just replace the current state with the new snapshot
2. **Reliability**: Missing an event doesn't corrupt the client state
3. **Debugging**: Each event is self-contained and can be examined independently
4. **Flexibility**: Easy to add new fields or change structure without breaking clients
5. **Consistency**: One processing model for all event types

## Implementation Details

### Event Structure
Each streaming event contains the complete response state:

```python
{
    "output": [
        {
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Complete text up to this point...",
                    "annotations": [
                        {
                            "type": "file_citation",
                            "file_id": "file_123",
                            "index": 0
                        }
                    ]
                }
            ]
        },
        {
            "type": "file_search_call",
            "status": "completed",
            "queries": ["search term"],
            "results": [...]
        }
    ],
    "usage": {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    }
}
```

### Current Implementation Pattern

```python
class StreamHandler:
    async def handle_stream(self, stream, initial_request: str) -> StreamState:
        """Handle streaming events using snapshot-based processing."""
        state = StreamState()
        
        async for event_type, event_data in stream:
            # Route to appropriate processor based on event type
            self.processor_registry.process(
                event_type, event_data, state, self.display
            )
            
            # Each processor handles complete snapshots
            # No complex state synchronization needed
        
        return state

class MessageProcessor(OutputProcessor):
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        """Process complete message snapshots."""
        # Extract full content from snapshot
        content = self._extract_complete_content(event_data)
        annotations = self._extract_all_annotations(event_data)
        # Process complete state, not deltas
```

### Display Strategy Integration

```python
# Each display handles snapshots according to its capabilities
class RichDisplay(BaseDisplay):
    def handle_message_update(self, content: str, citations: List[Citation]):
        """Rich display processes complete snapshots for live updates."""
        # Update live panel with complete content
        self._update_response_panel(content)
        self._update_citation_table(citations)

class PlainDisplay(BaseDisplay):
    def handle_message_update(self, content: str, citations: List[Citation]):
        """Plain display can use deltas or snapshots."""
        # Can handle both incremental and complete updates
        print(content)

class JsonDisplay(BaseDisplay):
    def handle_message_update(self, content: str, citations: List[Citation]):
        """JSON accumulates complete state for final output."""
        self.state["text"] = content
        self.state["citations"] = [c.to_dict() for c in citations]
```

## Consequences

### Positive
- **Robust error handling**: Clients can recover from any missed events
- **Simple client code**: No complex state management or event ordering
- **Easy testing**: Each event can be tested in isolation
- **Natural progressive enhancement**: Rich clients can use snapshots, simple clients can use deltas
- **Straightforward debugging**: Can examine any event to see complete state

### Negative
- **Bandwidth overhead**: Typically 2-5x more data than delta approach
- **Processing overhead**: Client must parse complete state each time
- **Memory usage**: Both client and server need to maintain complete state

### Mitigation Strategies
1. Use compression (gzip) for SSE streams to reduce bandwidth
2. Implement client-side diffing for UI updates if needed
3. Provide delta events alongside snapshots for bandwidth-sensitive clients
4. Use efficient JSON serialization

## Performance Analysis

### Bandwidth Comparison
For a typical response generating 1000 tokens:
- Delta approach: ~50KB total
- Snapshot approach: ~200KB total
- With gzip compression: ~60KB (snapshot) vs ~40KB (delta)

### Processing Time
- Delta: O(n) for state reconstruction
- Snapshot: O(1) for state access, O(n) for parsing

## Migration Path

The design allows for future addition of delta events without breaking existing clients:
1. Snapshot events continue to work as-is
2. New delta events can be added with different event types
3. Clients can opt into delta processing when ready

## References

- Server-Sent Events (SSE) specification
- OpenAI Streaming API documentation
- React Server Components (similar snapshot approach)
- ADR-002-reasoning-event-handling.md
- ADR-003-file-search-annotation-display.md

## Related Code

- `src/forge_cli/stream/handler.py` - Main streaming handler implementation
- `src/forge_cli/processors/` - Event processor implementations using snapshots
- `src/forge_cli/display/` - Display strategies that handle snapshot updates
- `src/forge_cli/models/state.py` - State management for snapshot processing
- `src/forge_cli/sdk.py` - SDK streaming implementation with SSE