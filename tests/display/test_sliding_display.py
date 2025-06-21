"""Tests for the sliding_display function in style.py."""

import pytest
from forge_cli.display.v3.style import sliding_display


class TestSlidingDisplay:
    """Test cases for sliding_display function."""

    def test_sliding_display_basic(self):
        """Test basic sliding display functionality."""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = sliding_display(content, max_lines=3)
        
        expected = ["```text", "Line 3", "Line 4", "Line 5", "```"]
        assert result == expected

    def test_sliding_display_fewer_lines_than_max(self):
        """Test when content has fewer lines than max_lines."""
        content = "Line 1\nLine 2"
        result = sliding_display(content, max_lines=5)
        
        expected = ["```text", "Line 1", "Line 2", "```"]
        assert result == expected

    def test_sliding_display_empty_content(self):
        """Test with empty content."""
        assert sliding_display("") is None
        assert sliding_display("   ") is None
        assert sliding_display("\n\n\n") is None

    def test_sliding_display_single_line(self):
        """Test with single line content."""
        content = "Single line"
        result = sliding_display(content, max_lines=3)
        
        expected = ["```text", "Single line", "```"]
        assert result == expected

    def test_sliding_display_with_empty_lines(self):
        """Test handling of empty lines."""
        content = "Line 1\n\nLine 3\n\nLine 5"
        
        # With strip_empty=True (default)
        result = sliding_display(content, max_lines=3, strip_empty=True)
        expected = ["```text", "Line 1", "Line 3", "Line 5", "```"]
        assert result == expected
        
        # With strip_empty=False
        result = sliding_display(content, max_lines=3, strip_empty=False)
        expected = ["```text", "Line 3", "", "Line 5", "```"]
        assert result == expected

    def test_sliding_display_format_types(self):
        """Test different format types."""
        content = "Line 1\nLine 2\nLine 3"
        
        # Text format (default)
        result = sliding_display(content, max_lines=2, format_type="text")
        expected = ["```text", "Line 2", "Line 3", "```"]
        assert result == expected
        
        # Code format (same as text)
        result = sliding_display(content, max_lines=2, format_type="code")
        expected = ["```text", "Line 2", "Line 3", "```"]
        assert result == expected
        
        # Markdown format
        result = sliding_display(content, max_lines=2, format_type="markdown")
        expected = ["Line 2", "Line 3"]
        assert result == expected
        
        # Raw format
        result = sliding_display(content, max_lines=2, format_type="raw")
        expected = ["Line 2", "Line 3"]
        assert result == expected

    def test_sliding_display_execution_trace_example(self):
        """Test with realistic execution trace content."""
        trace_content = """[2024-01-01 10:00:00] Starting file processing
[2024-01-01 10:00:01] Reading file: document.pdf
[2024-01-01 10:00:02] Processing page 1
[2024-01-01 10:00:03] Processing page 2
[2024-01-01 10:00:04] Processing page 3
[2024-01-01 10:00:05] Extraction complete"""
        
        result = sliding_display(trace_content, max_lines=3)
        expected = [
            "```text",
            "[2024-01-01 10:00:03] Processing page 2",
            "[2024-01-01 10:00:04] Processing page 3",
            "[2024-01-01 10:00:05] Extraction complete",
            "```"
        ]
        assert result == expected

    def test_sliding_display_edge_cases(self):
        """Test edge cases and unusual inputs."""
        # Only whitespace lines
        content = "  \n   \n    "
        assert sliding_display(content, strip_empty=True) is None
        
        result = sliding_display(content, strip_empty=False)
        expected = ["```text", "  ", "   ", "    ", "```"]
        assert result == expected
        
        # Mixed content
        content = "Valid line\n\n  \nAnother valid line"
        result = sliding_display(content, max_lines=2, strip_empty=True)
        expected = ["```text", "Valid line", "Another valid line", "```"]
        assert result == expected

    def test_sliding_display_large_content(self):
        """Test with large content to ensure sliding works correctly."""
        lines = [f"Line {i}" for i in range(1, 101)]  # 100 lines
        content = "\n".join(lines)
        
        result = sliding_display(content, max_lines=5)
        expected = ["```text", "Line 96", "Line 97", "Line 98", "Line 99", "Line 100", "```"]
        assert result == expected

    def test_sliding_display_max_lines_zero(self):
        """Test with max_lines=0."""
        content = "Line 1\nLine 2\nLine 3"
        result = sliding_display(content, max_lines=0)
        expected = ["```text", "```"]
        assert result == expected

    def test_sliding_display_max_lines_negative(self):
        """Test with negative max_lines (should handle gracefully)."""
        content = "Line 1\nLine 2\nLine 3"
        result = sliding_display(content, max_lines=-1)
        # Negative max_lines should return empty list
        expected = ["```text", "```"]
        assert result == expected 