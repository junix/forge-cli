"""Show pages command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..base import ChatCommand
from ..utils import has_json_flag, parse_flag_parameters

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowPagesCommand(ChatCommand):
    """Show pages from a document.
    
    Usage:
        /show-pages <doc-id> [start] [end]                          (simple format, formatted output)
        /show-pages --id=<doc-id> --start=<n> --end=<m> --json     (flag format with JSON output)
    
    Examples:
        /show-pages doc_abc123                  # Show all pages
        /show-pages doc_abc123 1 5              # Show pages 1-5
        /show-pages --id=doc_abc123 --json      # All pages as JSON
        /show-pages --id=doc_abc123 --start=1 --end=5 --json
    """
    
    name = "show-pages"
    description = "Show pages from a document"
    aliases = ["pages"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-pages command.

        Args:
            args: Command arguments containing document ID and optional page range
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a document ID")
            controller.display.show_status("Usage:")
            controller.display.show_status("  /show-pages <doc-id> [start] [end]                          (formatted output)")
            controller.display.show_status("  /show-pages --id=<doc-id> --start=<n> --end=<m> --json     (JSON output)")
            return True

        # Parse arguments
        doc_id, start_page, end_page, json_output = self._parse_args(args)

        if not doc_id:
            controller.display.show_error("Document ID is required")
            return True

        # Show status (unless JSON output is requested)
        if not json_output:
            if start_page is not None and end_page is not None:
                controller.display.show_status_rich(f"📄 Fetching pages {start_page}-{end_page} from document: {doc_id}")
            else:
                controller.display.show_status_rich(f"📄 Fetching all pages from document: {doc_id}")

        try:
            # Import SDK functions
            from forge_cli.sdk.config import BASE_URL
            from forge_cli.sdk.http_client import async_make_request

            # Build query parameters
            params = {}
            if start_page is not None:
                params["start_page"] = start_page
            if end_page is not None:
                params["end_page"] = end_page

            # Make API call
            url = f"{BASE_URL}/v1/files/{doc_id}/pages"
            status_code, response_data = await async_make_request("GET", url, params=params)

            if status_code == 200 and isinstance(response_data, dict):
                if json_output:
                    # Output as JSON
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                else:
                    # Format and display the pages
                    self._display_pages(response_data, controller)
                    controller.display.show_status_rich("✅ Pages displayed successfully")

            elif status_code == 404:
                if json_output:
                    print(json.dumps({"error": f"Document not found: {doc_id}"}, indent=2))
                else:
                    controller.display.show_error(f"❌ Document not found: {doc_id}")
            else:
                error_msg = f"API returned status {status_code}"
                if json_output:
                    print(json.dumps({"error": error_msg, "details": response_data}, indent=2))
                else:
                    controller.display.show_error(f"❌ {error_msg}")

        except Exception as e:
            error_msg = f"Failed to fetch pages: {str(e)}"
            if json_output:
                print(json.dumps({"error": error_msg}, indent=2))
            else:
                controller.display.show_error(f"❌ {error_msg}")

        return True

    def _parse_args(self, args: str) -> tuple[str | None, int | None, int | None, bool]:
        """Parse command arguments.

        Supports two formats:
        1. Simple: "doc_id [start] [end]"
        2. Flag-based: "--id=doc_id --start=n --end=m --json"

        Args:
            args: Raw argument string

        Returns:
            Tuple of (doc_id, start_page, end_page, json_output)
        """
        args = args.strip()

        # Check if this looks like flag-based format (starts with --)
        if args.startswith("--"):
            params = parse_flag_parameters(args)
            doc_id = params.get("id", "").strip()
            
            # Parse page numbers
            start_page = None
            end_page = None
            
            if "start" in params:
                try:
                    start_page = int(params["start"])
                except ValueError:
                    pass
            
            if "end" in params:
                try:
                    end_page = int(params["end"])
                except ValueError:
                    pass
            
            json_output = has_json_flag(params)
            return doc_id, start_page, end_page, json_output
        else:
            # Simple format: doc_id [start] [end]
            parts = args.split()
            doc_id = parts[0] if parts else None
            
            start_page = None
            end_page = None
            
            if len(parts) > 1:
                try:
                    start_page = int(parts[1])
                except ValueError:
                    pass
            
            if len(parts) > 2:
                try:
                    end_page = int(parts[2])
                except ValueError:
                    pass
            
            return doc_id, start_page, end_page, False

    def _display_pages(self, pages_data: dict, controller: ChatController) -> None:
        """Display formatted page information.

        Args:
            pages_data: Pages data from API
            controller: Chat controller for display
        """
        controller.display.show_status_rich("📄 Document Pages:")
        controller.display.show_status_rich("=" * 60)

        pages = pages_data.get("pages", pages_data.get("data", []))
        
        if not pages:
            controller.display.show_status_rich("No pages found.")
            return

        for page in pages:
            if isinstance(page, dict):
                page_num = page.get("page_number", page.get("page", "?"))
                content = page.get("content", page.get("text", ""))
                
                controller.display.show_status_rich(f"\n--- Page {page_num} ---")
                
                # Truncate long content
                if len(content) > 500:
                    controller.display.show_status_rich(content[:500] + "...\n[Content truncated]")
                else:
                    controller.display.show_status_rich(content)

        controller.display.show_status_rich("=" * 60)
