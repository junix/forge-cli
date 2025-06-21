"""Output renderer for Rich display system."""

from typing import Any

from forge_cli.display.citation_styling import long2circled
from ..rendable import Rendable


class MessageContentRenderer(Rendable):
    """Renderer for message content (text/refusal) with proper formatting."""
    
    def __init__(self, content):
        """Initialize the message content renderer.
        
        Args:
            content: The message content to render
        """
        self.content = content
    
    def render(self) -> str:
        """Render message content with proper formatting.
        
        Returns:
            Formatted content text
        """
        if self.content.type == "output_text":
            # Convert long-style citation markers to circled digits
            converted_text = long2circled(self.content.text)
            return converted_text
        elif self.content.type == "output_refusal":
            return f"> ⚠️ Response refused: {self.content.refusal}"
        return ""


class CitationsRenderer(Rendable):
    """Renderer for citations as a references section."""
    
    def __init__(self, citations: list[Any]):
        """Initialize the citations renderer.
        
        Args:
            citations: List of citation objects
        """
        self.citations = citations
    
    def render(self) -> str:
        """Render citations as a references section.
        
        Returns:
            Formatted references section
        """
        if not self.citations:
            return ""
        
        ref_lines = ["### References"]
        for idx, citation in enumerate(self.citations, 1):
            if citation.type == "file_citation":
                # Use typed properties from AnnotationFileCitation
                source = citation.filename or citation.file_id or "unknown_file"
                # Note: AnnotationFileCitation uses 'index' not 'page_number'
                page = f" p.{citation.index}" if citation.index is not None else ""
                ref_lines.append(f"{idx}. {source} 󰭤 {page}")
            elif citation.type == "url_citation":
                # Use typed properties from AnnotationURLCitation
                url = citation.url
                if not citation.title:
                    title = url
                else:
                    title = citation.title
                ref_lines.append(f"{idx}. [{title}]({url})")
            elif citation.type == "file_path":
                # Use typed properties from AnnotationFilePath
                source = citation.file_id or "unknown_file"
                ref_lines.append(f"󰅼[{idx}] {source}")
        
        return "\n".join(ref_lines)


# Legacy functions for backward compatibility
def render_message_content(content) -> str:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        content: The message content to render
        
    Returns:
        Formatted content text
    """
    return MessageContentRenderer(content).render()


def render_citations(citations: list[Any]) -> str:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        citations: List of citation objects
        
    Returns:
        Formatted references section
    """
    return CitationsRenderer(citations).render() 