#!/usr/bin/env python3
"""Demonstration of FileReaderToolRender usage patterns."""

from forge_cli.display.v3.renderers.rich import FileReaderToolRender
from forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader


def demo_basic_usage():
    """Demonstrate basic FileReaderToolRender usage."""
    print("=== Basic FileReaderToolRender Usage ===")
    
    # Example 1: Simple filename display
    renderer1 = FileReaderToolRender()
    result1 = renderer1.with_filename("research_paper.pdf").render()
    print(f"1. Basic filename: {result1}")
    
    # Example 2: Document ID fallback
    renderer2 = FileReaderToolRender()
    result2 = renderer2.with_doc_ids(["doc_abc123456789"]).render()
    print(f"2. Document ID: {result2}")
    
    # Example 3: Progress indicator
    renderer3 = FileReaderToolRender()
    result3 = renderer3.with_filename("report.xlsx").with_progress(0.75).render()
    print(f"3. With progress: {result3}")
    print()


def demo_method_chaining():
    """Demonstrate method chaining capabilities."""
    print("=== Method Chaining Examples ===")
    
    # Example 1: Full feature chain
    renderer1 = FileReaderToolRender()
    result1 = (renderer1
              .with_filename("financial_report_2024.pdf")
              .with_progress(0.85)
              .with_query("What are the key revenue trends?")
              .with_file_size(2 * 1024 * 1024)  # 2MB
              .render())
    print(f"1. Full chain: {result1}")
    
    # Example 2: Alternative properties
    renderer2 = FileReaderToolRender()
    result2 = (renderer2
              .with_doc_ids(["document_xyz_789"])
              .with_file_type("application/pdf")
              .with_page_count(45)
              .with_status("completed")
              .render())
    print(f"2. Alternative props: {result2}")
    
    # Example 3: Minimal chain
    renderer3 = FileReaderToolRender()
    result3 = (renderer3
              .with_filename("notes.txt")
              .with_query("Find action items")
              .render())
    print(f"3. Minimal chain: {result3}")
    print()


def demo_different_file_types():
    """Demonstrate rendering for different file types."""
    print("=== Different File Types ===")
    
    file_examples = [
        ("presentation.pptx", "10MB", "application/vnd.ms-powerpoint"),
        ("data.csv", "156KB", "text/csv"),
        ("README.md", "4KB", "text/markdown"),
        ("image.png", "892KB", "image/png"),
        ("code.py", "12KB", "text/x-python"),
    ]
    
    for filename, size_str, mime_type in file_examples:
        # Convert size string to bytes (simplified)
        if "MB" in size_str:
            size_bytes = int(size_str.replace("MB", "")) * 1024 * 1024
        elif "KB" in size_str:
            size_bytes = int(size_str.replace("KB", "")) * 1024
        else:
            size_bytes = int(size_str.replace("B", ""))
        
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename(filename)
                 .with_file_size(size_bytes)
                 .with_file_type(mime_type)
                 .render())
        print(f"   {filename:20} → {result}")
    print()


def demo_progress_states():
    """Demonstrate different progress states."""
    print("=== Progress States ===")
    
    filename = "large_document.pdf"
    progress_states = [
        (0.0, "just started"),
        (0.25, "quarter done"),
        (0.5, "halfway"),
        (0.75, "almost done"),
        (1.0, "completed"),
    ]
    
    for progress, description in progress_states:
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename(filename)
                 .with_progress(progress)
                 .render())
        print(f"   {description:12} ({int(progress*100):3}%): {result}")
    print()


def demo_query_handling():
    """Demonstrate query text handling and truncation."""
    print("=== Query Handling ===")
    
    queries = [
        "Simple query",
        "What are the main findings in this research?",
        "Can you provide a detailed analysis of the financial performance indicators shown in the quarterly report including revenue growth, profit margins, and cash flow trends?",
    ]
    
    for i, query in enumerate(queries, 1):
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename("document.pdf")
                 .with_query(query)
                 .render())
        print(f"   Query {i}: {result}")
    print()


