"""Parser for @ file reference syntax in chat messages."""

from __future__ import annotations

import re
from typing import NamedTuple


class FileReference(NamedTuple):
    """Represents a file reference in a message."""
    file_id: str
    start_pos: int
    end_pos: int


class ParsedMessage(NamedTuple):
    """Represents a parsed message with file references."""
    text: str
    file_references: list[FileReference]


class FileReferenceParser:
    """Parser for @ file reference syntax.
    
    Parses messages like:
    - "@file_123 What is this document about?"
    - "Compare @doc_abc and @doc_xyz"
    - "Based on @report_2024 and @analysis_data, what are the trends?"
    """
    
    # Pattern to match @file_id (alphanumeric, underscore, hyphen)
    FILE_REFERENCE_PATTERN = re.compile(r'@([a-zA-Z0-9_-]+)')
    
    @classmethod
    def parse(cls, message: str) -> ParsedMessage:
        """Parse a message to extract file references.
        
        Args:
            message: The input message text
            
        Returns:
            ParsedMessage with text and extracted file references
        """
        file_references = []
        
        # Find all file references
        for match in cls.FILE_REFERENCE_PATTERN.finditer(message):
            file_id = match.group(1)  # The part after @
            start_pos = match.start()
            end_pos = match.end()
            
            file_references.append(FileReference(
                file_id=file_id,
                start_pos=start_pos,
                end_pos=end_pos
            ))
        
        return ParsedMessage(
            text=message,
            file_references=file_references
        )
    
    @classmethod
    def has_file_references(cls, message: str) -> bool:
        """Check if a message contains file references.
        
        Args:
            message: The input message text
            
        Returns:
            True if the message contains @ file references
        """
        return bool(cls.FILE_REFERENCE_PATTERN.search(message))
    
    @classmethod
    def extract_file_ids(cls, message: str) -> list[str]:
        """Extract just the file IDs from a message.
        
        Args:
            message: The input message text
            
        Returns:
            List of file IDs referenced in the message
        """
        return [match.group(1) for match in cls.FILE_REFERENCE_PATTERN.finditer(message)]
    
    @classmethod
    def replace_file_references(cls, message: str, replacement_func=None) -> str:
        """Replace file references in a message.
        
        Args:
            message: The input message text
            replacement_func: Function to generate replacement text (optional)
                            If None, removes the @ symbol but keeps the file ID
            
        Returns:
            Message with file references replaced
        """
        if replacement_func is None:
            # Default: just remove the @ symbol
            return cls.FILE_REFERENCE_PATTERN.sub(r'\1', message)
        
        def replacer(match):
            file_id = match.group(1)
            return replacement_func(file_id)
        
        return cls.FILE_REFERENCE_PATTERN.sub(replacer, message)


def create_file_input_message(parsed_message: ParsedMessage) -> list:
    """Create input message content with file references.
    
    Args:
        parsed_message: Parsed message with file references
        
    Returns:
        List of input content items for the API request
    """
    from forge_cli.response._types.response_input_file import ResponseInputFile
    from forge_cli.response._types.response_input_text import ResponseInputText
    
    content = []
    
    # Add file inputs for each referenced file
    for file_ref in parsed_message.file_references:
        content.append(ResponseInputFile(
            type="input_file",
            file_id=file_ref.file_id
        ))
    
    # Add the text content (with @ symbols removed for cleaner display)
    clean_text = FileReferenceParser.replace_file_references(parsed_message.text)
    content.append(ResponseInputText(
        type="input_text", 
        text=clean_text
    ))
    
    return content


# Example usage and testing functions
def demo_parser():
    """Demonstrate the file reference parser."""
    test_messages = [
        "@file_123 What is this document about?",
        "Compare @doc_abc and @doc_xyz for similarities",
        "Based on @report_2024, @analysis_data, and @summary_q3, what are the key trends?",
        "No file references in this message",
        "@single_file_ref",
        "Mixed content @file1 with some text @file2 and more text"
    ]
    
    print("🔍 File Reference Parser Demo:")
    print()
    
    for message in test_messages:
        parsed = FileReferenceParser.parse(message)
        print(f"Input: {message}")
        print(f"Has refs: {FileReferenceParser.has_file_references(message)}")
        print(f"File IDs: {FileReferenceParser.extract_file_ids(message)}")
        print(f"Clean text: {FileReferenceParser.replace_file_references(message)}")
        print(f"References: {parsed.file_references}")
        print(f"Content: {create_file_input_message(parsed)}")
        print("-" * 50)


if __name__ == "__main__":
    demo_parser()
