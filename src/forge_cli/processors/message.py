"""Processor for message output items."""

from typing import Any

from forge_cli.common.types import ProcessedMessage
from forge_cli.response._types.annotations import AnnotationList
from forge_cli.response._types.response_output_message import ResponseOutputMessage

from ..response._types import (
    AnnotationFileCitation,
    AnnotationURLCitation,
    ResponseOutputText,  # ResponseOutputMessage is imported directly
)
from .base import OutputProcessor


class MessageProcessor(OutputProcessor):
    """Processes message output items containing the final response."""

    def can_process(self, item_type: str) -> bool:
        """Check if this processor can handle the item type."""
        return item_type == "message"

    def process(self, item: ResponseOutputMessage) -> ProcessedMessage | None:
        """Extract text and annotations from message content."""
        if item.role != "assistant":
            return None

        full_text = ""
        all_annotations = []

        # Find the first text content item
        for content_item in item.content or []:
            if isinstance(content_item, ResponseOutputText):
                full_text = content_item.text or ""
                all_annotations = content_item.annotations or []
                break

        return ProcessedMessage(
            type="message",
            text=full_text,
            annotations=all_annotations,  # type: ignore # AnnotationList vs List[AnnotationUnion]
            id=item.id or "",
            status=item.status or "completed",
        )

    def format(self, processed: ProcessedMessage) -> str:
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

    def _process_annotations(self, annotations: AnnotationList) -> list[dict[str, Any]]:
        """Process annotations into citation format."""
        citations = []

        for i, ann in enumerate(annotations):
            # Handle typed annotation
            if isinstance(ann, AnnotationFileCitation):
                filename = ann.filename or "Unknown"

                # Try to get filename from nested file object
                if not filename and hasattr(ann, "file") and ann.file:
                    filename = ann.file.filename or "Unknown"

                # Convert 0-based page index to 1-based
                page_index = ann.index or "N/A"
                if isinstance(page_index, int):
                    page_index = page_index + 1

                citations.append(
                    {
                        "number": i + 1,
                        "type": "file",
                        "page": page_index,
                        "filename": filename,
                        "file_id": ann.file_id or "",
                        "url": None,
                        "title": filename,
                    }
                )

            elif isinstance(ann, AnnotationURLCitation):
                url = ann.url or ""
                title = ann.title or ""
                snippet = ann.snippet or ""

                # Create display name
                display_name = title
                if not display_name:
                    display_name = url[:50] + "..." if len(url) > 50 else url

                citations.append(
                    {
                        "number": i + 1,
                        "type": "url",
                        "page": "N/A",
                        "filename": display_name,
                        "file_id": None,
                        "url": url,
                        "title": title,
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
