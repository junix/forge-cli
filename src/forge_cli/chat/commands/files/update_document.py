"""Update document command."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class UpdateDocumentCommand(ChatCommand):
    """Update an existing document's metadata and properties.

    Usage:
    - /update-document <document_id> --title="New Title" --author="New Author"
    - /update-document doc_123 --title="Updated Document Title"
    - /update-document doc_123 --author="John Doe" --is-favorite=true
    - /update-document doc_123 --metadata="category:research,priority:high"
    - /update-document doc_123 --notes="Important finding,Follow up needed"
    - /update-document doc_123 --bookmarks="10,25,50" --highlights="key insight,important quote"
    - /update-document doc_123 --read-progress=0.75 --owner="user123"
    """

    name = "update-document"
    description = "Update an existing document's metadata and properties"
    aliases = ["update-doc", "modify-document", "modify-doc", "edit-document", "edit-doc"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the update-document command.

        Args:
            args: Command arguments containing document ID and update parameters
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            self._show_usage(controller)
            return True

        try:
            # Parse document ID and parameters
            document_id, params = self._parse_args(args)
            
            if not document_id:
                controller.display.show_error("Document ID is required")
                self._show_usage(controller)
                return True

            if not params:
                controller.display.show_error("At least one update parameter is required")
                self._show_usage(controller)
                return True

            # Import SDK function
            from forge_cli.sdk.files import async_update_document

            controller.display.show_status(f"🔄 Updating document: {document_id}")

            # Prepare update request
            update_data = {}
            
            # Handle basic fields
            if "title" in params:
                update_data["title"] = params["title"]
                controller.display.show_status(f"  📝 Title: {params['title']}")
            
            if "author" in params:
                update_data["author"] = params["author"]
                controller.display.show_status(f"  👤 Author: {params['author']}")
            
            if "owner" in params:
                update_data["owner"] = params["owner"]
                controller.display.show_status(f"  👑 Owner: {params['owner']}")

            # Handle boolean fields
            if "is_favorite" in params:
                is_favorite = params["is_favorite"].lower() in ("true", "1", "yes", "on")
                update_data["is_favorite"] = is_favorite
                controller.display.show_status(f"  ⭐ Favorite: {is_favorite}")

            # Handle numeric fields
            if "read_progress" in params:
                try:
                    progress = float(params["read_progress"])
                    if 0.0 <= progress <= 1.0:
                        update_data["read_progress"] = progress
                        controller.display.show_status(f"  📊 Read progress: {progress:.1%}")
                    else:
                        controller.display.show_error("read_progress must be between 0.0 and 1.0")
                        return True
                except ValueError:
                    controller.display.show_error("read_progress must be a number")
                    return True

            # Handle list fields
            if "bookmarks" in params:
                bookmarks = self._parse_int_list(params["bookmarks"])
                if bookmarks is not None:
                    update_data["bookmarks"] = bookmarks
                    controller.display.show_status(f"  🔖 Bookmarks: {len(bookmarks)} bookmark(s)")

            if "highlights" in params:
                highlights = self._parse_string_list(params["highlights"])
                if highlights:
                    update_data["highlights"] = highlights
                    controller.display.show_status(f"  🖍️  Highlights: {len(highlights)} highlight(s)")

            if "notes" in params:
                notes = self._parse_string_list(params["notes"])
                if notes:
                    update_data["notes"] = notes
                    controller.display.show_status(f"  📝 Notes: {len(notes)} note(s)")

            if "related_docs" in params:
                related_docs = self._parse_string_list(params["related_docs"])
                if related_docs:
                    update_data["related_docs"] = related_docs
                    controller.display.show_status(f"  🔗 Related docs: {len(related_docs)} document(s)")

            if "permissions" in params:
                permissions = self._parse_string_list(params["permissions"])
                if permissions:
                    update_data["permissions"] = permissions
                    controller.display.show_status(f"  🔐 Permissions: {len(permissions)} permission(s)")

            if "vector_store_ids" in params:
                vector_store_ids = self._parse_string_list(params["vector_store_ids"])
                if vector_store_ids:
                    update_data["vector_store_ids"] = vector_store_ids
                    controller.display.show_status(f"  📦 Vector stores: {len(vector_store_ids)} collection(s)")

            # Handle metadata
            if "metadata" in params:
                metadata = self._parse_metadata(params["metadata"])
                if metadata:
                    update_data["metadata"] = metadata
                    controller.display.show_status(f"  🏷️  Metadata: {len(metadata)} key(s)")

            # Perform the update
            result = await async_update_document(document_id, **update_data)

            if result:
                controller.display.show_status("✅ Document updated successfully!")
                controller.display.show_status(f"📄 ID: {result.get('id', document_id)}")
                if "title" in update_data:
                    controller.display.show_status(f"📝 Title: {update_data['title']}")
                controller.display.show_status(f"🕒 Updated: {result.get('updated_at', 'now')}")
            else:
                controller.display.show_error("❌ Failed to update document")

        except ValueError as e:
            controller.display.show_error(f"❌ Invalid arguments: {str(e)}")
            self._show_usage(controller)
        except Exception as e:
            controller.display.show_error(f"❌ Failed to update document: {str(e)}")

        return True

    def _parse_args(self, args: str) -> tuple[str, dict[str, str]]:
        """Parse command arguments.
        
        Args:
            args: Raw argument string
            
        Returns:
            Tuple of (document_id, parameters_dict)
            
        Raises:
            ValueError: If parsing fails
        """
        # Split to get document ID first
        parts = args.strip().split(maxsplit=1)
        if not parts:
            raise ValueError("Document ID is required")
            
        document_id = parts[0]
        
        # Parse parameters if present
        params = {}
        if len(parts) > 1:
            params = self._parse_parameters(parts[1])
            
        return document_id, params

    def _parse_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in --key=value format.
        
        Supports both quoted and unquoted values:
        - --title="My Document" --author="John Doe"
        - --title=simple --author=basic
        - --bookmarks="1,2,3" --is-favorite=true
        
        Args:
            args: Argument string to parse
            
        Returns:
            Dictionary of parsed parameters
            
        Raises:
            ValueError: If parsing fails
        """
        params = {}
        
        # Regular expression to match --key=value pairs with optional quotes
        # Supports: --key="quoted value" or --key=unquoted_value
        pattern = r'--(\w+(?:[-_]\w+)*)=(?:"([^"]*)"|([^\s]+))'
        
        matches = re.findall(pattern, args)
        
        if not matches:
            raise ValueError("No valid --key=value parameters found")
        
        for match in matches:
            key = match[0].replace('-', '_')  # Convert kebab-case to snake_case
            value = match[1] if match[1] else match[2]  # Quoted or unquoted value
            params[key] = value
            
        return params

    def _parse_metadata(self, metadata_str: str) -> dict[str, str]:
        """Parse metadata string in key:value,key:value format.
        
        Args:
            metadata_str: Metadata string to parse
            
        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}
        
        if not metadata_str.strip():
            return metadata
            
        # Split by comma and parse key:value pairs
        pairs = [pair.strip() for pair in metadata_str.split(",") if pair.strip()]
        
        for pair in pairs:
            if ":" in pair:
                key, value = pair.split(":", 1)
                metadata[key.strip()] = value.strip()
                
        return metadata

    def _parse_string_list(self, list_str: str) -> list[str]:
        """Parse comma-separated string list.
        
        Args:
            list_str: Comma-separated string
            
        Returns:
            List of strings
        """
        if not list_str.strip():
            return []
            
        return [item.strip() for item in list_str.split(",") if item.strip()]

    def _parse_int_list(self, list_str: str) -> list[int] | None:
        """Parse comma-separated integer list.
        
        Args:
            list_str: Comma-separated integer string
            
        Returns:
            List of integers, or None if parsing fails
        """
        if not list_str.strip():
            return []
            
        try:
            return [int(item.strip()) for item in list_str.split(",") if item.strip()]
        except ValueError:
            return None

    def _show_usage(self, controller: ChatController) -> None:
        """Show command usage examples."""
        controller.display.show_status("📋 Usage: /update-document <document_id> [options]")
        controller.display.show_status("")
        controller.display.show_status("📝 Basic Updates:")
        controller.display.show_status('  /update-document doc_123 --title="New Document Title"')
        controller.display.show_status('  /update-document doc_123 --author="John Doe"')
        controller.display.show_status("  /update-document doc_123 --is-favorite=true")
        controller.display.show_status("")
        controller.display.show_status("📊 Progress & Bookmarks:")
        controller.display.show_status("  /update-document doc_123 --read-progress=0.75")
        controller.display.show_status('  /update-document doc_123 --bookmarks="10,25,50"')
        controller.display.show_status("")
        controller.display.show_status("📝 Notes & Highlights:")
        controller.display.show_status('  /update-document doc_123 --notes="Important finding,Follow up needed"')
        controller.display.show_status('  /update-document doc_123 --highlights="key insight,important quote"')
        controller.display.show_status("")
        controller.display.show_status("🏷️  Metadata & Relations:")
        controller.display.show_status('  /update-document doc_123 --metadata="category:research,priority:high"')
        controller.display.show_status('  /update-document doc_123 --related-docs="doc_456,doc_789"')
        controller.display.show_status("")
        controller.display.show_status("🔄 Combined Updates:")
        controller.display.show_status('  /update-document doc_123 --title="Research Paper" --author="Dr. Smith" --is-favorite=true')
