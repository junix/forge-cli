"""Tests for the TextBuilder class in builder.py."""

import pytest
from forge_cli.display.v3.builder import TextBuilder, Build


class TestTextBuilder:
    """Test cases for TextBuilder class."""

    def test_basic_initialization(self):
        """Test basic TextBuilder initialization."""
        text = "Hello\nWorld"
        builder = TextBuilder(text)
        result = builder.build()
        assert result == text

    def test_convenience_function(self):
        """Test the Build convenience function."""
        text = "Hello\nWorld"
        result = Build(text).build()
        assert result == text

    def test_with_block_quote(self):
        """Test blockquote transformation."""
        text = "Line 1\nLine 2\nLine 3"
        result = Build(text).with_block_quote().build()
        expected = "> Line 1\n> Line 2\n> Line 3"
        assert result == expected

    def test_with_slide_basic(self):
        """Test basic sliding display."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = Build(text).with_slide(max_lines=3, format_type="raw").build()
        expected = ["Line 3", "Line 4", "Line 5"]
        assert result == expected

    def test_with_slide_text_format(self):
        """Test sliding display with text format."""
        text = "Line 1\nLine 2\nLine 3"
        result = Build(text).with_slide(max_lines=2, format_type="text").build()
        expected = ["```text", "Line 2", "Line 3", "```"]
        assert result == expected

    def test_chaining_slide_then_blockquote(self):
        """Test chaining slide then blockquote."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = Build(text).with_slide(max_lines=3, format_type="raw").with_block_quote().build()
        expected = "> Line 3\n> Line 4\n> Line 5"
        assert result == expected

    def test_chaining_blockquote_then_slide(self):
        """Test chaining blockquote then slide."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = Build(text).with_block_quote().with_slide(max_lines=2, format_type="raw").build()
        expected = ["> Line 4", "> Line 5"]
        assert result == expected

    def test_with_format_code(self):
        """Test format transformation with code."""
        text = "Hello\nWorld"
        result = Build(text).with_format("code").build()
        expected = ["```text", "Hello", "World", "```"]
        assert result == expected

    def test_with_format_markdown(self):
        """Test format transformation with markdown."""
        text = "Hello\nWorld"
        result = Build(text).with_format("markdown").build()
        expected = "Hello\nWorld"
        assert result == expected

    def test_with_prefix(self):
        """Test prefix transformation."""
        text = "Line 1\nLine 2"
        result = Build(text).with_prefix(">> ").build()
        expected = [">> Line 1", ">> Line 2"]
        assert result == expected

    def test_with_suffix(self):
        """Test suffix transformation."""
        text = "Line 1\nLine 2"
        result = Build(text).with_suffix(" <<").build()
        expected = ["Line 1 <<", "Line 2 <<"]
        assert result == expected

    def test_with_header(self):
        """Test header transformation."""
        text = "Content line 1\nContent line 2"
        result = Build(text).with_header("Header line").build()
        expected = ["Header line", "Content line 1", "Content line 2"]
        assert result == expected

    def test_with_header_multiline(self):
        """Test header with multiple lines."""
        text = "Content"
        result = Build(text).with_header("Header 1\nHeader 2").build()
        expected = ["Header 1", "Header 2", "Content"]
        assert result == expected

    def test_with_footer(self):
        """Test footer transformation."""
        text = "Content line 1\nContent line 2"
        result = Build(text).with_footer("Footer line").build()
        expected = ["Content line 1", "Content line 2", "Footer line"]
        assert result == expected

    def test_with_footer_multiline(self):
        """Test footer with multiple lines."""
        text = "Content"
        result = Build(text).with_footer("Footer 1\nFooter 2").build()
        expected = ["Content", "Footer 1", "Footer 2"]
        assert result == expected

    def test_header_and_footer_together(self):
        """Test using both header and footer."""
        text = "Middle content"
        result = Build(text).with_header("Top").with_footer("Bottom").build()
        expected = ["Top", "Middle content", "Bottom"]
        assert result == expected

    def test_header_footer_with_empty_content(self):
        """Test header and footer with empty content."""
        result = Build("").with_header("Header").with_footer("Footer").build()
        expected = ["Header", "", "Footer"]
        assert result == expected

    def test_header_on_none_content(self):
        """Test header with None content."""
        result = Build(None).with_header("Header").build()
        assert result == "Header"

    def test_footer_on_none_content(self):
        """Test footer with None content."""
        result = Build(None).with_footer("Footer").build()
        assert result == "Footer"

    def test_empty_header_footer(self):
        """Test with empty header and footer strings."""
        text = "Content"
        result = Build(text).with_header("").with_footer("").build()
        expected = ["", "Content", ""]
        assert result == expected

    def test_header_footer_order_matters(self):
        """Test that header/footer order affects result."""
        text = "Middle"
        
        # Header first, then footer
        result1 = Build(text).with_header("Top").with_footer("Bottom").build()
        expected1 = ["Top", "Middle", "Bottom"]
        assert result1 == expected1
        
        # Footer first, then header (header still goes to beginning)
        result2 = Build(text).with_footer("Bottom").with_header("Top").build()
        expected2 = ["Top", "Middle", "Bottom"]
        assert result2 == expected2

    def test_complex_chaining(self):
        """Test complex method chaining."""
        text = "Step 1: Start\nStep 2: Process\nStep 3: Validate\nStep 4: Complete\nStep 5: Finish"
        result = (Build(text)
                 .with_slide(max_lines=3, format_type="raw")
                 .with_prefix("📋 ")
                 .with_suffix(" ✓")
                 .build())
        
        expected = ["📋 Step 3: Validate ✓", "📋 Step 4: Complete ✓", "📋 Step 5: Finish ✓"]
        assert result == expected

    def test_complex_chaining_with_header_footer(self):
        """Test complex chaining including header and footer."""
        text = "Line 1\nLine 2\nLine 3\nLine 4"
        result = (Build(text)
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
        result = (Build(text)
                 .with_header("📢 Announcement")
                 .with_footer("Thank you!")
                 .with_block_quote()
                 .build())
        
        expected = "> 📢 Announcement\n> Important message\n> Thank you!"
        assert result == expected

    def test_empty_content(self):
        """Test with empty content."""
        result = Build("").with_block_quote().build()
        assert result == ""

    def test_none_content_handling(self):
        """Test handling of None content during processing."""
        builder = TextBuilder("Hello")
        builder._content = None  # Simulate None content
        result = builder.with_block_quote().with_slide().build()
        assert result == ""

    def test_slide_with_empty_result(self):
        """Test sliding display that returns None."""
        text = ""
        result = Build(text).with_slide(max_lines=3).build()
        assert result == []

    def test_realistic_execution_trace_example(self):
        """Test with realistic execution trace scenario."""
        trace = """[10:00:00] Starting file processing
