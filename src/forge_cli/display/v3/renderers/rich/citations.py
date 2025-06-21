"""Citations renderer for Rich display system."""

from typing import Any

from rich.markdown import Markdown
from ..rendable import Rendable


class CitationsRenderer(Rendable):
    """Renderer for citations as a references section."""
    
    def __init__(self, citations: list[Any]):
        """Initialize the citations renderer.
        
        Args:
            citations: List of citation objects
        """
        self.citations = citations
    
    def render(self) -> Markdown | None:
        """Render citations as a Markdown references section.
        
        Returns:
            Markdown object with formatted references section or None if no citations
        """
        if not self.citations:
            return None
        
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
        
        references_text = "\n".join(ref_lines)
        return Markdown(references_text)


# Legacy function for backward compatibility
def render_citations(citations: list[Any]) -> Markdown | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        citations: List of citation objects
        
    Returns:
        Markdown object with formatted references section or None if no citations
    """
    return CitationsRenderer(citations).render() 