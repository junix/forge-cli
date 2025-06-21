"""Tests for the TextBuilder class in builder.py."""

import pytest
from forge_cli.display.v3.builder import TextBuilder


class TestTextBuilder:
    """Test cases for TextBuilder class."""

    def test_basic_initialization(self):
        """Test basic TextBuilder initialization."""
        text = "Hello, World!"
        builder = TextBuilder(text)
        result = builder.build()
        assert result == text

    def test_convenience_function(self):
        """Test the from_text class method."""
        text = "Hello, World!"
        result = TextBuilder.from_text(text).build()
        assert result == text

    def test_with_block_quote(self):
        """Test blockquote transformation."""
        text = "Hello\nWorld"
        result = TextBuilder.from_text(text).with_block_quote().build()
        expected = "> Hello\n> World"
        assert result == expected

    def test_with_slide_basic(self):
        """Test sliding display with raw format."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = TextBuilder.from_text(text).with_slide(max_lines=3, format_type="raw").build()
        expected = ["Line 3", "Line 4", "Line 5"]
        assert result == expected

    def test_with_slide_text_format(self):
        """Test sliding display with text format (code block)."""
        text = "Line 1\nLine 2\nLine 3"
        result = TextBuilder.from_text(text).with_slide(max_lines=2, format_type="text").build()
        expected = ["```text", "Line 2", "Line 3", "```"]
        assert result == expected

    def test_chaining_slide_then_blockquote(self):
        """Test chaining slide then blockquote."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = TextBuilder.from_text(text).with_slide(max_lines=3, format_type="raw").with_block_quote().build()
        expected = "> Line 3\n> Line 4\n> Line 5"
        assert result == expected

    def test_chaining_blockquote_then_slide(self):
        """Test chaining blockquote then slide (should work differently)."""
        text = "Line 1\nLine 2\nLine 3"
        result = TextBuilder.from_text(text).with_block_quote().with_slide(max_lines=2, format_type="raw").build()
        expected = ["> Line 2", "> Line 3"]
        assert result == expected

    def test_with_format_code(self):
        """Test code formatting."""
        text = "print('hello')\nprint('world')"
        result = TextBuilder.from_text(text).with_format("code").build()
        expected = ["```text", "print('hello')", "print('world')", "```"]
        assert result == expected

    def test_with_format_markdown(self):
        """Test markdown formatting."""
        text = "# Header\nContent"
        result = TextBuilder.from_text(text).with_format("markdown").build()
        expected = "# Header\nContent"
        assert result == expected

    def test_with_prefix(self):
        """Test prefix transformation."""
        text = "Line 1\nLine 2"
        result = TextBuilder.from_text(text).with_prefix(">> ").build()
        expected = [">> Line 1", ">> Line 2"]
        assert result == expected

    def test_with_suffix(self):
        """Test suffix transformation."""
        text = "Line 1\nLine 2"
        result = TextBuilder.from_text(text).with_suffix(" <<").build()
        expected = ["Line 1 <<", "Line 2 <<"]
        assert result == expected

    def test_with_header(self):
        """Test header transformation."""
        text = "Content line 1\nContent line 2"
        result = TextBuilder.from_text(text).with_header("Header line").build()
        expected = ["Header line", "Content line 1", "Content line 2"]
        assert result == expected

    def test_with_header_multiline(self):
        """Test header with multiple lines."""
        text = "Content"
        result = TextBuilder.from_text(text).with_header("Header 1\nHeader 2").build()
        expected = ["Header 1", "Header 2", "Content"]
        assert result == expected

    def test_with_footer(self):
        """Test footer transformation."""
        text = "Content line 1\nContent line 2"
        result = TextBuilder.from_text(text).with_footer("Footer line").build()
        expected = ["Content line 1", "Content line 2", "Footer line"]
        assert result == expected

    def test_with_footer_multiline(self):
        """Test footer with multiple lines."""
        text = "Content"
        result = TextBuilder.from_text(text).with_footer("Footer 1\nFooter 2").build()
        expected = ["Content", "Footer 1", "Footer 2"]
        assert result == expected

    def test_header_and_footer_together(self):
        """Test using both header and footer."""
        text = "Middle content"
        result = TextBuilder.from_text(text).with_header("Top").with_footer("Bottom").build()
        expected = ["Top", "Middle content", "Bottom"]
        assert result == expected

    def test_header_footer_with_empty_content(self):
        """Test header and footer with empty content."""
        result = TextBuilder.from_text("").with_header("Header").with_footer("Footer").build()
        expected = ["Header", "", "Footer"]
        assert result == expected

    def test_header_on_none_content(self):
        """Test header with None content."""
        result = TextBuilder.from_text(None).with_header("Header").build()
        assert result == "Header"

    def test_footer_on_none_content(self):
        """Test footer with None content."""
        result = TextBuilder.from_text(None).with_footer("Footer").build()
        assert result == "Footer"

    def test_empty_header_footer(self):
        """Test with empty header and footer strings."""
        text = "Content"
        result = TextBuilder.from_text(text).with_header("").with_footer("").build()
        expected = ["", "Content", ""]
        assert result == expected

    def test_header_footer_order_matters(self):
        """Test that header/footer order affects result."""
        text = "Middle"
        
        # Header first, then footer
        result1 = TextBuilder.from_text(text).with_header("Top").with_footer("Bottom").build()
        expected1 = ["Top", "Middle", "Bottom"]
        assert result1 == expected1
        
        # Footer first, then header (header still goes to beginning)
        result2 = TextBuilder.from_text(text).with_footer("Bottom").with_header("Top").build()
        expected2 = ["Top", "Middle", "Bottom"]
        assert result2 == expected2

    def test_complex_chaining(self):
        """Test complex method chaining."""
        text = "Step 1: Start\nStep 2: Process\nStep 3: Validate\nStep 4: Complete\nStep 5: Finish"
        result = (TextBuilder.from_text(text)
                 .with_slide(max_lines=3, format_type="raw")
                 .with_prefix("📋 ")
                 .with_suffix(" ✓")
                 .build())
        
        expected = ["📋 Step 3: Validate ✓", "📋 Step 4: Complete ✓", "📋 Step 5: Finish ✓"]
        assert result == expected

    def test_complex_chaining_with_header_footer(self):
        """Test complex chaining including header and footer."""
        text = "Line 1\nLine 2\nLine 3\nLine 4"
        result = (TextBuilder.from_text(text)
                 .with_header("=== Start ===")
                 .with_slide(max_lines=3, format_type="raw")
                 .with_footer("=== End ===")
                 .with_prefix("• ")
                 .build())
        
        # After header is added: ["=== Start ===", "Line 1", "Line 2", "Line 3", "Line 4"]
        # After slide(max_lines=3): Last 3 lines are ["Line 2", "Line 3", "Line 4"] 
        # After footer is added: ["Line 2", "Line 3", "Line 4", "=== End ==="]
        # After prefix: ["• Line 2", "• Line 3", "• Line 4", "• === End ==="]
        expected = ["• Line 2", "• Line 3", "• Line 4", "• === End ==="]
        assert result == expected

    def test_header_footer_with_blockquote(self):
        """Test header and footer with blockquote formatting."""
        text = "Important message"
        result = (TextBuilder.from_text(text)
                 .with_header("📢 Announcement")
                 .with_footer("Thank you!")
                 .with_block_quote()
                 .build())
        
        expected = "> 📢 Announcement\n> Important message\n> Thank you!"
        assert result == expected

    def test_empty_content(self):
        """Test with empty content."""
        result = TextBuilder.from_text("").with_block_quote().build()
        assert result == ""

    def test_none_content_handling(self):
        """Test with None content."""
        builder = TextBuilder("Hello")
        builder._content = None
        result = builder.with_block_quote().with_slide().build()
        assert result == ""

    def test_slide_with_empty_result(self):
        """Test sliding display with empty result."""
        text = "\n\n\n"  # Only empty lines
        result = TextBuilder.from_text(text).with_slide(max_lines=3).build()
        assert result == []

    def test_realistic_execution_trace_example(self):
        """Test realistic execution trace scenario."""
        trace = """[10:00:01] Starting file analysis
[10:00:02] Reading file: document.pdf
[10:00:03] Parsing page 1 of 5
[10:00:04] Parsing page 2 of 5
[10:00:05] Parsing page 3 of 5
[10:00:06] Parsing page 4 of 5
[10:00:07] Parsing page 5 of 5
[10:00:08] Extracting text content
[10:00:09] Processing complete"""

        result = (TextBuilder.from_text(trace)
                 .with_slide(max_lines=3, format_type="text")
                 .build())
        
        expected = ["```text", "[10:00:07] Parsing page 5 of 5", "[10:00:08] Extracting text content", "[10:00:09] Processing complete", "```"]
        assert result == expected

    def test_reasoning_text_example(self):
        """Test reasoning text formatting."""
        reasoning = """First, I'll analyze the document structure to understand its layout.
Then, I'll identify the key sections and headings.
Next, I'll extract the main content from each section.
Finally, I'll summarize the important information."""

        result = (TextBuilder.from_text(reasoning)
                 .with_slide(max_lines=3, format_type="raw")
                 .with_block_quote()
                 .build())
        
        expected = "> Then, I'll identify the key sections and headings.\n> Next, I'll extract the main content from each section.\n> Finally, I'll summarize the important information."
        assert result == expected

    def test_method_chaining_order_independence(self):
        """Test that certain method chains produce consistent results."""
        text = "Line 1\nLine 2\nLine 3\nLine 4"
        
        # Different orders should produce similar logical results
        result1 = (TextBuilder.from_text(text)
                  .with_slide(max_lines=2, format_type="raw")
                  .with_prefix("• ")
                  .build())
        
        result2 = (TextBuilder.from_text(text)
                  .with_prefix("• ")
                  .with_slide(max_lines=2, format_type="raw")
                  .build())
        
        # Both should be lists with prefixed content
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        assert all("•" in line for line in result1)
        assert all("•" in line for line in result2)

    def test_list_to_string_conversion(self):
        """Test conversion between list and string formats."""
        text = "Line 1\nLine 2\nLine 3"
        
        # Start with list (via prefix), then convert to string (via blockquote)
        result = (TextBuilder.from_text(text)
                 .with_prefix("• ")
                 .with_block_quote()
                 .build())
        
        expected = "> • Line 1\n> • Line 2\n> • Line 3"
        assert result == expected
        assert isinstance(result, str) 