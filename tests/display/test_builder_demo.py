"""Demonstration of TextBuilder usage patterns."""

from forge_cli.display.v3.builder import TextBuilder


def demo_basic_usage():
    """Demonstrate basic TextBuilder usage."""
    print("=== Basic TextBuilder Usage ===")
    
    text = "Hello\nWorld\nFrom\nTextBuilder"
    
    # Example 1: Simple blockquote
    result1 = TextBuilder.from_text(text).with_block_quote().build()
    print("1. Blockquote:")
    print(result1)
    print()
    
    # Example 2: Sliding display
    result2 = TextBuilder.from_text(text).with_slide(max_lines=2, format_type="raw").build()
    print("2. Sliding display (last 2 lines):")
    print(result2)
    print()


def demo_method_chaining():
    """Demonstrate method chaining capabilities."""
    print("=== Method Chaining Examples ===")
    
    # Example execution trace
    trace_log = """[10:00:00] Starting file processing
[10:00:01] Loading document
[10:00:02] Parsing page 1 of 5
[10:00:03] Parsing page 2 of 5 
[10:00:04] Parsing page 3 of 5
[10:00:05] Parsing page 4 of 5
[10:00:06] Parsing page 5 of 5
[10:00:07] Parsing page 5 of 5
[10:00:08] Extracting text content
[10:00:09] Processing complete"""

    # Example 1: Last few lines as blockquote
    result1 = (TextBuilder.from_text(trace_log)
              .with_slide(max_lines=3, format_type="raw")
              .with_block_quote()
              .build())
    print("1. Last 3 lines as blockquote:")
    print(result1)
    print()
    
    # Example 2: Prefixed and suffixed
    result2 = (TextBuilder.from_text(trace_log)
              .with_slide(max_lines=2, format_type="raw")
              .with_prefix("🔄 ")
              .with_suffix(" ✓")
              .build())
    print("2. Last 2 lines with emoji decoration:")
    for line in result2:
        print(line)
    print()
    
    # Example 3: Complex chain with prefix then blockquote
    result3 = (TextBuilder.from_text(trace_log)
              .with_slide(max_lines=4, format_type="raw")
              .with_prefix("│ ")
              .with_block_quote()
              .build())
    print("3. Last 4 lines with prefix then blockquote:")
    print(result3)
    print()


def demo_real_world_scenarios():
    """Demonstrate real-world usage scenarios."""
    print("=== Real-World Scenarios ===")
    
    # AI Reasoning Display
    reasoning = """I need to analyze this document carefully.
First, I'll examine the overall structure and layout.
Then, I'll identify the key sections and headings.
Next, I'll extract the main content from each section.
Finally, I'll summarize the important information."""
    
    reasoning_display = (TextBuilder.from_text(reasoning)
                       .with_slide(max_lines=3, format_type="raw")
                       .with_block_quote()
                       .build())
    print("1. AI Reasoning (last 3 thoughts as blockquote):")
    print(reasoning_display)
    print()
    
    # Tool Execution Trace
    execution_trace = """Processing page 1: Introduction
Processing page 2: Methodology
Processing page 3: Results
Processing page 4: Discussion
Processing page 5: Conclusions
Extraction completed successfully
Total pages processed: 5"""
    
    trace_display = (TextBuilder.from_text(execution_trace)
                    .with_slide(max_lines=3, format_type="text")
                    .build())
    print("2. Tool Execution Trace (last 3 steps in code block):")
    for line in trace_display:
        print(f"   {line}")
    print()
    
    # Status Updates
    status_updates = """Connecting to API endpoint ...
Authenticating user credentials ...
Loading vectorstore collections ...
Processing queries ...
Generating response ..."""
    
    status_display = (TextBuilder.from_text(status_updates)
                     .with_slide(max_lines=2, format_type="raw")
                     .with_prefix("🔸 ")
                     .build())
    print("3. Status Updates (last 2 with progress indicators):")
    for line in status_display:
        print(f"   {line}")
    print()


