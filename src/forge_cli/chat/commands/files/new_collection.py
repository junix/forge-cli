"""New collection command."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class NewCollectionCommand(ChatCommand):
    """Create a new vector store collection.

    Usage:
    - /new-collection name="Collection Name" desc="Description here"
    - /new-vs name="My Collection" desc="For storing documents"
    """

    name = "new-collection"
    description = "Create a new vector store collection"
    aliases = ["new-vs", "create-collection", "create-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the new-collection command.

        Args:
            args: Command arguments containing collection parameters
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error(
                'Please provide collection parameters: /new-collection name="Collection Name" desc="Description"'
            )
            controller.display.show_status(
                'Example: /new-collection name="My Documents" desc="Personal document collection"'
            )
            return True

        # Parse name and description from args
        name = None
        description = None

        # Simple parsing for name="..." and desc="..." format
        name_match = re.search(r'name="([^"]*)"', args)
        desc_match = re.search(r'desc="([^"]*)"', args)

        if name_match:
            name = name_match.group(1)
        if desc_match:
            description = desc_match.group(1)

        if not name:
            controller.display.show_error("Collection name is required")
            controller.display.show_status('Use format: name="Collection Name" desc="Description"')
            return True

        if not description:
            description = f"Collection created via CLI: {name}"
            controller.display.show_status('Example: /new-collection name="My Collection" desc="Description"')

        try:
            # Import SDK function
            from forge_cli.sdk import async_create_vectorstore

            controller.display.show_status(f"🔨 Creating collection: {name}")

            # Create the collection
            collection = await async_create_vectorstore(name=name, description=description)

            controller.display.show_status("✅ Collection created successfully!")
            controller.display.show_status(f"📦 Name: {collection.name}")
            controller.display.show_status(f"🆔 ID: {collection.id}")
            if collection.description:
                controller.display.show_status(f"📄 Description: {collection.description}")

            # Ask if user wants to add it to active collections
            controller.display.show_status(f"💡 Use '/use-collection {collection.id}' to add it to active collections")
            controller.display.show_status("💡 Use '/upload' to add documents to this collection")

        except Exception as e:
            controller.display.show_error(f"❌ Failed to create collection: {str(e)}")

        return True
