# Reasoning/Thinking Events in Knowledge Forge Streaming

## Overview

This document describes how to handle and display reasoning/thinking events in the Knowledge Forge streaming API. These events allow you to show the AI's thinking process in real-time, providing transparency into how the AI arrives at its conclusions.

## Event Types

### Reasoning Events

The Knowledge Forge API supports two different formats for reasoning events:

#### Format 1: Output Item Events (Primary)
1. **`response.output_item.added`**
   - When `item.type == "reasoning"`
   - Contains `summary` array with reasoning text
   - Structure: `{item: {type: "reasoning", summary: [{type: "summary_text", text: "..."}]}}`

2. **`response.output_item.done`**
   - When `item.type == "reasoning"`
   - Indicates reasoning item is complete

#### Format 2: Reasoning Summary Events (Alternative)
1. **`response.reasoning_summary_text.delta`**
   - Contains incremental reasoning text
   - Field: `delta` - the text fragment
   - Streamed character by character or in small chunks

2. **`response.reasoning_summary_text.done`**
   - Indicates reasoning phase is complete
   - Marks transition to response generation

3. **`response.reasoning_summary_part.added`**
   - New reasoning section started
   - Contains metadata about the reasoning part

4. **`response.reasoning_summary_part.done`**
   - Reasoning section completed

## Implementation in hello-file-search.py

The updated `hello-file-search.py` now properly handles reasoning events:

### Key Changes

1. **Track Reasoning State**
   ```python
   reasoning_text = ""  # Accumulate reasoning text
   in_reasoning = False  # Track if currently in reasoning mode
   ```

2. **Handle Reasoning Delta Events**
   ```python
   elif event_type == "response.reasoning_summary_text.delta" and event_data:
       if "delta" in event_data:
           reasoning_fragment = event_data["delta"]
           reasoning_text += reasoning_fragment
           # Display reasoning in yellow
   ```

3. **Rich Display Support**
   - Shows both reasoning and response in a unified panel
   - Reasoning displayed in yellow/dim style
   - Response in normal style

4. **Terminal Display**
   - Shows "🤔 Thinking:" prefix
   - Reasoning text in yellow (if colors enabled)
   - Clear transition to response phase

## Usage Examples

### Basic Usage
```bash
# Run with default settings
python -m commands.hello-file-search -q "Complex question requiring reasoning"

# Enable debug to see all events
python -m commands.hello-file-search -q "Analyze this document" --debug

# Use higher effort levels for more reasoning
python -m commands.hello-file-search -q "Compare these concepts" --effort high
```

### Testing Reasoning Events
```bash
# Use the test script to verify reasoning events
python -m commands.test-reasoning-stream --model qwen-max-latest --effort medium
```

## Display Modes

### With Rich Library
- Unified panel showing both thinking and response
- Real-time updates as text streams
- Clear visual separation between phases

### Without Rich (Terminal)
- Inline display with prefixes
- Color coding if terminal supports it
- Clear phase transitions

### JSON Output Mode
- Reasoning events are suppressed in JSON mode
- Only final response is output as JSON

## Model and Effort Level Considerations

1. **Model Support**
   - Not all models support reasoning events
   - DeepSeek R1 and similar models emit reasoning
   - Standard models may not have reasoning phase

2. **Effort Levels**
   - `low`: Minimal or no reasoning events
   - `medium`: Moderate reasoning for complex queries
   - `high`: Extensive reasoning and analysis
   - `dev`: Development-focused mode with enhanced debugging and detailed logging

3. **Query Complexity**
   - Simple queries may not trigger reasoning
   - Complex analytical questions more likely to show reasoning
   - Multi-step problems benefit from visible reasoning

## Troubleshooting

### No Reasoning Events Shown

1. **Use the Debug Event Logger**
   ```bash
   python -m commands.debug-event-logger -q "Your question" --effort medium
   ```
   This will show all events being fired and help identify the reasoning format

2. **Check Model Support**
   - Verify the model supports reasoning output
   - Try with known reasoning models (e.g., models with thinking capabilities)

3. **Increase Effort Level**
   ```bash
   python -m commands.hello-file-search --effort medium
   python -m commands.hello-file-search --effort high
   python -m commands.hello-file-search --effort dev
   ```
   Higher effort levels are more likely to trigger reasoning. The `dev` effort level provides enhanced debugging output.

4. **Enable Debug Mode**
   ```bash
   python -m commands.hello-file-search --debug
   ```
   This shows all events received, including reasoning structure

5. **Check Event Format**
   - Reasoning may come through `response.output_item.added` events
   - Look for items with `type: "reasoning"`
   - The text is in `item.summary[].text`

6. **Server Configuration**
   - Ensure server is configured to stream reasoning events
   - Verify streaming is enabled in request
   - Check if the model version supports reasoning output

### Performance Considerations

- Reasoning events add to streaming time
- Can be disabled for faster responses
- Consider user experience vs transparency tradeoff

## Future Enhancements

1. **Configurable Display**
   - Option to hide/show reasoning
   - Reasoning-only mode
   - Save reasoning to separate file

2. **Enhanced Formatting**
   - Markdown rendering for reasoning
   - Step-by-step breakdown
   - Progress indicators

3. **Integration**
   - Reasoning replay functionality
   - Reasoning analysis tools
   - Export reasoning traces