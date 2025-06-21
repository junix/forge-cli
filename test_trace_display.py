#!/usr/bin/env python3
"""Test script to demonstrate the new clean tool display format."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from forge_cli.display.v3.renderers.plaintext.tools.file_search import PlaintextFileSearchToolRender
from forge_cli.display.v3.renderers.plaintext.tools.file_reader import PlaintextFileReaderToolRender
from forge_cli.display.v3.renderers.plaintext.config import PlaintextDisplayConfig
from forge_cli.display.v3.renderers.plaintext.styles import PlaintextStyles

class MockToolItem:
    """Mock tool item for testing."""
    def __init__(self, tool_type: str, tool_id: str, status: str = "in_progress", **kwargs):
        self.type = tool_type
        self.id = tool_id
        self.status = status
        for key, value in kwargs.items():
            setattr(self, key, value)

def test_old_vs_new_format():
    """Compare old ugly format with new clean format."""
    print("=== Tool Display Format Comparison ===\n")
    
    # Create mock objects
    config = PlaintextDisplayConfig()
    styles = PlaintextStyles()
    
    # Test File Search Tool
    print("🔍 FILE SEARCH TOOL:")
    print("OLD UGLY: [FILE_SEARCH_CALL] call_58b32ba49c934bdd8fb551 - in_progress")
    
    mock_search_tool = MockToolItem(
        "file_search_call", 
        "call_58b32ba49c934bdd8fb551", 
        "in_progress",
        queries=["machine learning algorithms", "neural networks"]
    )
    
    search_renderer = PlaintextFileSearchToolRender.from_tool_item(mock_search_tool, styles, config)
    new_format = search_renderer.render()
    print(f"NEW CLEAN: {new_format}")
    print()
    
    # Test File Reader Tool
    print("📖 FILE READER TOOL:")
    print("OLD UGLY: [FILE_READER_CALL] call_abc123def456789 - completed")
    
    mock_reader_tool = MockToolItem(
        "file_reader_call",
        "call_abc123def456789",
        "completed", 
        file_name="research_paper.pdf",
        doc_ids=["doc_12345"]
    )
    
    reader_renderer = PlaintextFileReaderToolRender.from_tool_item(mock_reader_tool, styles, config)
    new_format = reader_renderer.render()
    print(f"NEW CLEAN: {new_format}")
    print()
    
    # Test with execution trace
    print("📖 FILE READER WITH TRACE:")
    mock_reader_with_trace = MockToolItem(
        "file_reader_call",
        "call_trace_example",
        "in_progress",
        file_name="document.pdf",
        progress=0.75,
        execution_trace="[2024-01-15 10:30:45] STEP_1] Extracting text from PDF pages\n[2024-01-15 10:30:46] STEP_2] Processing document content successfully"
    )
    
    trace_renderer = PlaintextFileReaderToolRender.from_tool_item(mock_reader_with_trace, styles, config)
    new_format = trace_renderer.render()
    print(f"NEW CLEAN: {new_format}")
    print()
    
    print("✅ The new format is much cleaner with:")
    print("  • Beautiful icons instead of ugly brackets")
    print("  • Clean status indicators")
    print("  • Properly formatted queries using pack_queries")
    print("  • Concise tool names")
    print("  • Better visual hierarchy")

if __name__ == "__main__":
    test_old_vs_new_format()
