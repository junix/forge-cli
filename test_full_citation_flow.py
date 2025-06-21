#!/usr/bin/env python3
"""Test complete citation flow with proper annotations."""

from unittest.mock import Mock
from src.forge_cli.display.v3.renderers.plaintext.message_content import PlaintextMessageContentRenderer
from src.forge_cli.display.v3.renderers.plaintext.citations import PlaintextCitationsRenderer
from src.forge_cli.display.v3.renderers.plaintext.styles import PlaintextStyles
from src.forge_cli.display.v3.renderers.plaintext.config import PlaintextDisplayConfig

def test_complete_citation_flow():
    """Test complete citation flow with proper annotations."""
    
    print("=== Complete Citation Flow Test ===")
    
    # Text with long-style citation markers (what the AI would generate)
    original_text = """北森控股有限公司在人工智能领域的核心产品包括：

1. AI员工助手：截至2024年9月30日，该产品已助力核心HCM业务实现28%的同比增长⟦⟦1⟧⟧。

2. AI面试系统：该系统已帮助招测一体化业务实现ARR占比21%⟦⟦1⟧⟧。

3. AI学习云平台：该平台实现ARR同比增长60%⟦⟦2⟧⟧。"""

    # Create mock annotations (what would come from the AI response)
    mock_annotation1 = Mock()
    mock_annotation1.type = "file_citation"
    mock_annotation1.filename = "北森2024年中期报告.pdf"
    mock_annotation1.file_id = "file_abc123"
    mock_annotation1.index = 15  # Page number
    
    mock_annotation2 = Mock()
    mock_annotation2.type = "url_citation"
    mock_annotation2.url = "https://beisen.com/annual-report"
    mock_annotation2.title = "北森年度业务报告"
    
    # Create mock content with annotations
    mock_content = Mock()
    mock_content.type = "output_text"
    mock_content.text = original_text
    mock_content.annotations = [mock_annotation1, mock_annotation2]
    
    # Create mock response
    mock_item = Mock()
    mock_item.type = "message"
    mock_item.content = [mock_content]
    
    mock_response = Mock()
    mock_response.output = [mock_item]
    
    # Setup renderers
    styles = PlaintextStyles()
    config = PlaintextDisplayConfig()
    config.show_citations = True
    
    print("1. Original text with long-style markers:")
    print(original_text[:200] + "...\n")
    
    print("2. Message content after conversion:")
    message_renderer = PlaintextMessageContentRenderer(styles)
    message_result = message_renderer.with_content(mock_content).render()
    if hasattr(message_result, 'markup'):
        converted_text = message_result.markup
        print(converted_text[:300] + "...\n")
    
    print("3. Citations extraction:")
    citations = PlaintextCitationsRenderer._extract_citations(mock_response)
    print(f"Extracted {len(citations)} citations\n")
    
    print("4. Citations rendering:")
    citations_renderer = PlaintextCitationsRenderer(styles, config)
    citations_result = citations_renderer.with_citations(citations).render()
    
    if citations_result:
        print("Citations section:")
        print(str(citations_result))
    else:
        print("No citations rendered\n")
    
    print("=== Full Display Simulation ===")
    print("This is how it should appear in the terminal:")
    print("=" * 60)
    if hasattr(message_result, 'markup'):
        print(message_result.markup)
    print()
    if citations_result:
        print(str(citations_result))
    print("=" * 60)

if __name__ == "__main__":
    test_complete_citation_flow() 