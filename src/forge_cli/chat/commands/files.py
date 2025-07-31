from __future__ import annotations

"""File operation commands for chat mode."""

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


class UploadCommand(ChatCommand):
    """Upload and process files with real-time progress tracking.
    
    Usage:
    - /upload <file_path> - Upload a file and track processing progress
    - /upload <file_path> --vectorize - Upload file and enable vectorization
    - /upload <file_path> --purpose qa - Upload with specific purpose
    """
    
    name = "upload"
    description = "Upload and process files with progress tracking"
    aliases = ["u", "up"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the upload command with async progress tracking.
        
        Args:
            args: Command arguments containing file path and options
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please specify a file path: /upload <file_path>")
            controller.display.show_status("Example: /upload ./documents/report.pdf")
            return True
            
        # Parse arguments
        arg_parts = args.strip().split()
        file_path_str = arg_parts[0]
        
        # Parse options
        enable_vectorize = "--vectorize" in arg_parts
        purpose = "general"
        if "--purpose" in arg_parts:
            try:
                purpose_idx = arg_parts.index("--purpose")
                if purpose_idx + 1 < len(arg_parts):
                    purpose = arg_parts[purpose_idx + 1]
            except (ValueError, IndexError):
                pass
        
        # Validate file path
        file_path = Path(file_path_str).expanduser().resolve()
        if not file_path.exists():
            controller.display.show_error(f"File not found: {file_path}")
            return True
            
        if not file_path.is_file():
            controller.display.show_error(f"Path is not a file: {file_path}")
            return True
            
        # Start upload process
        controller.display.show_status(f"📤 Starting upload: {file_path.name}")
        
        try:
            # Import SDK functions
            from forge_cli.sdk import async_upload_file, async_check_task_status, async_wait_for_task_completion
            
            # Prepare parse options
            parse_options = None
            if enable_vectorize:
                parse_options = {
                    "abstract": "enable",
                    "summary": "enable", 
                    "keywords": "enable",
                    "vectorize": "enable"
                }
            
            # Upload file
            controller.display.show_status("⏳ Uploading file...")
            file_result = await async_upload_file(
                path=str(file_path),
                purpose=purpose,
                skip_exists=False,
                parse_options=parse_options
            )
            
            controller.display.show_status(f"✅ File uploaded! ID: {file_result.id}")
            controller.display.show_status(f"📋 Task ID: {file_result.task_id}")
            
            # Start progress tracking
            if file_result.task_id:
                await self._track_processing_progress(controller, file_result.task_id, file_path.name)
            else:
                controller.display.show_status("✅ File processing completed immediately")
                
        except Exception as e:
            controller.display.show_error(f"Upload failed: {str(e)}")
            
        return True
    
    async def _track_processing_progress(self, controller: ChatController, task_id: str, filename: str):
        """Track file processing progress with real-time updates.
        
        Args:
            controller: The ChatController instance
            task_id: Task ID to track
            filename: Original filename for display
        """
        try:
            from forge_cli.sdk import async_check_task_status
            import time
            
            controller.display.show_status(f"🔄 Tracking progress for: {filename}")
            
            poll_interval = 2  # Check every 2 seconds
            max_attempts = 150  # 5 minutes max (150 * 2 seconds)
            attempt = 0
            consecutive_errors = 0  # Track consecutive errors
            max_consecutive_errors = 3  # Stop after 3 consecutive errors
            
            last_status = None
            last_progress = None
            
            while attempt < max_attempts:
                try:
                    # Check task status
                    task_status = await async_check_task_status(task_id)
                    consecutive_errors = 0  # Reset error counter on success
                    
                    # Update display if status or progress changed
                    status_changed = task_status.status != last_status
                    progress_changed = task_status.progress != last_progress
                    
                    if status_changed or progress_changed:
                        progress_percent = int(task_status.progress) if task_status.progress else 0
                        status_emoji = self._get_status_emoji(task_status.status)
                        
                        controller.display.show_status(
                            f"{status_emoji} {task_status.status.upper()}: {filename} "
                            f"({progress_percent}%)"
                        )
                        
                        # Show additional details for certain statuses
                        if status_changed:
                            if task_status.status == "parsing":
                                controller.display.show_status("📖 Parsing document content...")
                            elif task_status.status == "vectorizing":
                                controller.display.show_status("🧮 Creating vector embeddings...")
                    
                    last_status = task_status.status
                    last_progress = task_status.progress
                    
                    # Check if processing is complete
                    if task_status.status in ["completed", "failed", "cancelled"]:
                        if task_status.status == "completed":
                            controller.display.show_status(f"✅ Processing completed: {filename}")
                            document_id = task_id.replace('upload-', '')
                            controller.display.show_status(f"📄 Document ID: {document_id}")
                            
                            # Save document ID to conversation state
                            controller.conversation.add_uploaded_document(
                                document_id=document_id,
                                filename=filename
                            )
                            controller.display.show_status(f"💾 Document saved to conversation state")
                        elif task_status.status == "failed":
                            error_msg = "Unknown error"
                            # Try multiple fields for error information
                            if hasattr(task_status, 'failure_reason') and task_status.failure_reason:
                                error_msg = task_status.failure_reason
                            elif hasattr(task_status, 'error_message') and task_status.error_message:
                                error_msg = task_status.error_message
                            elif hasattr(task_status, 'data') and task_status.data and isinstance(task_status.data, dict):
                                error_msg = task_status.data.get('error', error_msg)
                            controller.display.show_error(f"❌ Processing failed: {error_msg}")
                        else:
                            controller.display.show_status(f"⏹️ Processing cancelled: {filename}")
                        return  # Exit method cleanly
                        
                except ConnectionError as e:
                    consecutive_errors += 1
                    controller.display.show_error(f"🌐 Connection error (attempt {consecutive_errors}): {str(e)}")
                    if consecutive_errors >= max_consecutive_errors:
                        controller.display.show_error("❌ Too many connection errors, stopping progress tracking")
                        return
                except TimeoutError as e:
                    consecutive_errors += 1
                    controller.display.show_error(f"⏱️ Request timeout (attempt {consecutive_errors}): {str(e)}")
                    if consecutive_errors >= max_consecutive_errors:
                        controller.display.show_error("❌ Too many timeouts, stopping progress tracking")
                        return
                except Exception as e:
                    consecutive_errors += 1
                    controller.display.show_error(f"❓ Unexpected error (attempt {consecutive_errors}): {str(e)}")
                    if consecutive_errors >= max_consecutive_errors:
                        controller.display.show_error("❌ Too many errors, stopping progress tracking")
                        return
                
                # Wait before next check
                try:
                    await asyncio.sleep(poll_interval)
                except asyncio.CancelledError:
                    controller.display.show_status("⏹️ Progress tracking cancelled")
                    return
                attempt += 1
            
            # Handle timeout
            if attempt >= max_attempts:
                controller.display.show_error(f"⏰ Timeout: Processing took longer than expected")
                controller.display.show_status(f"You can check status manually with task ID: {task_id}")
                
        except asyncio.CancelledError:
            controller.display.show_status("⏹️ Progress tracking cancelled")
            raise  # Re-raise cancellation to handle it properly
        except Exception as e:
            controller.display.show_error(f"Progress tracking initialization failed: {str(e)}")
    
    def _get_status_emoji(self, status: str) -> str:
        """Get appropriate emoji for task status.
        
        Args:
            status: Task status string
            
        Returns:
            Emoji string for the status
        """
        status_emojis = {
            "pending": "⏳",
            "parsing": "📖", 
            "running": "🔄",
            "vectorizing": "🧮",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️",
            "timeout": "⏰",
            # Additional server status values
            "in_progress": "🔄",
            "parse_pending": "⏳"
        }
        return status_emojis.get(status, "🔄")


class DocumentsCommand(ChatCommand):
    """List documents uploaded during this conversation.
    
    Usage:
    - /documents - List all uploaded documents
    - /docs - Alias for documents command
    """
    
    name = "documents"
    description = "List documents uploaded during this conversation"
    aliases = ["docs", "files"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the documents command to list uploaded documents.
        
        Args:
            args: Command arguments (unused for now)
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        uploaded_docs = controller.conversation.get_uploaded_documents()
        
        if not uploaded_docs:
            controller.display.show_status("📂 No documents uploaded in this conversation yet")
            return True
        
        controller.display.show_status(f"📚 {len(uploaded_docs)} document(s) uploaded in this conversation:")
        
        for i, doc in enumerate(uploaded_docs, 1):
            # Format upload time
            try:
                from datetime import datetime
                upload_dt = datetime.fromisoformat(doc["uploaded_at"])
                time_str = upload_dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                time_str = doc.get("uploaded_at", "Unknown time")
            
            controller.display.show_status(
                f"  {i}. 📄 {doc['filename']} (ID: {doc['id']}) - {time_str}"
            )
        
        controller.display.show_status("💡 Use /upload to add more documents")
        return True


class JoinDocumentsCommand(ChatCommand):
    """Join uploaded documents to a vector store collection.
    
    Usage:
    - /join-docs <vector_store_id> - Join all uploaded documents to the vector store
    - /join-docs <vector_store_id> <doc_id1> <doc_id2> ... - Join specific documents
    """
    
    name = "join-docs"
    description = "Join uploaded documents to a vector store collection"
    aliases = ["join", "add-to-collection"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the join-documents command.
        
        Args:
            args: Command arguments containing vector store ID and optional document IDs
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please specify a vector store ID: /join-docs <vector_store_id> [doc_ids...]")
            controller.display.show_status("Example: /join-docs vs_123")
            controller.display.show_status("Example: /join-docs vs_123 doc1 doc2")
            return True
        
        arg_parts = args.strip().split()
        vector_store_id = arg_parts[0]
        
        # Get uploaded documents
        uploaded_docs = controller.conversation.get_uploaded_documents()
        if not uploaded_docs:
            controller.display.show_error("No documents have been uploaded in this conversation")
            controller.display.show_status("Use /upload to upload documents first")
            return True
        
        # Determine which documents to join
        if len(arg_parts) > 1:
            # Specific document IDs provided
            requested_doc_ids = arg_parts[1:]
            documents_to_join = []
            
            for doc_id in requested_doc_ids:
                doc = next((d for d in uploaded_docs if d["id"] == doc_id), None)
                if doc:
                    documents_to_join.append(doc)
                else:
                    controller.display.show_error(f"Document ID not found: {doc_id}")
            
            if not documents_to_join:
                controller.display.show_error("No valid document IDs provided")
                return True
        else:
            # Join all uploaded documents
            documents_to_join = uploaded_docs
        
        controller.display.show_status(f"🔗 Joining {len(documents_to_join)} document(s) to vector store: {vector_store_id}")
        
        try:
            # Import SDK function
            from forge_cli.sdk import async_join_files_to_vectorstore
            
            # Extract document IDs
            file_ids = [doc["id"] for doc in documents_to_join]
            
            # Join documents to vector store
            result = await async_join_files_to_vectorstore(
                vector_store_id=vector_store_id,
                file_ids=file_ids
            )
            
            if result:
                controller.display.show_status(f"✅ Successfully joined {len(documents_to_join)} document(s) to vector store")
                
                # Update conversation state to include this vector store
                current_vs_ids = controller.conversation.get_current_vector_store_ids()
                if vector_store_id not in current_vs_ids:
                    current_vs_ids.append(vector_store_id)
                    controller.conversation.set_vector_store_ids(current_vs_ids)
                    controller.display.show_status(f"📚 Vector store {vector_store_id} added to conversation")
                
                # Show joined documents
                for doc in documents_to_join:
                    controller.display.show_status(f"  📄 {doc['filename']} (ID: {doc['id']})")
                    
            else:
                controller.display.show_error("Failed to join documents to vector store")
                
        except Exception as e:
            controller.display.show_error(f"Error joining documents: {str(e)}")
        
        return True


class NewCollectionCommand(ChatCommand):
    """Create a new vector store collection.
    
    Usage:
    - /new-collection name="Collection Name" desc="Description here"
    - /new-collection name="Research Papers" desc="AI research collection" model="text-embedding-v4"
    - /new-collection name="Support FAQ" desc="Customer support docs" metadata="domain:support,priority:high"
    """
    
    name = "new-collection"
    description = "Create a new vector store collection"
    aliases = ["new-vs", "create-collection", "create-vs"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the new-collection command.
        
        Args:
            args: Command arguments in key=value format (name=<name> desc=<desc> [model=<model>] [metadata=<key:value,key:value>])
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide collection parameters: /new-collection name=\"Collection Name\" desc=\"Description\"")
            controller.display.show_status("Example: /new-collection name=\"My Documents\" desc=\"Personal document collection\"")
            controller.display.show_status("Optional: model=\"text-embedding-v4\" metadata=\"domain:research,priority:high\"")
            return True
        
        # Parse parameters in key=value format
        try:
            params = self._parse_parameters(args)
        except ValueError as e:
            controller.display.show_error(f"Parameter parsing error: {str(e)}")
            controller.display.show_status("Use format: name=\"Collection Name\" desc=\"Description\"")
            return True
        
        # Validate required parameters
        if "name" not in params:
            controller.display.show_error("Missing required parameter: name")
            controller.display.show_status("Example: /new-collection name=\"My Collection\" desc=\"Description\"")
            return True
            
        if "desc" not in params:
            controller.display.show_error("Missing required parameter: desc")
            controller.display.show_status("Example: /new-collection name=\"My Collection\" desc=\"Description\"")
            return True
        
        name = params["name"]
        description = params["desc"]
        model = params.get("model")  # Optional
        custom_id = params.get("id")  # Optional custom ID
        
        # Parse metadata if provided
        metadata = None
        if "metadata" in params:
            try:
                metadata = self._parse_metadata(params["metadata"])
            except ValueError as e:
                controller.display.show_error(f"Metadata parsing error: {str(e)}")
                controller.display.show_status("Use format: metadata=\"key:value,key2:value2\"")
                return True
        
        controller.display.show_status(f"🏗️ Creating vector store collection: {name}")
        controller.display.show_status(f"📝 Description: {description}")
        
        if model:
            controller.display.show_status(f"🤖 Model: {model}")
        if metadata:
            controller.display.show_status(f"🏷️ Metadata: {metadata}")
        
        try:
            # Import SDK function
            from forge_cli.sdk import async_create_vectorstore
            
            # Create the vector store
            result = await async_create_vectorstore(
                name=name,
                description=description,
                custom_id=custom_id,
                metadata=metadata
            )
            
            if result:
                controller.display.show_status(f"✅ Collection created successfully!")
                controller.display.show_status(f"🆔 Collection ID: {result.id}")
                controller.display.show_status(f"📅 Created at: {self._format_timestamp(result.created_at)}")
                
                # Add to conversation's vector store IDs for easy reference
                current_vs_ids = controller.conversation.get_current_vector_store_ids()
                if result.id not in current_vs_ids:
                    current_vs_ids.append(result.id)
                    controller.conversation.set_vector_store_ids(current_vs_ids)
                    controller.display.show_status(f"📚 Collection added to conversation for file search")
                
                # Show usage tips
                controller.display.show_status("💡 Next steps:")
                controller.display.show_status(f"  • Upload documents: /upload path/to/file.pdf")
                controller.display.show_status(f"  • Join documents: /join-docs {result.id}")
                controller.display.show_status(f"  • Enable file search: /enable-file-search")
                
            else:
                controller.display.show_error("❌ Failed to create collection - no result returned")
                
        except Exception as e:
            controller.display.show_error(f"❌ Failed to create collection: {str(e)}")
            controller.display.show_status("💡 Make sure the server is running and accessible")
        
        return True
    
    def _parse_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in key=value format.
        
        Supports both quoted and unquoted values:
        - name="My Collection" desc="Long description here"
        - name=simple desc=basic
        
        Args:
            args: Argument string to parse
            
        Returns:
            Dictionary of parsed parameters
            
        Raises:
            ValueError: If parsing fails
        """
        params = {}
        import re
        
        # Regular expression to match key=value pairs with optional quotes
        # Supports: key="quoted value" or key=unquoted_value
        pattern = r'(\w+)=(?:"([^"]*)"|([^\s]+))'
        
        matches = re.findall(pattern, args)
        
        if not matches:
            raise ValueError("No valid key=value parameters found")
        
        for match in matches:
            key = match[0]
            # Use quoted value if present, otherwise use unquoted value
            value = match[1] if match[1] else match[2]
            params[key] = value
        
        return params
    
    def _parse_metadata(self, metadata_str: str) -> dict[str, str]:
        """Parse metadata string in format: key:value,key2:value2
        
        Args:
            metadata_str: Metadata string to parse
            
        Returns:
            Dictionary of metadata key-value pairs
            
        Raises:
            ValueError: If parsing fails
        """
        metadata = {}
        
        # Split by comma to get individual key:value pairs
        pairs = [pair.strip() for pair in metadata_str.split(',')]
        
        for pair in pairs:
            if ':' not in pair:
                raise ValueError(f"Invalid metadata format: '{pair}'. Use 'key:value' format")
            
            key, value = pair.split(':', 1)  # Split only on first colon
            key = key.strip()
            value = value.strip()
            
            if not key or not value:
                raise ValueError(f"Empty key or value in metadata: '{pair}'")
            
            metadata[key] = value
        
        return metadata
    
    def _format_timestamp(self, timestamp: int) -> str:
        """Format Unix timestamp to readable string.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted timestamp string
        """
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            return str(timestamp)


class ShowDocumentCommand(ChatCommand):
    """Show detailed information about a specific document.
    
    Usage:
    - /show-doc <document-id>
    - /doc file_abc123
    """
    
    name = "show-doc"
    description = "Show detailed information about a specific document"
    aliases = ["doc", "document", "file-info"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-document command.
        
        Args:
            args: Command arguments containing the document ID
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a document ID: /show-doc <document-id>")
            controller.display.show_status("Example: /show-doc file_abc123")
            return True
        
        document_id = args.strip()
        
        controller.display.show_status(f"🔍 Fetching document information: {document_id}")
        
        try:
            # Import SDK function
            from forge_cli.sdk import async_fetch_file
            
            # Fetch the document
            document = await async_fetch_file(document_id)
            
            if document is None:
                controller.display.show_error(f"❌ Document not found: {document_id}")
                controller.display.show_status("💡 Make sure the document ID is correct and the document exists")
                return True
            
            # Display document information
            controller.display.show_status("📄 Document Information")
            controller.display.show_status("=" * 50)
            
            # Basic information
            controller.display.show_status(f"🆔 Document ID: {document.id}")
            controller.display.show_status(f"📁 Filename: {document.filename}")
            controller.display.show_status(f"📏 Size: {self._format_file_size(document.bytes)}")
            
            if document.content_type:
                controller.display.show_status(f"📋 Content Type: {document.content_type}")
            
            controller.display.show_status(f"🎯 Purpose: {document.purpose}")
            
            # Status information
            if document.status:
                status_emoji = self._get_status_emoji(document.status)
                controller.display.show_status(f"{status_emoji} Status: {document.status}")
            
            # Timestamps
            created_str = self._format_datetime(document.created_at)
            controller.display.show_status(f"📅 Created: {created_str}")
            
            if document.updated_at:
                updated_str = self._format_datetime(document.updated_at)
                controller.display.show_status(f"🔄 Updated: {updated_str}")
            
            # Processing information
            if document.task_id:
                controller.display.show_status(f"⚙️ Task ID: {document.task_id}")
            
            if document.processing_error_message:
                controller.display.show_error(f"❌ Processing Error: {document.processing_error_message}")
            
            # Additional details
            if document.custom_id:
                controller.display.show_status(f"🏷️ Custom ID: {document.custom_id}")
            
            if document.md5:
                controller.display.show_status(f"🔐 MD5 Hash: {document.md5}")
            
            # Metadata
            if document.metadata:
                controller.display.show_status("📋 Metadata:")
                for key, value in document.metadata.items():
                    controller.display.show_status(f"  • {key}: {value}")
            
            # Usage tips
            controller.display.show_status("")
            controller.display.show_status("💡 Related commands:")
            controller.display.show_status(f"  • Join to collection: /join-docs <collection_id> {document.id}")
            controller.display.show_status("  • List collections: /tools")
            controller.display.show_status("  • View uploaded documents: /documents")
            
        except Exception as e:
            controller.display.show_error(f"❌ Failed to fetch document information: {str(e)}")
            controller.display.show_status("💡 Check the document ID and server connectivity")
        
        return True
    
    def _format_file_size(self, bytes_size: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            Formatted size string
        """
        if bytes_size < 1024:
            return f"{bytes_size} bytes"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    
    def _format_datetime(self, dt) -> str:
        """Format datetime to readable string.
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted datetime string
        """
        try:
            if hasattr(dt, 'strftime'):
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return str(dt)
        except:
            return str(dt)
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for document status.
        
        Args:
            status: Document status
            
        Returns:
            Appropriate emoji
        """
        status_emojis = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️",
            "uploaded": "📤",
            "ready": "✅"
        }
        return status_emojis.get(status.lower(), "📄")


class ShowCollectionCommand(ChatCommand):
    """Show detailed information about a specific collection.
    
    Usage:
    - /show-collection <collection-id>
    - /collection vs_abc123
    - /vs vs_abc123 --summary (to include summary if available)
    """
    
    name = "show-collection"
    description = "Show detailed information about a specific collection"
    aliases = ["collection", "vs", "show-vs"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the show-collection command.
        
        Args:
            args: Command arguments containing the collection ID and optional flags
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        if not args.strip():
            controller.display.show_error("Please provide a collection ID: /show-collection <collection-id>")
            controller.display.show_status("Example: /show-collection vs_abc123")
            controller.display.show_status("Optional: --summary to include collection summary")
            return True
        
        # Parse arguments
        arg_parts = args.strip().split()
        collection_id = arg_parts[0]
        show_summary = "--summary" in arg_parts
        
        controller.display.show_status(f"🔍 Fetching collection information: {collection_id}")
        
        try:
            # Import SDK functions
            from forge_cli.sdk import async_get_vectorstore, async_get_vectorstore_summary
            
            # Fetch the collection
            collection = await async_get_vectorstore(collection_id)
            
            if collection is None:
                controller.display.show_error(f"❌ Collection not found: {collection_id}")
                controller.display.show_status("💡 Make sure the collection ID is correct and exists")
                return True
            
            # Display collection information
            controller.display.show_status("📚 Collection Information")
            controller.display.show_status("=" * 50)
            
            # Basic information
            controller.display.show_status(f"🆔 Collection ID: {collection.id}")
            controller.display.show_status(f"📝 Name: {collection.name}")
            
            if collection.description:
                controller.display.show_status(f"📄 Description: {collection.description}")
            
            # Statistics
            file_counts = collection.file_counts
            controller.display.show_status(f"📊 File Statistics:")
            controller.display.show_status(f"  📁 Total Files: {file_counts.total}")
            
            if file_counts.completed > 0:
                controller.display.show_status(f"  ✅ Completed: {file_counts.completed}")
            if file_counts.in_progress > 0:
                controller.display.show_status(f"  🔄 In Progress: {file_counts.in_progress}")
            if file_counts.failed > 0:
                controller.display.show_status(f"  ❌ Failed: {file_counts.failed}")
            if file_counts.cancelled > 0:
                controller.display.show_status(f"  ⏹️ Cancelled: {file_counts.cancelled}")
            
            # File list (with smart truncation)
            if collection.file_ids:
                controller.display.show_status(f"📋 Files in Collection:")
                if len(collection.file_ids) <= 10:
                    for i, file_id in enumerate(collection.file_ids, 1):
                        controller.display.show_status(f"  {i}. {file_id}")
                else:
                    # Show first 8 and last 2
                    for i, file_id in enumerate(collection.file_ids[:8], 1):
                        controller.display.show_status(f"  {i}. {file_id}")
                    controller.display.show_status(f"  ... ({len(collection.file_ids) - 10} more files)")
                    for i, file_id in enumerate(collection.file_ids[-2:], len(collection.file_ids) - 1):
                        controller.display.show_status(f"  {i}. {file_id}")
            
            # Size information
            if collection.bytes:
                size_str = self._format_file_size(collection.bytes)
                controller.display.show_status(f"💾 Total Size: {size_str}")
            
            # Creation date
            created_str = self._format_datetime(collection.created_at)
            controller.display.show_status(f"📅 Created: {created_str}")
            
            # Metadata
            if collection.metadata:
                controller.display.show_status("🏷️ Metadata:")
                for key, value in collection.metadata.items():
                    if isinstance(value, (list, dict)):
                        controller.display.show_status(f"  • {key}: {len(value)} items")
                    else:
                        controller.display.show_status(f"  • {key}: {value}")
            
            # Collection summary (if requested)
            if show_summary:
                controller.display.show_status("")
                controller.display.show_status("📋 Fetching collection summary...")
                try:
                    summary = await async_get_vectorstore_summary(collection_id)
                    if summary:
                        controller.display.show_status(f"📝 Summary:")
                        controller.display.show_status(f"   {summary.summary_text}")
                        controller.display.show_status(f"🤖 Generated by: {summary.model_used}")
                    else:
                        controller.display.show_status("ℹ️ No summary available for this collection")
                except Exception as e:
                    controller.display.show_error(f"❌ Failed to fetch summary: {str(e)}")
            
            # Usage tips
            controller.display.show_status("")
            controller.display.show_status("💡 Related commands:")
            controller.display.show_status(f"  • Add documents: /join-docs {collection.id} <doc_id1> <doc_id2>")
            controller.display.show_status(f"  • Search collection: (enable file search and ask questions)")
            controller.display.show_status(f"  • Show summary: /show-collection {collection.id} --summary")
            controller.display.show_status("  • List all collections: /tools")
            
        except Exception as e:
            controller.display.show_error(f"❌ Failed to fetch collection information: {str(e)}")
            controller.display.show_status("💡 Check the collection ID and server connectivity")
        
        return True
    
    def _format_file_size(self, bytes_size: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            Formatted size string
        """
        if bytes_size < 1024:
            return f"{bytes_size} bytes"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    
    def _format_datetime(self, dt) -> str:
        """Format datetime to readable string.
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted datetime string
        """
        try:
            if hasattr(dt, 'strftime'):
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return str(dt)
        except:
            return str(dt)