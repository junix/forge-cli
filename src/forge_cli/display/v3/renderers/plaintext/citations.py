"""Citations renderer for plaintext display system."""

from typing import Any

from rich.text import Text
from rich.markdown import Markdown
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
    
    def render(self) -> Markdown | None:
        """Render citations list with Markdown link formatting.
        
        Returns:
            Rich Text object with Markdown-formatted citations or None if no citations
        """
        if not self._citations or not self.config.show_citations:
            return None
        
        text = []
        
        # Use Markdown format for citations
        text.append("\n\n#### references:\n")

        for i, citation in enumerate(self._citations, 1):
            if citation.type == "file_citation":
                # Markdown format: 1. [filename, P{index}](file_id)
                source = citation.filename or citation.file_id or "Unknown"
                page = f", P{citation.index}" if citation.index is not None else ""
                link_text = f"{source}{page}"
                link_url = citation.file_id or source
                text.append(f"{i}. [{link_text}]({link_url})")

            elif citation.type == "url_citation":
                # Markdown format: 1. [title](url)
                title = citation.title if citation.title else "Web Page"
                url = citation.url
                if url:
                    text.append(f"{i}. [{title}]({url})")
                else:
                    text.append(f"{i}. {title}")
            elif citation.type == "file_path":
                # Markdown format: 1. [filename](file_id)
                source = citation.file_id or "Unknown"
                text.append(f"{i}. [{source}]({source})")
            else:
                # Fallback format with Markdown links when possible
                source = getattr(citation, "filename", getattr(citation, "url", "Unknown"))
                url = getattr(citation, "url", getattr(citation, "file_id", source))
                if url and url != source:
                    text.append(f"{i}. [{source}]({url})")
                else:
                    text.append(f"{i}. {source}")
        
        return Markdown("\n".join(text))
    
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