[10:00:01] Loading document
[10:00:02] Parsing page 1
[10:00:03] Parsing page 2
[10:00:04] Extracting text
[10:00:05] Processing complete"""
        
        result = (Build(trace)
                 .with_slide(max_lines=3, format_type="raw")
                 .with_block_quote()
                 .build())
        
        expected = "> [10:00:03] Parsing page 2\n> [10:00:04] Extracting text\n> [10:00:05] Processing complete"
        assert result == expected

    def test_reasoning_text_example(self):
        """Test with reasoning text scenario."""
        reasoning = """I need to analyze this document carefully.
First, I'll examine the structure.
Then I'll look for key information.
Finally, I'll provide a summary."""
        
        result = (Build(reasoning)
                 .with_slide(max_lines=2, format_type="raw")
                 .with_block_quote()
                 .build())
        
        expected = "> Then I'll look for key information.\n> Finally, I'll provide a summary."
        assert result == expected

    def test_method_chaining_order_independence(self):
        """Test different ordering of operations."""
        text = "A\nB\nC\nD"
        
        # Order 1: slide then prefix
        result1 = (Build(text)
                  .with_slide(max_lines=2, format_type="raw")
                  .with_prefix("• ")
                  .build())
        
        # Order 2: different slide params
        result2 = (Build(text)
                  .with_slide(max_lines=3, format_type="raw")
                  .with_prefix("• ")
                  .build())
        
        assert result1 == ["• C", "• D"]
        assert result2 == ["• B", "• C", "• D"]

    def test_list_to_string_conversion(self):
        """Test proper conversion between list and string states."""
        text = "Line 1\nLine 2\nLine 3"
        
        # This should work: raw -> blockquote -> slide -> format
        result = (Build(text)
                 .with_slide(max_lines=2, format_type="raw")  # Returns list
                 .with_block_quote()  # Should handle list input, return string
                 .with_slide(max_lines=1, format_type="text")  # Should handle string input
                 .build())
        
        # Should get the last line of the blockquoted text
        assert isinstance(result, list)
        assert "```text" in result
        assert "```" in result 