def demo_from_tool_item():
    """Demonstrate the from_tool_item class method."""
    print("=== from_tool_item Method ===")
    
    # Example 1: With filename attribute
    print("1. Tool item with filename:")
    class MockToolWithFilename:
        def __init__(self):
            self.doc_ids = ["doc_123"]
            self.query = "Analyze the content"
            
    tool1 = MockToolWithFilename()
    setattr(tool1, "file_name", "analysis_report.docx")
    setattr(tool1, "progress", 0.6)
    
    result1 = FileReaderToolRender.from_tool_item(tool1)
    print(f"   Result: {result1}")
    
    # Example 2: With doc IDs only
    print("2. Tool item with doc IDs only:")
    class MockToolWithDocIds:
        def __init__(self):
            self.doc_ids = ["document_id_987654321"]
            self.query = "Extract key points"
            
    tool2 = MockToolWithDocIds()
    setattr(tool2, "progress", 0.3)
    
    result2 = FileReaderToolRender.from_tool_item(tool2)
    print(f"   Result: {result2}")
    
    # Example 3: Real ResponseFunctionFileReader
    print("3. Real ResponseFunctionFileReader model:")
    tool3 = ResponseFunctionFileReader(
        id="reader_001",
        type="file_reader_call", 
        status="in_progress",
        doc_ids=["pdf_document_456"],
        query="Summarize the executive summary section",
        progress=0.9
    )
    
    result3 = FileReaderToolRender.from_tool_item(tool3)
    print(f"   Result: {result3}")
    print()


def demo_edge_cases():
    """Demonstrate edge cases and error handling."""
    print("=== Edge Cases ===")
    
    # Empty renderer
    print("1. Empty renderer:")
    empty_renderer = FileReaderToolRender()
    result1 = empty_renderer.render()
    print(f"   Result: {result1}")
    
    # None values
    print("2. None values:")
    none_renderer = FileReaderToolRender()
    result2 = (none_renderer
              .with_filename(None)
              .with_progress(None)
              .with_query("")
              .render())
    print(f"   Result: {result2}")
    
    # Very long filename
    print("3. Very long filename:")
    long_renderer = FileReaderToolRender()
    very_long_name = "a" * 50 + "_document.pdf"
    result3 = long_renderer.with_filename(very_long_name).render()
    print(f"   Result: {result3}")
    
    # File without extension
    print("4. File without extension:")
    no_ext_renderer = FileReaderToolRender()
    result4 = no_ext_renderer.with_filename("README").render()
    print(f"   Result: {result4}")
    print()


def demo_real_world_scenarios():
    """Demonstrate real-world usage scenarios."""
    print("=== Real-World Scenarios ===")
    
    scenarios = [
        {
            "name": "Academic Paper Analysis",
            "filename": "quantum_computing_research.pdf",
            "query": "What are the key contributions to quantum algorithm development?",
            "progress": 0.4,
            "size": 3 * 1024 * 1024,  # 3MB
            "pages": 28
        },
        {
            "name": "Financial Report Review",
            "filename": "Q4_2024_earnings.xlsx",
            "query": "Extract revenue and profit margin trends",
            "progress": 0.8,
            "size": 512 * 1024,  # 512KB
            "pages": None
        },
        {
            "name": "Legal Document Processing",
            "filename": "contract_terms_and_conditions.docx",
            "query": "Identify liability and termination clauses",
            "progress": 0.2,
            "size": 1024 * 1024,  # 1MB
            "pages": 15
        },
    ]
    
    for scenario in scenarios:
        print(f"   {scenario['name']}:")
        renderer = FileReaderToolRender()
        chain = (renderer
                .with_filename(scenario['filename'])
                .with_query(scenario['query'])
                .with_progress(scenario['progress'])
                .with_file_size(scenario['size']))
        
        if scenario['pages']:
            chain = chain.with_page_count(scenario['pages'])
            
        result = chain.render()
        print(f"     {result}")
    print()


if __name__ == "__main__":
    print("🔧 FileReaderToolRender Demonstration")
    print("=" * 50)
    print()
    
    demo_basic_usage()
    demo_method_chaining()
    demo_different_file_types()
    demo_progress_states()
    demo_query_handling()
    demo_from_tool_item()
    demo_edge_cases()
    demo_real_world_scenarios()
    
    print("=== Summary ===")
    print("FileReaderToolRender provides a fluent interface for rendering file reader tools:")
    print()
    print("🔧 Core Methods:")
    print("  • with_filename(filename)     - Add filename with extension formatting")
    print("  • with_doc_ids(doc_ids)       - Add document ID display")
    print("  • with_progress(progress)     - Add progress percentage (0.0-1.0)")
    print("  • with_status(status)         - Add status information")
    print("  • with_query(query)           - Add query text with truncation")
    print("  • with_execution_trace(trace) - Add execution trace (for trace blocks)")
    print()
    print("🔧 Extended Methods:")
    print("  • with_file_size(size)        - Add file size in bytes (auto-formatted)")
    print("  • with_file_type(mime_type)   - Add file/MIME type")
    print("  • with_page_count(count)      - Add page count for documents")
    print()
    print("🔧 Class Methods:")
    print("  • from_tool_item(tool_item)   - Create render from tool item (matches existing style)")
    print()
    print("✅ All methods support chaining for complex rendering!")
    print("✅ Maintains consistency with existing Rich renderer styling!")
    print("✅ Handles edge cases and provides fallbacks gracefully!") 