#!/usr/bin/env python3
"""Debug script to understand citation rendering issue."""

from unittest.mock import Mock
from src.forge_cli.display.v3.renderers.plaintext.message_content import PlaintextMessageContentRenderer
from src.forge_cli.display.v3.renderers.plaintext.citations import PlaintextCitationsRenderer
from src.forge_cli.display.v3.renderers.plaintext.styles import PlaintextStyles
from src.forge_cli.display.v3.renderers.plaintext.config import PlaintextDisplayConfig

def debug_citation_rendering():
    """Debug why citations aren't being rendered."""
    
    # Your example text with citation markers
    test_text = """北森控股有限公司（北森公司）在人工智能产品领域已形成多维度布局，主要聚焦于人力资源管理场景的智能化升级。根据其2024年中期报告，核心AI产品及应用包括：

1 AI员工助手
• 截至2024年9月30日，该产品已助力核心HCM业务实现28%的同比增长，累计服务客户近2,100家❶ 。

2 AI面试系统  
• 该系统已帮助招测一体化业务实现ARR占比21%，并通过智能化评估流程提升招聘效率❶ 。"""

    print("=== Testing Message Content Rendering ===")
    
    # Create mock content
    mock_content = Mock()
    mock_content.type = "output_text"
    mock_content.text = test_text
    mock_content.annotations = []  # Empty annotations for now
    
    # Create renderer with styles
    styles = PlaintextStyles()
    renderer = PlaintextMessageContentRenderer(styles)
    
    # Test the rendering
    result = renderer.with_content(mock_content).render()
    
    print("Message content rendered successfully:")
    if hasattr(result, 'markup'):
        print(result.markup[:200] + "...")
    print()
    
    print("=== Testing Citations Rendering ===")
    
    # Create mock response with citations
    mock_response = Mock()
    mock_item = Mock()
    mock_item.type = "message"  # Changed to match is_message_item check
    mock_item.content = [mock_content]
    mock_response.output = [mock_item]
    
    config = PlaintextDisplayConfig()
    config.show_citations = True
    
    # Test citation extraction
    citations = PlaintextCitationsRenderer._extract_citations(mock_response)
    print(f"Extracted {len(citations)} citations from response")
    
    # Test citation rendering
    citations_renderer = PlaintextCitationsRenderer(styles, config)
    citations_result = citations_renderer.with_citations(citations).render()
    
    if citations_result:
        print("Citations rendered:")
        print(str(citations_result))
    else:
        print("No citations rendered (empty result)")
    
    print()
    print("=== Testing with Mock Citations ===")
    
    # Create mock citations to test rendering format
    mock_citation1 = Mock()
    mock_citation1.type = "file_citation"
    mock_citation1.filename = "北森2024年中期报告.pdf"
    mock_citation1.file_id = "file_abc123"
    mock_citation1.index = 5
    
    mock_citation2 = Mock()
    mock_citation2.type = "url_citation"
    mock_citation2.url = "https://beisen.com/reports"
    mock_citation2.title = "北森官方报告"
    
    mock_citations = [mock_citation1, mock_citation2]
    
    citations_renderer_mock = PlaintextCitationsRenderer(styles, config)
    mock_citations_result = citations_renderer_mock.with_citations(mock_citations).render()
    
    if mock_citations_result:
        print("Mock citations rendered successfully:")
        print(str(mock_citations_result))
    else:
        print("Mock citations failed to render")

if __name__ == "__main__":
    debug_citation_rendering() 