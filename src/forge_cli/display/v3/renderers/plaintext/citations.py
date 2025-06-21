"""Citations renderer for plaintext display system."""

from typing import Any

from rich.text import Text
from forge_cli.response._types.response import Response
from forge_cli.response.type_guards import is_message_item

from ..rendable import Rendable
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles


class PlaintextCitationsRenderer(Rendable):
    """Plaintext citations renderer."""
    
    def __init__(self, styles: PlaintextStyles, config: PlaintextDisplayConfig):
        """Initialize the citations renderer.
        
        Args:
            styles: Style manager instance
            config: Display configuration
        """
        self.styles = styles
        self.config = config
        self._citations = []
    
    def with_citations(self, citations: list[Any]) -> "PlaintextCitationsRenderer":
        """Set the citations to render.
        
        Args:
            citations: List of citation objects
            
        Returns:
            Self for method chaining
        """
        self._citations = citations
        return self
    
    def render(self) -> Text | None:
        """Render citations list with proper formatting.
        
        Returns:
            Rich Text object with formatted citations or None if no citations
        """
        if not self._citations or not self.config.show_citations:
            return None
        
        text = Text()
        
        # Use compact format for file citations
        text.append("\nreferences:\n", style=self.styles.get_style("citation_ref"))

        for i, citation in enumerate(self._citations, 1):
            if citation.type == "file_citation":
                # Compact format: 1. filename, P{index} - using typed properties
                source = citation.filename or citation.file_id or "Unknown"
                page = f", P{citation.index}" if citation.index is not None else ""
                text.append(f"{i}. {source}{page}\n", style=self.styles.get_style("citation_source"))

            elif citation.type == "url_citation":
                # URL format: 1. title (domain) - using typed properties
                title = citation.title if citation.title else "Web Page"
                url = citation.url
                if url:
                    try:
                        from urllib.parse import urlparse

                        domain = urlparse(url).netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
                        text.append(f"{i}. {title} ({domain})\n", style=self.styles.get_style("citation_source"))
                    except Exception:
                        text.append(f"{i}. {title}\n", style=self.styles.get_style("citation_source"))
                else:
                    text.append(f"{i}. {title}\n", style=self.styles.get_style("citation_source"))
            elif citation.type == "file_path":
                # File path format - using typed properties
                source = citation.file_id or "Unknown"
                text.append(f"{i}. {source}\n", style=self.styles.get_style("citation_source"))
            else:
                # Fallback format
                source = getattr(citation, "filename", getattr(citation, "url", "Unknown"))
                text.append(f"{i}. {source}\n", style=self.styles.get_style("citation_source"))
        
        return text
    
    @classmethod
    def from_response(cls, response: Response, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextCitationsRenderer":
        """Factory method to create renderer from response.
        
        Args:
            response: Response object to extract citations from
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Citations renderer with extracted citations
        """
        citations = cls._extract_citations(response)
        return cls(styles, config).with_citations(citations)
    
    @staticmethod
    def _extract_citations(response: Response) -> list[Any]:
        """Extract all citations from response annotations using type-based API.
        
        Args:
            response: Response object to extract citations from
            
        Returns:
            List of citation objects
        """
        citations = []

        for item in response.output:
            if is_message_item(item):
                for content in item.content:
                    if content.type == "output_text" and content.annotations:
                        for annotation in content.annotations:
                            # Only include citation types
                            if annotation.type in ["file_citation", "url_citation", "file_path"]:
                                citations.append(annotation)

        return citations


# Legacy function for backward compatibility
def render_citations(response: Response, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> Text | None:
    """Legacy function wrapper for backward compatibility.
    
    Args:
        response: Response object to extract citations from
        styles: Style manager instance
        config: Display configuration
        
    Returns:
        Rendered Text object with citations or None
    """
    renderer = PlaintextCitationsRenderer.from_response(response, styles, config)
    return renderer.render() 