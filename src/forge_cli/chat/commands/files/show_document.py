"""Show document command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..base import ChatCommand
from ..utils import has_json_flag, parse_flag_parameters

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowDocumentCommand(ChatCommand):
    """Show detailed information about a specific document.
    
    Usage:
        /show-doc <doc-id>              (simple format, formatted output)
        /show-doc --id=<doc-id> --json  (flag format with JSON output)
    
    Examples:
        /show-doc doc_abc123
        /show-doc --id=doc_abc123 --json
    """
    
    name = "show-doc"
    description = "Show detailed document information"
    aliases = ["doc", "document"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-doc command.

        Args:
            args: Command arguments containing the document ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a document ID")
            controller.display.show_status("Usage:")
            controller.display.show_status("  /show-doc <doc-id>              (formatted output)")
            controller.display.show_status("  /show-doc --id=<doc-id> --json  (JSON output)")
            return True

        # Parse arguments
        document_id, json_output = self._parse_args(args)

        if not document_id:
            controller.display.show_error("Document ID is required")
            return True

        # Show status (unless JSON output is requested)
        if not json_output:
            controller.display.show_status_rich(f"🔍 Fetching document: {document_id}")

        try:
            # Import SDK functions
            from forge_cli.sdk.config import BASE_URL
            from forge_cli.sdk.http_client import async_make_request

            # Make API call
            url = f"{BASE_URL}/v1/files/{document_id}/content"
            status_code, response_data = await async_make_request("GET", url)

            if status_code == 200 and isinstance(response_data, dict):
                if json_output:
                    # Output as JSON
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                else:
                    # Format and display the document information
                    self._display_document_info(response_data, controller)
                    controller.display.show_status_rich("✅ Document information displayed successfully")

            elif status_code == 404:
                if json_output:
                    print(json.dumps({"error": f"Document not found: {document_id}"}, indent=2))
                else:
                    controller.display.show_error(f"❌ Document not found: {document_id}")
                    controller.display.show_status_rich("💡 Make sure the document ID is correct and exists")
            else:
                error_msg = f"API returned status {status_code}"
                if json_output:
                    print(json.dumps({"error": error_msg, "details": response_data}, indent=2))
                else:
                    controller.display.show_error(f"❌ {error_msg}")
                    if isinstance(response_data, dict):
                        json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
                        controller.display.show_status_rich("Error response:")
                        controller.display.show_status_rich(json_str)

        except Exception as e:
            error_msg = f"Failed to fetch document: {str(e)}"
            if json_output:
                print(json.dumps({"error": error_msg}, indent=2))
            else:
                controller.display.show_error(f"❌ {error_msg}")
                controller.display.show_status_rich("💡 Check the document ID and server connectivity")

        return True

    def _parse_args(self, args: str) -> tuple[str, bool]:
        """Parse command arguments.

        Supports two formats:
        1. Simple: "doc_id" (no JSON output)
        2. Flag-based: "--id=doc_id --json"

        Args:
            args: Raw argument string

        Returns:
            Tuple of (document_id, json_output)
        """
        args = args.strip()

        # Check if this looks like flag-based format (starts with --)
        if args.startswith("--"):
            params = parse_flag_parameters(args)
            document_id = params.get("id", "").strip()
            json_output = has_json_flag(params)
            return document_id, json_output
        else:
            # Simple format: just the document ID
            document_id = args.strip()
            json_output = False
            return document_id, json_output

    def _display_document_info(self, doc_data: dict, controller: ChatController) -> None:
        """Display formatted document information.

        Args:
            doc_data: Document data from API
            controller: Chat controller for display
        """
        controller.display.show_status_rich("📄 Document Information:")
        controller.display.show_status_rich("=" * 60)

        # Display key fields
        if "id" in doc_data:
            controller.display.show_status_rich(f"ID: {doc_data['id']}")
        
        if "filename" in doc_data:
            controller.display.show_status_rich(f"Filename: {doc_data['filename']}")
        
        if "size" in doc_data:
            size_mb = doc_data["size"] / (1024 * 1024)
            controller.display.show_status_rich(f"Size: {size_mb:.2f} MB")
        
        if "created_at" in doc_data:
            controller.display.show_status_rich(f"Created: {doc_data['created_at']}")
        
        if "metadata" in doc_data and doc_data["metadata"]:
            controller.display.show_status_rich("\nMetadata:")
            for key, value in doc_data["metadata"].items():
                controller.display.show_status_rich(f"  {key}: {value}")

        controller.display.show_status_rich("=" * 60)
