"""Collection management commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class ShowCollectionsCommand(ChatCommand):
    """Show information about all known collections from config and conversation state.

    Usage:
    - /show-collections - Show all known collections
    - /collections - Alias for show-collections command
    - /list-collections - Another alias
    """

    name = "show-collections"
    description = "Show information about all known collections"
    aliases = ["collections", "list-collections", "ls-collections"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collections command to list all known collections.

        Args:
            args: Command arguments (unused for now)
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        # Get all unique collection IDs from both sources
        config_ids = set(controller.config.vec_ids) if controller.config.vec_ids else set()
        conversation_ids = set(controller.conversation.get_current_vector_store_ids())
        all_collection_ids = config_ids | conversation_ids

        if not all_collection_ids:
            controller.display.show_status("📂 No collections configured")
            controller.display.show_status(
                "💡 Use /new-collection to create a collection or /vectorstore to configure existing ones"
            )
            return True

        controller.display.show_status(f"📚 Found {len(all_collection_ids)} collection(s):")
        controller.display.show_status("=" * 60)

        # Track collections by status
        active_collections = []
        config_only_collections = []
        conversation_only_collections = []
        failed_collections = []

        # Fetch information for each collection
        for collection_id in sorted(all_collection_ids):
            collection_info = await self._get_collection_info(collection_id, controller)

            # Determine collection status
            in_config = collection_id in config_ids
            in_conversation = collection_id in conversation_ids

            if collection_info:
                if in_config and in_conversation:
                    active_collections.append((collection_id, collection_info, "Active"))
                elif in_config:
                    config_only_collections.append((collection_id, collection_info, "Config Only"))
                else:
                    conversation_only_collections.append((collection_id, collection_info, "Conversation Only"))
            else:
                failed_collections.append((collection_id, None, "Inaccessible"))

        # Display collections by category
        self._display_collection_category("🟢 Active Collections", active_collections, controller)
        self._display_collection_category("🔵 Config Collections", config_only_collections, controller)
        self._display_collection_category("🟡 Conversation Collections", conversation_only_collections, controller)
        self._display_collection_category("🔴 Inaccessible Collections", failed_collections, controller)

        # Summary and tips
        total_accessible = len(active_collections) + len(config_only_collections) + len(conversation_only_collections)
        controller.display.show_status(
            f"\n📊 Summary: {total_accessible} accessible, {len(failed_collections)} inaccessible"
        )

        if active_collections:
            controller.display.show_status("💡 Active collections are available for file search")

        controller.display.show_status("💡 Use /show-collection <id> for detailed information")
        controller.display.show_status("💡 Use /vectorstore to manage active collections")

        return True

    async def _get_collection_info(self, collection_id: str, controller: ChatController) -> dict | None:
        """Get collection information from the API.

        Args:
            collection_id: The collection ID to fetch
            controller: The ChatController instance

        Returns:
            Dictionary with collection info or None if failed
        """
        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore

            collection = await async_get_vectorstore(collection_id)
            if collection:
                # Handle file_counts properly - it's a FileCounts Pydantic model
                file_counts = getattr(collection, "file_counts", None)
                if file_counts:
                    # Convert FileCounts Pydantic model to dict
                    if hasattr(file_counts, "model_dump"):
                        # Pydantic v2
                        file_counts_dict = file_counts.model_dump()
                    elif hasattr(file_counts, "dict"):
                        # Pydantic v1
                        file_counts_dict = file_counts.dict()
                    elif isinstance(file_counts, dict):
                        # Already a dict
                        file_counts_dict = file_counts
                    else:
                        # Fallback: access as attributes (FileCounts model)
                        file_counts_dict = {
                            "total": getattr(file_counts, "total", 0),
                            "completed": getattr(file_counts, "completed", 0),
                            "in_progress": getattr(file_counts, "in_progress", 0),
                            "failed": getattr(file_counts, "failed", 0),
                            "cancelled": getattr(file_counts, "cancelled", 0),
                        }
                else:
                    file_counts_dict = {"total": 0, "completed": 0, "in_progress": 0, "failed": 0, "cancelled": 0}

                return {
                    "id": collection.id,
                    "name": getattr(collection, "name", "Unknown"),
                    "description": getattr(collection, "description", ""),
                    "file_counts": file_counts_dict,
                    "created_at": getattr(collection, "created_at", None),
                    "bytes": getattr(collection, "bytes", 0),
                }
            return None
        except Exception as e:
            # Log the error for debugging but don't fail the command
            controller.display.show_status(f"    ⚠️ Error accessing collection {collection_id}: {str(e)}")
            return None

    def _display_collection_category(self, title: str, collections: list, controller: ChatController) -> None:
        """Display a category of collections.

        Args:
            title: Category title
            collections: List of (id, info, status) tuples
            controller: The ChatController instance
        """
        if not collections:
            return

        controller.display.show_status(f"\n{title}:")

        for collection_id, info, status in collections:
            if info:
                name = info.get("name", "Unknown")
                file_counts = info.get("file_counts", {})
                total_files = file_counts.get("total", 0)
                completed_files = file_counts.get("completed", 0)

                # Format file count info
                if total_files > 0:
                    file_info = f"{completed_files}/{total_files} files"
                    if completed_files < total_files:
                        file_info += f" ({total_files - completed_files} processing)"
                else:
                    file_info = "No files"

                controller.display.show_status(f"  📦 {name} ({collection_id})")
                controller.display.show_status(f"      📊 {file_info}")

                if info.get("description"):
                    desc = info["description"][:60] + "..." if len(info["description"]) > 60 else info["description"]
                    controller.display.show_status(f"      📄 {desc}")
            else:
                controller.display.show_status(f"  ❌ {collection_id} - {status}")


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
        import re

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


class DeleteCollectionCommand(ChatCommand):
    """Delete a vector store collection.

    Usage:
    - /del-collection <collection-id> - Delete a collection by ID
    - /delete-vs vs_123 - Short alias
    """

    name = "del-collection"
    description = "Delete a vector store collection"
    aliases = ["delete-collection", "delete-vs", "del-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the delete-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /del-collection <collection-id>")
            controller.display.show_status("Example: /del-collection vs_abc123")
            return True

        collection_id = args.strip().split()[0]

        # Confirm deletion
        controller.display.show_status(f"⚠️ Are you sure you want to delete collection: {collection_id}?")
        controller.display.show_status("This action cannot be undone and will delete all documents in the collection.")
        controller.display.show_status("Type 'yes' to confirm or anything else to cancel:")

        # Note: In a real implementation, you'd want to get user confirmation
        # For now, we'll skip the confirmation step
        controller.display.show_status("⚠️ Deletion confirmation not implemented in CLI mode")
        controller.display.show_status("Use the web interface for safe collection deletion")

        return True


class ShowCollectionCommand(ChatCommand):
    """Show detailed information about a specific collection.

    Usage:
    - /show-collection <collection-id> - Show collection details
    - /collection vs_123 - Short alias
    """

    name = "show-collection"
    description = "Show detailed collection information"
    aliases = ["collection", "vs-info"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /show-collection <collection-id>")
            controller.display.show_status("Example: /show-collection vs_abc123")
            return True

        collection_id = args.strip().split()[0]

        try:
            from forge_cli.sdk.vectorstore import async_get_vectorstore

            controller.display.show_status(f"🔍 Fetching collection: {collection_id}")

            collection = await async_get_vectorstore(collection_id)

            if not collection:
                controller.display.show_error(f"❌ Collection not found: {collection_id}")
                return True

            # Display collection information
            controller.display.show_status("=" * 50)
            controller.display.show_status(f"📦 Collection: {collection.name}")
            controller.display.show_status(f"🆔 ID: {collection.id}")

            if hasattr(collection, "description") and collection.description:
                controller.display.show_status(f"📄 Description: {collection.description}")

            # Handle file counts
            if hasattr(collection, "file_counts") and collection.file_counts:
                file_counts = collection.file_counts
                if hasattr(file_counts, "model_dump"):
                    counts = file_counts.model_dump()
                elif hasattr(file_counts, "dict"):
                    counts = file_counts.dict()
                else:
                    counts = {
                        "total": getattr(file_counts, "total", 0),
                        "completed": getattr(file_counts, "completed", 0),
                        "in_progress": getattr(file_counts, "in_progress", 0),
                        "failed": getattr(file_counts, "failed", 0),
                        "cancelled": getattr(file_counts, "cancelled", 0),
                    }

                controller.display.show_status("📊 File Statistics:")
                controller.display.show_status(f"  Total: {counts.get('total', 0)}")
                controller.display.show_status(f"  Completed: {counts.get('completed', 0)}")
                controller.display.show_status(f"  In Progress: {counts.get('in_progress', 0)}")
                controller.display.show_status(f"  Failed: {counts.get('failed', 0)}")
                controller.display.show_status(f"  Cancelled: {counts.get('cancelled', 0)}")

            if hasattr(collection, "created_at") and collection.created_at:
                controller.display.show_status(f"📅 Created: {collection.created_at}")

            if hasattr(collection, "bytes") and collection.bytes:
                size_mb = collection.bytes / (1024 * 1024)
                controller.display.show_status(f"💾 Size: {size_mb:.2f} MB")

            controller.display.show_status("=" * 50)

        except Exception as e:
            controller.display.show_error(f"❌ Error fetching collection: {str(e)}")

        return True


class UseCollectionCommand(ChatCommand):
    """Add a collection to active vector stores for file search.

    Usage:
    - /use-collection <collection-id> - Add collection to active vector stores
    - /use-vs vs_123 - Short alias
    """

    name = "use-collection"
    description = "Add a collection to active vector stores for file search"
    aliases = ["use-vs", "add-collection", "add-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the use-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /use-collection <collection-id>")
            controller.display.show_status("Example: /use-collection vs_abc123")
            controller.display.show_status("This will add the collection to active vector stores for file search")
            return True

        # Parse collection ID
        collection_id = args.strip().split()[0]

        # Optional: Validate the collection exists
        controller.display.show_status(f"🔍 Checking collection: {collection_id}")

        try:
            # Import SDK function
            from forge_cli.sdk import async_get_vectorstore

            # Check if collection exists
            collection = await async_get_vectorstore(collection_id)

            if collection is None:
                controller.display.show_error(f"❌ Collection not found: {collection_id}")
                controller.display.show_status("💡 Make sure the collection ID is correct")
                controller.display.show_status("Use /vectorstore to see available collections")
                return True

            # Add to config.vec_ids if not already present
            if collection_id not in controller.config.vec_ids:
                controller.config.vec_ids.append(collection_id)
                controller.display.show_status(f"✅ Collection '{collection_id}' added to active vector stores")

                # Also update conversation's vector store IDs for consistency
                current_vs_ids = controller.conversation.get_current_vector_store_ids()
                if collection_id not in current_vs_ids:
                    current_vs_ids.append(collection_id)
                    controller.conversation.set_vector_store_ids(current_vs_ids)

                # Show collection info
                controller.display.show_status(f"📚 Collection: {collection.name}")
                if collection.description:
                    controller.display.show_status(f"📄 Description: {collection.description}")

                # Show current status
                controller.display.show_status(f"📊 Active collections: {len(controller.config.vec_ids)}")

                # Show helpful next steps
                if not controller.conversation.file_search_enabled:
                    controller.display.show_status("💡 Use /enable-file-search to start searching documents")
                else:
                    controller.display.show_status("✅ File search is enabled - you can now search this collection!")

            else:
                controller.display.show_status(f"ℹ️ Collection '{collection_id}' is already in active vector stores")
                controller.display.show_status(f"📊 Active collections: {len(controller.config.vec_ids)}")

                # Show all active collections
                if len(controller.config.vec_ids) > 1:
                    controller.display.show_status("📚 Active collections:")
                    for idx, vs_id in enumerate(controller.config.vec_ids, 1):
                        controller.display.show_status(f"  {idx}. {vs_id}")

        except Exception as e:
            controller.display.show_error(f"❌ Error adding collection: {str(e)}")
            controller.display.show_status("💡 Check the collection ID and server connectivity")

        return True


class UnuseCollectionCommand(ChatCommand):
    """Remove a collection from active vector stores for file search.

    Usage:
    - /unuse-collection <collection-id> - Remove collection from active vector stores
    - /unuse-vs vs_123 - Short alias
    """

    name = "unuse-collection"
    description = "Remove a collection from active vector stores for file search"
    aliases = ["unuse-vs", "remove-collection", "remove-vs"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the unuse-collection command.

        Args:
            args: Command arguments containing the collection ID
            controller: The ChatController instance

        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /unuse-collection <collection-id>")
            controller.display.show_status("Example: /unuse-collection vs_abc123")
            controller.display.show_status("This will remove the collection from active vector stores")
            return True

        # Parse collection ID
        collection_id = args.strip().split()[0]

        # Check if collection is currently in use
        if collection_id not in controller.config.vec_ids:
            controller.display.show_status(f"ℹ️ Collection '{collection_id}' is not in active vector stores")

            # Show current active collections if any
            if controller.config.vec_ids:
                controller.display.show_status("📚 Currently active collections:")
                for idx, vs_id in enumerate(controller.config.vec_ids, 1):
                    controller.display.show_status(f"  {idx}. {vs_id}")
            else:
                controller.display.show_status("📂 No collections are currently active")
                controller.display.show_status("💡 Use /use-collection to add collections")

            return True

        # Optional: Get collection info before removing (for better user feedback)
        collection_name = collection_id  # Default to ID
        try:
            from forge_cli.sdk import async_get_vectorstore

            collection = await async_get_vectorstore(collection_id)
            if collection and hasattr(collection, "name"):
                collection_name = collection.name
        except Exception:
            # If we can't get collection info, that's okay - just use the ID
            pass

        # Remove from config.vec_ids
        controller.config.vec_ids.remove(collection_id)
        controller.display.show_status(
            f"✅ Collection '{collection_name}' ({collection_id}) removed from active vector stores"
        )

        # Also remove from conversation's vector store IDs for consistency
        current_vs_ids = controller.conversation.get_current_vector_store_ids()
        if collection_id in current_vs_ids:
            current_vs_ids.remove(collection_id)
            controller.conversation.set_vector_store_ids(current_vs_ids)

        # Show updated status
        remaining_count = len(controller.config.vec_ids)
        controller.display.show_status(f"📊 Active collections: {remaining_count}")

        if remaining_count > 0:
            controller.display.show_status("📚 Remaining active collections:")
            for idx, vs_id in enumerate(controller.config.vec_ids, 1):
                controller.display.show_status(f"  {idx}. {vs_id}")
        else:
            controller.display.show_status("📂 No collections are currently active")
            controller.display.show_status("💡 File search will not work without active collections")

            # Auto-disable file search if no collections left
            if controller.conversation.file_search_enabled:
                controller.conversation.disable_file_search()
                controller.display.show_status("🔍 Auto-disabled file search (no active collections)")

        # Show helpful next steps
        controller.display.show_status("💡 Use /show-collections to see all available collections")
        controller.display.show_status("💡 Use /use-collection <id> to add collections back")

        return True
