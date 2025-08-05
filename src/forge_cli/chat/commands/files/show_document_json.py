"""Show document JSON command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowDocumentJsonCommand(ChatCommand):
    """Show raw JSON response from document API.

    Usage:
    - /show-doc-json <doc-id> - Show raw JSON response
    - /doc-json <doc-id> - Short alias
    """

    name = "show-doc-json"
    description = "Show raw JSON response from document API"
    aliases = ["doc-json", "json-doc", "raw-doc"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-doc-json command.

        Args:
            args: Command arguments containing the document ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a document ID: /show-doc-json <document-id>")
            controller.display.show_status_rich("Example: /show-doc-json doc_abc123")
            return True

        document_id = args.strip()

        controller.display.show_status_rich(f"🔍 Fetching raw JSON for document: {document_id}")

        try:
            # Import SDK internal functions to get raw response
            import json

            from forge_cli.sdk.config import BASE_URL
            from forge_cli.sdk.http_client import async_make_request

            # Make raw API call
            url = f"{BASE_URL}/v1/files/{document_id}/content"
            status_code, response_data = await async_make_request("GET", url)

            if status_code == 200 and isinstance(response_data, dict):
                # Display raw JSON response
                controller.display.show_status_rich("📄 Raw JSON Response:")
                controller.display.show_status_rich("=" * 60)

                # Pretty print JSON with indentation
                json_str = json.dumps(response_data, indent=2, ensure_ascii=False)

                # Display JSON in chunks to avoid overwhelming the terminal
                lines = json_str.split("\n")
                for line in lines:
                    controller.display.show_status_rich(line)

                controller.display.show_status_rich("=" * 60)
                controller.display.show_status_rich("✅ JSON response displayed successfully")

            elif status_code == 404:
                controller.display.show_error(f"❌ Document not found: {document_id}")
                controller.display.show_status_rich("💡 Make sure the document ID is correct and exists")
            else:
                controller.display.show_error(f"❌ API returned status {status_code}")
                if isinstance(response_data, dict):
                    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
                    controller.display.show_status_rich("Error response:")
                    controller.display.show_status_rich(json_str)
                else:
                    controller.display.show_status_rich(f"Response: {response_data}")

        except Exception as e:
            controller.display.show_error(f"❌ Failed to fetch document JSON: {str(e)}")
            controller.display.show_status_rich("💡 Check the document ID and server connectivity")

        return True
