"""Demo script showcasing the modular tool renderer architecture."""

from forge_cli.display.v3.renderers.rich.tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)


def demo_file_reader_renderer():
    """Demonstrate FileReaderToolRender capabilities."""
    print("🔥 FileReaderToolRender Demo:")
    
    # Basic file reading
    result1 = (FileReaderToolRender()
              .with_filename("research_paper.pdf")
              .with_file_size(2048000)
              .with_progress(0.85)
              .render())
    print(f"  Basic: {result1}")
    
    # Document ID based
    result2 = (FileReaderToolRender()
              .with_doc_ids(["doc_abc123xyz"])
              .with_query("machine learning trends")
              .render())
    print(f"  Doc ID: {result2}")
    
    print()


def demo_web_search_renderer():
    """Demonstrate WebSearchToolRender capabilities."""
    print("🌐 WebSearchToolRender Demo:")
    
    # Single query
    result1 = (WebSearchToolRender()
              .with_queries(["latest Python tutorials"])
              .with_results_count(15)
              .render())
    print(f"  Single: {result1}")
    
    # Multiple queries
    result2 = (WebSearchToolRender()
              .with_queries(["React hooks", "Vue composition API", "Angular signals", "Svelte stores"])
              .render())
    print(f"  Multiple: {result2}")
    
    print()


def demo_file_search_renderer():
    """Demonstrate FileSearchToolRender capabilities."""
    print("🔍 FileSearchToolRender Demo:")
    
    result1 = (FileSearchToolRender()
              .with_queries(["error handling", "exception management"])
              .with_results_count(8)
              .render())
    print(f"  Search: {result1}")
    
    result2 = (FileSearchToolRender()
              .with_status("searching")
              .render())
    print(f"  Status: {result2}")
    
    print()


def demo_page_reader_renderer():
    """Demonstrate PageReaderToolRender capabilities."""
    print("📄 PageReaderToolRender Demo:")
    
    # Single page
    result1 = (PageReaderToolRender()
              .with_document_id("financial_report_2024")
              .with_page_range(5, 5)
              .with_progress(0.3)
              .render())
    print(f"  Single page: {result1}")
    
    # Page range
    result2 = (PageReaderToolRender()
              .with_document_id("technical_manual")
              .with_page_range(10, 25)
              .render())
    print(f"  Page range: {result2}")
    
    print()


def demo_code_interpreter_renderer():
    """Demonstrate CodeInterpreterToolRender capabilities."""
    print("💻 CodeInterpreterToolRender Demo:")
    
    # Python code
    python_code = """
import pandas as pd
import numpy as np

def analyze_data(df):
    return df.describe()

data = pd.read_csv('data.csv')
result = analyze_data(data)
print(result)
"""
    
    result1 = (CodeInterpreterToolRender()
              .with_code(python_code.strip())
              .with_output("DataFrame statistics output...")
              .render())
    print(f"  Python: {result1}")
    
    # JavaScript code
    js_code = "const users = await fetch('/api/users').then(r => r.json());"
    result2 = (CodeInterpreterToolRender()
              .with_code(js_code)
              .render())
    print(f"  JavaScript: {result2}")
    
    print()


def demo_function_call_renderer():
    """Demonstrate FunctionCallToolRender capabilities."""
    print("⚙️ FunctionCallToolRender Demo:")
    
    # Simple function
    result1 = (FunctionCallToolRender()
              .with_function("calculate_statistics")
              .with_arguments({"data": [1, 2, 3, 4, 5], "method": "mean"})
              .with_output("3.0")
              .render())
    print(f"  Simple: {result1}")
    
    # Complex function with many args
    result2 = (FunctionCallToolRender()
              .with_function("process_user_data")
              .with_arguments({
                  "user_id": 12345,
                  "name": "John Doe",
                  "email": "john@example.com",
                  "preferences": {"theme": "dark"},
                  "metadata": {"created": "2024-01-01"}
              })
              .render())
    print(f"  Complex: {result2}")
    
    print()


def demo_list_documents_renderer():
    """Demonstrate ListDocumentsToolRender capabilities."""
    print("📋 ListDocumentsToolRender Demo:")
    
    result1 = (ListDocumentsToolRender()
              .with_queries(["quarterly reports"])
              .with_document_count(12)
              .render())
    print(f"  Basic: {result1}")
    
    result2 = (ListDocumentsToolRender()
              .with_queries(["meeting notes", "project plans", "design docs"])
              .with_document_count(45)
              .render())
    print(f"  Multiple: {result2}")
    
    print()


def demo_builder_pattern():
    """Demonstrate the builder pattern flexibility."""
    print("🏗️ Builder Pattern Demo:")
    
    # Start with empty renderer
    renderer = FileReaderToolRender()
    print(f"  Empty: {renderer.render()}")
    
    # Add filename
    renderer.with_filename("config.json")
    print(f"  + Filename: {renderer.render()}")
    
    # Add file size
    renderer.with_file_size(1024)
    print(f"  + Size: {renderer.render()}")
    
    # Add progress
    renderer.with_progress(0.9)
    print(f"  + Progress: {renderer.render()}")
    
    print()


def main():
    """Run all demos."""
    print("=" * 60)
    print("🎨 MODULAR TOOL RENDERER ARCHITECTURE DEMO")
    print("=" * 60)
    print()
    
    demo_file_reader_renderer()
    demo_web_search_renderer()
    demo_file_search_renderer()
    demo_page_reader_renderer()
    demo_code_interpreter_renderer()
    demo_function_call_renderer()
    demo_list_documents_renderer()
    demo_builder_pattern()
    
    print("=" * 60)
    print("✅ All renderers demonstrated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main() 