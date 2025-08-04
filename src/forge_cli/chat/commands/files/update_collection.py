"""Update collection command."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class UpdateCollectionCommand(ChatCommand):
    """Update an existing vector store collection.

    Usage:
    - /update-collection <collection_id> --name="New Name" --description="New Description"
    - /update-collection vs_123 --name="Updated Collection"
    - /update-collection vs_123 --description="Updated description" --metadata="key1:value1,key2:value2"
    - /update-collection vs_123 --add-files="file1,file2" --remove-files="file3,file4"
    - /update-collection vs_123 --expires-after=3600
    """

    name = "update-collection"
    description = "Update an existing vector store collection"
    aliases = ["update-vs", "modify-collection", "modify-vs", "edit-collection"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the update-collection command.

        Args:
            args: Command arguments containing collection ID and update parameters
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            self._show_usage(controller)
            return True

        try:
            # Parse collection ID and parameters
            collection_id, params = self._parse_args(args)
            
            if not collection_id:
                controller.display.show_error("Collection ID is required")
                self._show_usage(controller)
                return True

            if not params:
                controller.display.show_error("At least one update parameter is required")
                self._show_usage(controller)
                return True

            # Import SDK function
            from forge_cli.sdk.vectorstore import async_modify_vectorstore

            controller.display.show_status(f"🔄 Updating collection: {collection_id}")

            # Prepare update request
            update_data = {}
            
            # Handle basic fields
            if "name" in params:
                update_data["name"] = params["name"]
                controller.display.show_status(f"  📝 Name: {params['name']}")
            
            if "description" in params:
                update_data["description"] = params["description"]
                controller.display.show_status(f"  📄 Description: {params['description']}")
            
            if "expires_after" in params:
                try:
                    update_data["expires_after"] = int(params["expires_after"])
                    controller.display.show_status(f"  ⏰ Expires after: {params['expires_after']} seconds")
                except ValueError:
                    controller.display.show_error("expires_after must be a number")
                    return True

            # Handle metadata
            if "metadata" in params:
                metadata = self._parse_metadata(params["metadata"])
                if metadata:
                    update_data["metadata"] = metadata
                    controller.display.show_status(f"  🏷️  Metadata: {len(metadata)} key(s)")

            # Handle file operations
            if "add_files" in params:
                file_ids = [f.strip() for f in params["add_files"].split(",") if f.strip()]
                if file_ids:
                    update_data["join_file_ids"] = file_ids
                    controller.display.show_status(f"  ➕ Adding files: {len(file_ids)} file(s)")

            if "remove_files" in params:
                file_ids = [f.strip() for f in params["remove_files"].split(",") if f.strip()]
                if file_ids:
                    update_data["left_file_ids"] = file_ids
                    controller.display.show_status(f"  ➖ Removing files: {len(file_ids)} file(s)")

            # Perform the update
            result = await async_modify_vectorstore(collection_id, **update_data)

            if result:
                controller.display.show_status("✅ Collection updated successfully!")
                controller.display.show_status(f"📦 Name: {result.name}")
                controller.display.show_status(f"🆔 ID: {result.id}")
                if result.description:
                    controller.display.show_status(f"📄 Description: {result.description}")
                
                # Show file count if available
                if hasattr(result, 'metadata') and result.metadata and 'files' in result.metadata:
                    file_count = len(result.metadata['files'])
                    controller.display.show_status(f"📁 Files: {file_count}")
            else:
                controller.display.show_error("❌ Failed to update collection")

        except ValueError as e:
            controller.display.show_error(f"❌ Invalid arguments: {str(e)}")
            self._show_usage(controller)
        except Exception as e:
            controller.display.show_error(f"❌ Failed to update collection: {str(e)}")

        return True

    def _parse_args(self, args: str) -> tuple[str, dict[str, str]]:
        """Parse command arguments.
        
        Args:
            args: Raw argument string
            
        Returns:
            Tuple of (collection_id, parameters_dict)
            
        Raises:
            ValueError: If parsing fails
        """
        # Split to get collection ID first
        parts = args.strip().split(maxsplit=1)
        if not parts:
            raise ValueError("Collection ID is required")
            
        collection_id = parts[0]
        
        # Parse parameters if present
        params = {}
        if len(parts) > 1:
            params = self._parse_parameters(parts[1])
            
        return collection_id, params

    def _parse_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in --key=value format.
        
        Supports both quoted and unquoted values:
        - --name="My Collection" --description="Long description here"
        - --name=simple --description=basic
        - --add-files="file1,file2" --remove-files="file3"
        
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

    def _show_usage(self, controller: ChatController) -> None:
        """Show command usage examples."""
        controller.display.show_status("📋 Usage: /update-collection <collection_id> [options]")
        controller.display.show_status("")
        controller.display.show_status("📝 Basic Updates:")
        controller.display.show_status('  /update-collection vs_123 --name="New Collection Name"')
        controller.display.show_status('  /update-collection vs_123 --description="Updated description"')
        controller.display.show_status("  /update-collection vs_123 --expires-after=3600")
        controller.display.show_status("")
        controller.display.show_status("🏷️  Metadata Updates:")
        controller.display.show_status('  /update-collection vs_123 --metadata="domain:research,priority:high"')
        controller.display.show_status("")
        controller.display.show_status("📁 File Management:")
        controller.display.show_status('  /update-collection vs_123 --add-files="file1,file2,file3"')
        controller.display.show_status('  /update-collection vs_123 --remove-files="file4,file5"')
        controller.display.show_status("")
        controller.display.show_status("🔄 Combined Updates:")
        controller.display.show_status('  /update-collection vs_123 --name="Research Papers" --add-files="doc1,doc2"')