def demo_different_formats():
    """Demonstrate different output formats."""
    print("=== Different Output Formats ===")
    
    content = "Step 1: Initialize\nStep 2: Process\nStep 3: Validate\nStep 4: Complete"
    
    # Raw format
    raw_result = TextBuilder.from_text(content).with_slide(max_lines=2, format_type="raw").build()
    print("1. Raw format (list of strings):")
    print(f"   Type: {type(raw_result)}")
    print(f"   Content: {raw_result}")
    print()
    
    # Text format (code block)
    text_result = TextBuilder.from_text(content).with_slide(max_lines=2, format_type="text").build()
    print("2. Text format (code block):")
    print(f"   Type: {type(text_result)}")
    for line in text_result:
        print(f"   {line}")
    print()
    
    # String result (after blockquote)
    string_result = TextBuilder.from_text(content).with_slide(max_lines=2, format_type="raw").with_block_quote().build()
    print("3. String format (after blockquote):")
    print(f"   Type: {type(string_result)}")
    print(f"   Content:\n{string_result}")
    print()


def demo_header_footer():
    """Demonstrate header and footer functionality."""
    print("=== Header and Footer Examples ===")
    
    # Basic header and footer
    content = "Main content line 1\nMain content line 2"
    result1 = (TextBuilder.from_text(content)
              .with_header("📋 Report Header")
              .with_footer("📄 End of Report")
              .build())
    print("1. Basic header and footer:")
    for line in result1:
        print(f"   {line}")
    print()
    
    # Multi-line header and footer
    result2 = (TextBuilder.from_text(content)
              .with_header("=== DOCUMENT START ===\n🔍 Analysis Report")
              .with_footer("Generated on 2024-01-01\n=== DOCUMENT END ===")
              .build())
    print("2. Multi-line header and footer:")
    for line in result2:
        print(f"   {line}")
    print()
    
    # Header/footer with sliding and blockquote
    log_content = """Processing file 1
Processing file 2  
Processing file 3
Processing file 4
Processing file 5"""
    
    result3 = (TextBuilder.from_text(log_content)
              .with_header("🚀 Latest Activity")
              .with_slide(max_lines=3, format_type="raw")
              .with_footer("⏰ Last updated: now")
              .with_block_quote()
              .build())
    print("3. Header/footer with sliding and blockquote:")
    print(result3)
    print()
    
    # Complex formatting with all features
    task_log = """Task 1: Initialize system
Task 2: Load configuration
Task 3: Connect to database
Task 4: Process requests
Task 5: Generate reports
Task 6: Cleanup resources"""
    
    result4 = (TextBuilder.from_text(task_log)
              .with_header("📊 System Status Dashboard")
              .with_slide(max_lines=3, format_type="raw")
              .with_prefix("✅ ")
              .with_suffix(" [DONE]")
              .with_footer("🔄 Auto-refresh enabled")
              .build())
    print("4. Complex formatting with all features:")
    for line in result4:
        print(f"   {line}")
    print()
    
    # Practical example: Code documentation
    code_example = """def process_document(file_path):
    parser = DocumentParser()
    content = parser.parse(file_path)
    return content.extract_text()"""
    
    result5 = (TextBuilder.from_text(code_example)
              .with_header("💻 Python Code Example")
              .with_footer("📝 More examples at docs.example.com")
              .with_format("code")
              .build())
    print("5. Code documentation example:")
    for line in result5:
        print(f"   {line}")
    print()


if __name__ == "__main__":
    demo_basic_usage()
    demo_method_chaining()
    demo_real_world_scenarios()
    demo_different_formats()
    
    demo_header_footer()
    
    print("=== Summary ===")
    print("TextBuilder provides a fluent interface for text processing:")
    print("• TextBuilder.from_text(text) - Create builder")
    print("• .with_slide() - Apply sliding window")
    print("• .with_block_quote() - Add blockquote formatting")
    print("• .with_prefix() - Add prefix to lines")
    print("• .with_suffix() - Add suffix to lines")
    print("• .with_header() - Add header text")
    print("• .with_footer() - Add footer text")
    print("• .with_format() - Apply code/markdown formatting")
    print("• .build() - Get final result")
    print("\nMethods can be chained for complex text transformations!") 