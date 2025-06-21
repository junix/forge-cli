"""Text processing builder for fluent method chaining.

This module provides the TextBuilder class for chaining text transformations
using a fluent interface pattern.
"""

from .style import sliding_display


class TextBuilder:
    """Builder class for chaining text processing operations.
    
    Provides a fluent interface for applying multiple text transformations
    in sequence using method chaining.
    
    Example:
        >>> text = "Line 1\\nLine 2\\nLine 3\\nLine 4\\nLine 5"
        >>> result = TextBuilder(text).with_slide(max_lines=3).with_block_quote().build()
        >>> print(result)
        > Line 3
        > Line 4  
        > Line 5
        
        >>> result = TextBuilder(text).with_block_quote().with_slide(max_lines=2, format_type="raw").build()
        >>> print("\\n".join(result))
        > Line 4
        > Line 5
    """
    
    def __init__(self, text: str):
        """Initialize builder with text content.
        
        Args:
            text: Initial text content to process
        """
        self._content = text
        self._is_list = False  # Track if content is a list of lines
    
    def with_slide(
        self, 
        max_lines: int = 3, 
        format_type: str = "raw", 
        strip_empty: bool = True
    ) -> "TextBuilder":
        """Apply sliding display transformation.
        
        Args:
            max_lines: Maximum number of lines to show (default: 3)
            format_type: Output format - "text", "code", "markdown", "raw" (default: "raw")
            strip_empty: Whether to remove empty lines before processing (default: True)
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            return self
            
        # Convert content to string if it's a list
        if self._is_list:
            content_str = "\n".join(self._content) if isinstance(self._content, list) else str(self._content)
        else:
            content_str = str(self._content)
            
        result = sliding_display(content_str, max_lines, format_type, strip_empty)
        
        if result is not None:
            self._content = result
            self._is_list = True
        else:
            self._content = []
            self._is_list = True
            
        return self
    
    def with_block_quote(self) -> "TextBuilder":
        """Apply blockquote transformation.
        
        Converts text to blockquote format by adding '> ' prefix to each line.
        
        Returns:
            Self for method chaining
        """
        if self._content is None:
            return self
            
        # Import here to avoid circular imports
        from forge_cli.style.markdowns import convert_to_blockquote
        
        # Convert content to string if it's a list
        if self._is_list:
            content_str = "\n".join(self._content) if isinstance(self._content, list) else str(self._content)
        else:
            content_str = str(self._content)
        
        # Apply blockquote transformation
        result = convert_to_blockquote(content_str)
        
        # Result is always a string for blockquote
        self._content = result
        self._is_list = False
        
        return self
    
    def with_format(self, format_type: str) -> "TextBuilder":
        """Apply formatting transformation.
        
        Args:
            format_type: Format to apply - "code", "markdown"
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            return self
            
        # Convert content to string if it's a list
        if self._is_list:
            content_str = "\n".join(self._content) if isinstance(self._content, list) else str(self._content)
        else:
            content_str = str(self._content)
        
        if format_type == "code":
            # Wrap in code block
            formatted_lines = ["```text"]
            formatted_lines.extend(content_str.split("\n"))
            formatted_lines.append("```")
            self._content = formatted_lines
            self._is_list = True
        elif format_type == "markdown":
            # Keep as markdown (no change needed)
            self._content = content_str
            self._is_list = False
        else:
            # Unknown format, no change
            pass
            
        return self
    
    def with_prefix(self, prefix: str) -> "TextBuilder":
        """Add prefix to each line.
        
        Args:
            prefix: Prefix to add to each line
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            return self
            
        # Convert content to string if it's a list  
        if self._is_list:
            lines = self._content if isinstance(self._content, list) else [str(self._content)]
        else:
            lines = str(self._content).split("\n")
            
        prefixed_lines = [f"{prefix}{line}" for line in lines]
        self._content = prefixed_lines
        self._is_list = True
        
        return self
    
    def with_suffix(self, suffix: str) -> "TextBuilder":
        """Add suffix to each line.
        
        Args:
            suffix: Suffix to add to each line
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            return self
            
        # Convert content to string if it's a list  
        if self._is_list:
            lines = self._content if isinstance(self._content, list) else [str(self._content)]
        else:
            lines = str(self._content).split("\n")
            
        suffixed_lines = [f"{line}{suffix}" for line in lines]
        self._content = suffixed_lines
        self._is_list = True
        
        return self
    
    def with_header(self, header: str) -> "TextBuilder":
        """Add header text at the beginning.
        
        Args:
            header: Header text to add at the beginning
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            self._content = header
            self._is_list = False
            return self
            
        # Convert content to lines
        if self._is_list:
            content_lines = self._content if isinstance(self._content, list) else [str(self._content)]
        else:
            content_lines = str(self._content).split("\n")
        
        # Add header lines at the beginning (handle empty string case)
        header_lines = header.split("\n") if header is not None else []
        combined_lines = header_lines + content_lines
        
        self._content = combined_lines
        self._is_list = True
        
        return self
    
    def with_footer(self, footer: str) -> "TextBuilder":
        """Add footer text at the end.
        
        Args:
            footer: Footer text to add at the end
            
        Returns:
            Self for method chaining
        """
        if self._content is None:
            self._content = footer
            self._is_list = False
            return self
            
        # Convert content to lines
        if self._is_list:
            content_lines = self._content if isinstance(self._content, list) else [str(self._content)]
        else:
            content_lines = str(self._content).split("\n")
        
        # Add footer lines at the end (handle empty string case)
        footer_lines = footer.split("\n") if footer is not None else []
        combined_lines = content_lines + footer_lines
        
        self._content = combined_lines
        self._is_list = True
        
        return self
    
    def build(self) -> str | list[str]:
        """Build the final processed content.
        
        Returns:
            Processed content as string or list of strings
        """
        if self._content is None:
            return ""
            
        if self._is_list:
            return self._content
        else:
            return str(self._content)


def Build(text: str) -> TextBuilder:
    """Create a new TextBuilder instance.
    
    Convenience function for creating a TextBuilder with shorter syntax.
    
    Args:
        text: Initial text content to process
        
    Returns:
        New TextBuilder instance
        
    Example:
        >>> result = Build("Hello\\nWorld").with_block_quote().build()
        >>> print(result)
        > Hello
        > World
    """
    return TextBuilder(text) 