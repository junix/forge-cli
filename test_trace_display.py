#!/usr/bin/env python3
"""Test script to demonstrate the new clean tool display format."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from forge_cli.display.v3.renderers.plaintext.tools.file_search import PlaintextFileSearchToolRender
from forge_cli.display.v3.renderers.plaintext.tools.file_reader import PlaintextFileReaderToolRender
from forge_cli.display.v3.renderers.plaintext.tools.web_search import PlaintextWebSearchToolRender
from forge_cli.display.v3.renderers.plaintext.tools.function_call import PlaintextFunctionCallToolRender
from forge_cli.display.v3.renderers.plaintext.tools.list_documents import PlaintextListDocumentsToolRender
from forge_cli.display.v3.renderers.plaintext.tools.page_reader import PlaintextPageReaderToolRender
from forge_cli.display.v3.renderers.plaintext.tools.code_interpreter import PlaintextCodeInterpreterToolRender
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

def test_all_tool_renderers():
    """Test all tool renderers with the new clean format."""
    print("=== ALL TOOL RENDERERS - OLD vs NEW FORMAT ===\n")
    
    # Create mock objects
    config = PlaintextDisplayConfig()
    styles = PlaintextStyles()
    
    # 1. File Search Tool
    print("🔍 FILE SEARCH TOOL:")
    print("OLD UGLY: [FILE_SEARCH_CALL] call_58b32ba49c934bdd8fb551 - in_progress")
    mock_search_tool = MockToolItem("file_search_call", "call_search_123", "completed", 
                                   queries=["machine learning algorithms", "neural networks", "deep learning"])
    search_renderer = PlaintextFileSearchToolRender.from_tool_item(mock_search_tool, styles, config)
    print(f"NEW CLEAN: {search_renderer.render()}")
    print()
    
    # 2. File Reader Tool
    print("📖 FILE READER TOOL:")
    print("OLD UGLY: [FILE_READER_CALL] call_abc123def456789 - completed")
    mock_reader_tool = MockToolItem("file_reader_call", "call_reader_456", "completed", 
                                   file_name="research_paper.pdf", doc_ids=["doc_12345"])
    reader_renderer = PlaintextFileReaderToolRender.from_tool_item(mock_reader_tool, styles, config)
    print(f"NEW CLEAN: {reader_renderer.render()}")
    print()
    
    # 3. Web Search Tool
    print("🌐 WEB SEARCH TOOL:")
    print("OLD UGLY: [WEB_SEARCH_CALL] call_websearch789 - searching")
    mock_web_tool = MockToolItem("web_search_call", "call_web_789", "searching",
                                queries=["Python best practices", "FastAPI tutorial"], result_count=5)
    web_renderer = PlaintextWebSearchToolRender.from_tool_item(mock_web_tool, styles, config)
    print(f"NEW CLEAN: {web_renderer.render()}")
    print()
    
    # 4. Function Call Tool
    print("⚙️ FUNCTION CALL TOOL:")
    print("OLD UGLY: [FUNCTION_CALL] call_func_abc123 - completed")
    mock_func_tool = MockToolItem("function_call", "call_func_abc", "completed",
                                 name="calculate_metrics", call_id="call_abc123def456789",
                                 arguments={"data": [1, 2, 3], "method": "average"})
    func_renderer = PlaintextFunctionCallToolRender.from_tool_item(mock_func_tool, styles, config)
    print(f"NEW CLEAN: {func_renderer.render()}")
    print()
    
    # 5. List Documents Tool
    print("📋 LIST DOCUMENTS TOOL:")
    print("OLD UGLY: [LIST_DOCUMENTS_CALL] call_list_def456 - completed")
    mock_list_tool = MockToolItem("list_documents_call", "call_list_def", "completed",
                                 queries=["financial reports", "Q4 earnings"])
    list_renderer = PlaintextListDocumentsToolRender.from_tool_item(mock_list_tool, styles, config)
    print(f"NEW CLEAN: {list_renderer.render()}")
    print()
    
    # 6. Page Reader Tool
    print("📄 PAGE READER TOOL:")
    print("OLD UGLY: [PAGE_READER_CALL] call_page_ghi789 - in_progress")
    mock_page_tool = MockToolItem("page_reader_call", "call_page_ghi", "in_progress",
                                 document_id="doc_financial_report_2024", start_page=5, end_page=10, progress=0.6)
    page_renderer = PlaintextPageReaderToolRender.from_tool_item(mock_page_tool, styles, config)
    print(f"NEW CLEAN: {page_renderer.render()}")
    print()
    
    # 7. Code Interpreter Tool
    print("💻 CODE INTERPRETER TOOL:")
    print("OLD UGLY: [CODE_INTERPRETER_CALL] call_code_jkl012 - interpreting")
    mock_code_tool = MockToolItem("code_interpreter_call", "call_code_jkl", "interpreting",
                                 language="python", code="import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())")
    code_renderer = PlaintextCodeInterpreterToolRender.from_tool_item(mock_code_tool, styles, config)
    print(f"NEW CLEAN: {code_renderer.render()}")
    print()
    
    print("✅ ALL TOOLS NOW USE THE CLEAN FORMAT WITH:")
    print("  • Beautiful icons instead of ugly [BRACKETS]")
    print("  • Clean status indicators with visual icons")
    print("  • Properly formatted content using pack_queries where applicable")
    print("  • Concise tool names (File Search vs FILE_SEARCH_CALL)")
    print("  • Better visual hierarchy with • separators")
    print("  • Consistent styling across all tool types")
    print("  • Smart truncation of long content")
    print("  • Progress indicators and trace previews when available")

if __name__ == "__main__":
    test_all_tool_renderers()
