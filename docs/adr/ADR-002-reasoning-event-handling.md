# ADR-002: Reasoning Event Handling in Command Line Tools

## Status
Accepted

## Context
When using the Forge CLI, reasoning/thinking tokens were being generated by the model but not displayed in the UI. This caused the command line to appear frozen while the model was thinking, providing a poor user experience.

Investigation revealed that reasoning events come through multiple event structures, requiring flexible handling in the processor architecture.

## Decision
We implement reasoning event handling through a modular processor architecture:

1. **Primary Format**: Handle `response.output_item.added` events where `item.type == "reasoning"`
   - Processed by `ReasoningProcessor` class
   - Extract text from both `item.summary[].text` and `item.summary[].summary_text` 
   - Support for multiple reasoning text formats

2. **Alternative Format**: Keep handlers for `response.reasoning_summary_text.delta` events
   - Provides backward compatibility for different API versions
   - Handled through the same processor interface

3. **Processor Architecture**: Utilize the registry pattern for event handling
   - `ProcessorRegistry` routes reasoning events to `ReasoningProcessor`
   - Flexible registration system allows easy extension
   - Consistent interface across all event types

## Implementation Details

### Event Structure (Primary Format)
```json
{
  "type": "response.output_item.added",
  "item": {
    "type": "reasoning",
    "id": "reason-xxx",
    "summary": [
      {
        "type": "summary_text",
        "text": "The thinking process text..."
      }
    ],
    "status": "in_progress"
  }
}
```

### Implementation Architecture
```python
# ReasoningProcessor handles reasoning events
class ReasoningProcessor(OutputProcessor):
    def process(self, event_data: dict, state: StreamState, display: BaseDisplay):
        # Extract reasoning content
        reasoning_text = self._extract_reasoning_text(event_data)
        
        # Update state
        state.set_reasoning(reasoning_text)
        
        # Update display
        display.handle_reasoning_update(reasoning_text)

# Registry routes events to appropriate processors
registry.register("reasoning", ReasoningProcessor())
```

### Display Strategy
- Rich Display: Live updating reasoning panel with spinner indicators
- Plain Display: Simple "🤔 Thinking:" prefix with text
- JSON Display: Structured reasoning data in output
- Support for multiple display modes through strategy pattern

## Consequences

### Positive
- **Better UX**: Users see thinking process in real-time
- **Transparency**: Clear visibility into AI reasoning
- **Flexibility**: Supports multiple event formats
- **Debugging**: Event logger helps diagnose issues

### Negative
- **Complexity**: Must handle multiple event formats
- **Maintenance**: Need to track API changes in event structure

## Lessons Learned

1. **Event Structure Varies**: Different models/APIs may use different event structures
2. **Debug First**: Create debugging tools before implementing features
3. **Flexible Handlers**: Design event handlers to accommodate multiple formats
4. **User Feedback**: Visual feedback during long operations is critical

## References
- Original issue: Reasoning tokens not displayed during streaming
- Debug output showing actual event structure
- Knowledge Forge Response API documentation