"""Processor for message output items."""

from typing import Dict, Any, Optional, Union, List

from .base import OutputProcessor
from ..response._types import (
    ResponseStreamEvent,
    ResponseOutputMessage,
    ResponseOutputText,
    Annotation,
    AnnotationFileCitation,
    AnnotationURLCitation,
)


class MessageProcessor(OutputProcessor):
    """Processes message output items containing the final response."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "message"

    def process(
        self, item: Union[Dict[str, Any], ResponseStreamEvent]
    ) -> Optional[Dict[str, Any]]:
        """Extract text and annotations from message content."""
        # Handle typed event
        if isinstance(item, ResponseOutputMessage):
            if item.role != "assistant":
                return None
                
            full_text = ""
            all_annotations = []
            
            for content_item in item.content or []:
                if isinstance(content_item, ResponseOutputText) or (hasattr(content_item, 'type') and content_item.type == "output_text"):
                    full_text = content_item.text or ""
                    all_annotations = content_item.annotations or []
                    break
            
            return {
                "type": "message",
                "text": full_text,
                "annotations": all_annotations,
                "id": item.id or "",
                "status": item.status or "completed",
            }
        
        # Handle dict for backward compatibility
        elif isinstance(item, dict):
            if item.get("role") != "assistant":
                return None

            full_text = ""
            all_annotations = []

            content_list = item.get("content", [])
            for content_item in content_list:
                if content_item.get("type") == "output_text":
                    full_text = content_item.get("text", "")
                    all_annotations = content_item.get("annotations", [])
                    break

            return {
                "type": "message",
                "text": full_text,
                "annotations": all_annotations,
                "id": item.get("id", ""),
                "status": item.get("status", "completed"),
            }
        
        return None

    def format(self, processed: Dict[str, Any]) -> str:
        """Format message with text and citations."""
        text = processed.get("text", "")
        annotations = processed.get("annotations", [])

        parts = []

        # Add main text
        if text:
            parts.append(text)

        # Add citations if present
        if annotations:
            citations = self._process_annotations(annotations)
            if citations:
                parts.append("")  # Empty line
                parts.append(self._format_citations_table(citations))

        return "\n".join(parts)

    def _process_annotations(self, annotations: List[Union[Dict[str, Any], Annotation]]) -> List[Dict[str, Any]]:
        """Process annotations into citation format."""
        citations = []

        for i, ann in enumerate(annotations):
            # Handle typed annotation
            if isinstance(ann, AnnotationFileCitation):
                filename = ann.filename or "Unknown"
                
                # Try to get filename from nested file object
                if not filename and hasattr(ann, 'file') and ann.file:
                    filename = ann.file.filename or "Unknown"
                
                # Convert 0-based page index to 1-based
                page_index = ann.index or "N/A"
                if isinstance(page_index, int):
                    page_index = page_index + 1
                
                citations.append({
                    "number": i + 1,
                    "type": "file",
                    "page": page_index,
                    "filename": filename,
                    "file_id": ann.file_id or "",
                    "url": None,
                    "title": filename,
                })
                
            elif isinstance(ann, AnnotationURLCitation):
                url = ann.url or ""
                title = ann.title or ""
                snippet = ann.snippet or ""
                
                # Create display name
                display_name = title
                if not display_name:
                    display_name = url[:50] + "..." if len(url) > 50 else url
                
                citations.append({
                    "number": i + 1,
                    "type": "url",
                    "page": "N/A",
                    "filename": display_name,
                    "file_id": None,
                    "url": url,
                    "title": title,
                })
            
            # Handle dict annotation for backward compatibility
            elif isinstance(ann, dict):
                citation_type = ann.get("type")

                if citation_type == "file_citation":
                    file_id = ann.get("file_id", "")
                    filename = ann.get("filename", "")

                    # Try to get filename from nested file object
                    if not filename and "file" in ann:
                        filename = ann["file"].get("filename", "")

                    if not filename:
                        filename = "Unknown"

                    # Convert 0-based page index to 1-based
                    page_index = ann.get("index", "N/A")
                    if isinstance(page_index, int):
                        page_index = page_index + 1

                    citations.append(
                        {
                            "number": i + 1,
                            "type": "file",
                            "page": page_index,
                            "filename": filename,
                            "file_id": file_id,
                            "url": None,
                            "title": filename,
                        }
                    )

                elif citation_type == "url_citation":
                    url = ann.get("url", "")
                    title = ann.get("title", "")
                    snippet = ann.get("snippet", "")

                # Create display name
                display_name = title
                if not display_name and url:
                    try:
                        from urllib.parse import urlparse

                        parsed = urlparse(url)
                        display_name = parsed.netloc or url
                    except:
                        display_name = url

                if not display_name:
                    display_name = "Web Source"

                citations.append(
                    {
                        "number": i + 1,
                        "type": "web",
                        "page": "Web",
                        "filename": display_name,
                        "file_id": None,
                        "url": url,
                        "title": title,
                        "snippet": snippet,
                    }
                )

        return citations

    def _format_citations_table(self, citations: list[dict[str, str | int]]) -> str:
        """Format citations as a markdown table."""
        if not citations:
            return ""

        # Check citation types
        has_file = any(c.get("type") == "file" for c in citations)
        has_web = any(c.get("type") == "web" for c in citations)

        lines = ["### 📚 References", ""]

        if has_file and has_web:
            # Mixed citations
            lines.extend(["| Citation | Source | Location | ID/URL |", "|----------|--------|----------|--------|"])
            for cite in citations:
                if cite.get("type") == "web":
                    url_display = cite.get("url", "")
                    if len(url_display) > 50:
                        url_display = url_display[:47] + "..."
                    lines.append(f"| [{cite['number']}] | {cite['filename']} | Web | {url_display} |")
                else:
                    lines.append(
                        f"| [{cite['number']}] | {cite['filename']} | p.{cite['page']} | {cite.get('file_id', 'N/A')} |"
                    )
        elif has_web:
            # Web citations only
            lines.extend(["| Citation | Title | URL |", "|----------|-------|-----|"])
            for cite in citations:
                url_display = cite.get("url", "")
                if len(url_display) > 60:
                    url_display = url_display[:57] + "..."
                lines.append(f"| [{cite['number']}] | {cite['filename']} | {url_display} |")
        else:
            # File citations only
            lines.extend(["| Citation | Document | Page | File ID |", "|----------|----------|------|---------|"])
            for cite in citations:
                lines.append(
                    f"| [{cite['number']}] | {cite['filename']} | {cite['page']} | {cite.get('file_id', 'N/A')} |"
                )

        return "\n".join(lines)
