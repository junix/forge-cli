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


class FileHelpCommand(ChatCommand):
    """Comprehensive help system for file management commands.
    
    Usage:
    - /file-help - Show general overview of all file commands
    - /file-help <command-name> - Show detailed help for specific command
    """
    
    name = "file-help"
    description = "Show detailed help for file management commands"
    aliases = ["fhelp", "file-usage", "help-files"]
    
    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the file help command.
        
        Args:
            args: Optional command name to get specific help
            controller: The ChatController instance
            
        Returns:
            True to continue the chat session
        """
        command_name = args.strip().lower() if args.strip() else None
        
        if not command_name:
            await self._show_general_help(controller)
        else:
            await self._show_specific_help(command_name, controller)
        
        return True
    
    async def _show_general_help(self, controller: ChatController) -> None:
        """Show general overview of all file management commands."""
        controller.display.show_status("📚 File Management Commands - Overview")
        controller.display.show_status("=" * 60)
        controller.display.show_status("")
        
        commands_info = [
            ("📤 /upload", "Upload files with progress tracking", "Essential"),
            ("📋 /documents", "List uploaded documents in conversation", "Basic"),
            ("🔗 /join-docs", "Join documents to collections", "Advanced"),
            ("🏗️ /new-collection", "Create new vector store collections", "Advanced"),
            ("📄 /show-doc", "Show detailed document information", "Utility"),
            ("📚 /show-collection", "Show detailed collection information", "Utility"),
            ("❓ /file-help", "This help system", "Help")
        ]
        
        controller.display.show_status("Available Commands:")
        for cmd, desc, level in commands_info:
            controller.display.show_status(f"  {cmd:<18} - {desc} ({level})")
        
        controller.display.show_status("")
        controller.display.show_status("💡 Quick Start Workflow:")
        controller.display.show_status("  1. Upload documents: /upload path/to/file.pdf")
        controller.display.show_status("  2. Create collection: /new-collection name=\"My Docs\" desc=\"My collection\"")
        controller.display.show_status("  3. Join documents: /join-docs <collection-id>")
        controller.display.show_status("  4. Enable file search: /enable-file-search")
        controller.display.show_status("  5. Ask questions about your documents!")
        
        controller.display.show_status("")
        controller.display.show_status("📖 For detailed help on any command:")
        controller.display.show_status("  /file-help <command-name>")
        controller.display.show_status("  Example: /file-help upload")
    
    async def _show_specific_help(self, command_name: str, controller: ChatController) -> None:
        """Show detailed help for a specific command."""
        # Map command names and aliases to help methods
        help_methods = {
            "upload": self._show_upload_help,
            "u": self._show_upload_help,
            "up": self._show_upload_help,
            
            "documents": self._show_documents_help,
            "docs": self._show_documents_help,
            "files": self._show_documents_help,
            
            "join-docs": self._show_join_docs_help,
            "join": self._show_join_docs_help,
            "add-to-collection": self._show_join_docs_help,
            
            "new-collection": self._show_new_collection_help,
            "new-vs": self._show_new_collection_help,
            "create-collection": self._show_new_collection_help,
            "create-vs": self._show_new_collection_help,
            
            "show-doc": self._show_show_doc_help,
            "doc": self._show_show_doc_help,
            "document": self._show_show_doc_help,
            "file-info": self._show_show_doc_help,
            
            "show-collection": self._show_show_collection_help,
            "collection": self._show_show_collection_help,
            "vs": self._show_show_collection_help,
            "show-vs": self._show_show_collection_help,
            
            "file-help": self._show_help_help,
            "fhelp": self._show_help_help,
            "file-usage": self._show_help_help,
            "help-files": self._show_help_help,
        }
        
        help_method = help_methods.get(command_name)
        if help_method:
            await help_method(controller)
        else:
            controller.display.show_error(f"❌ No help available for command: {command_name}")
            controller.display.show_status("Available commands: upload, documents, join-docs, new-collection, show-doc, show-collection, file-help")
    
    async def _show_upload_help(self, controller: ChatController) -> None:
        """Show detailed help for upload command."""
        controller.display.show_status("📤 Upload Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Upload and process files with real-time progress tracking")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Basic Usage:")
        controller.display.show_status("  /upload <file_path>")
        controller.display.show_status("  /u <file_path>           # Short alias")
        controller.display.show_status("  /up <file_path>          # Alternative alias")
        controller.display.show_status("")
        
        controller.display.show_status("🎛️ Advanced Options:")
        controller.display.show_status("  /upload <file_path> --vectorize    # Enable full text processing")
        controller.display.show_status("  /upload <file_path> --purpose qa   # Set specific purpose")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /upload ./documents/report.pdf")
        controller.display.show_status("  /upload ~/Desktop/research.docx --vectorize")
        controller.display.show_status("  /upload /path/to/manual.pdf --purpose documentation")
        controller.display.show_status("")
        
        controller.display.show_status("✨ Features:")
        controller.display.show_status("  • Real-time progress tracking with status updates")
        controller.display.show_status("  • Automatic document ID persistence")
        controller.display.show_status("  • Support for various file formats (PDF, DOCX, TXT, etc.)")
        controller.display.show_status("  • Intelligent error handling and recovery")
        controller.display.show_status("  • Path expansion (~/Documents works)")
        controller.display.show_status("")
        
        controller.display.show_status("⚠️ Important Notes:")
        controller.display.show_status("  • File must exist and be readable")
        controller.display.show_status("  • Processing may take time for large files")
        controller.display.show_status("  • Document IDs are saved automatically for easy reference")
        controller.display.show_status("  • Use --vectorize for better search capabilities")
    
    async def _show_documents_help(self, controller: ChatController) -> None:
        """Show detailed help for documents command."""
        controller.display.show_status("📋 Documents Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  List all documents uploaded during this conversation")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Usage:")
        controller.display.show_status("  /documents               # List all uploaded documents")
        controller.display.show_status("  /docs                   # Short alias")
        controller.display.show_status("  /files                  # Alternative alias")
        controller.display.show_status("")
        
        controller.display.show_status("📊 Information Displayed:")
        controller.display.show_status("  • Document filename")
        controller.display.show_status("  • Document ID (for use with other commands)")
        controller.display.show_status("  • Upload timestamp")
        controller.display.show_status("  • Total count of documents")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Example Output:")
        controller.display.show_status("  📚 2 document(s) uploaded in this conversation:")
        controller.display.show_status("    1. 📄 report.pdf (ID: doc_abc123) - 2024-01-15 14:30:25")
        controller.display.show_status("    2. 📄 manual.docx (ID: doc_def456) - 2024-01-15 14:35:12")
        controller.display.show_status("")
        
        controller.display.show_status("🔗 Related Commands:")
        controller.display.show_status("  • /upload <file>          # Upload more documents")
        controller.display.show_status("  • /show-doc <doc-id>      # View detailed document info")
        controller.display.show_status("  • /join-docs <vs-id>      # Add documents to collections")
    
    async def _show_join_docs_help(self, controller: ChatController) -> None:
        """Show detailed help for join-docs command."""
        controller.display.show_status("🔗 Join Documents Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Join uploaded documents to vector store collections for search")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Basic Usage:")
        controller.display.show_status("  /join-docs <collection_id>                  # Join all documents")
        controller.display.show_status("  /join-docs <collection_id> <doc1> <doc2>    # Join specific documents")
        controller.display.show_status("  /join <collection_id>                       # Short alias")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /join-docs vs_abc123                        # Join all uploaded docs")
        controller.display.show_status("  /join-docs vs_abc123 doc_123 doc_456        # Join specific documents")
        controller.display.show_status("  /add-to-collection vs_research doc_789      # Using alternative alias")
        controller.display.show_status("")
        
        controller.display.show_status("✨ Features:")
        controller.display.show_status("  • Automatically adds collection to conversation context")
        controller.display.show_status("  • Validates document IDs before joining")
        controller.display.show_status("  • Shows confirmation of successful joins")
        controller.display.show_status("  • Lists all joined documents for verification")
        controller.display.show_status("")
        
        controller.display.show_status("🔄 Workflow:")
        controller.display.show_status("  1. Upload documents: /upload file.pdf")
        controller.display.show_status("  2. Create collection: /new-collection name=\"My Docs\" desc=\"Description\"")
        controller.display.show_status("  3. Join documents: /join-docs <collection-id>")
        controller.display.show_status("  4. Enable file search: /enable-file-search")
        controller.display.show_status("  5. Ask questions about your documents!")
        controller.display.show_status("")
        
        controller.display.show_status("⚠️ Prerequisites:")
        controller.display.show_status("  • Documents must be uploaded first (/upload)")
        controller.display.show_status("  • Collection must exist (/new-collection)")
        controller.display.show_status("  • Use /documents to see available document IDs")
    
    async def _show_new_collection_help(self, controller: ChatController) -> None:
        """Show detailed help for new-collection command."""
        controller.display.show_status("🏗️ New Collection Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Create new vector store collections to organize your documents")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Basic Usage:")
        controller.display.show_status("  /new-collection name=\"Collection Name\" desc=\"Description\"")
        controller.display.show_status("")
        
        controller.display.show_status("🎛️ Advanced Options:")
        controller.display.show_status("  name=\"Name\"              # Required: Collection name")
        controller.display.show_status("  desc=\"Description\"        # Required: Collection description")
        controller.display.show_status("  model=\"embedding-model\"   # Optional: Embedding model")
        controller.display.show_status("  id=\"custom-id\"           # Optional: Custom collection ID")
        controller.display.show_status("  metadata=\"key:val,k2:v2\" # Optional: Custom metadata")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  # Basic collection")
        controller.display.show_status("  /new-collection name=\"Research Papers\" desc=\"AI research documents\"")
        controller.display.show_status("")
        controller.display.show_status("  # Advanced collection with metadata")
        controller.display.show_status("  /new-collection name=\"Support FAQ\" desc=\"Customer support docs\" metadata=\"domain:support,priority:high\"")
        controller.display.show_status("")
        controller.display.show_status("  # Collection with custom model")
        controller.display.show_status("  /new-collection name=\"Technical Docs\" desc=\"Technical documentation\" model=\"text-embedding-v4\"")
        controller.display.show_status("")
        
        controller.display.show_status("✨ Features:")
        controller.display.show_status("  • Intelligent parameter parsing with quoted values")
        controller.display.show_status("  • Automatic collection ID generation")
        controller.display.show_status("  • Metadata support for organization")
        controller.display.show_status("  • Auto-adds to conversation context")
        controller.display.show_status("  • Helpful next-steps guidance")
        controller.display.show_status("")
        
        controller.display.show_status("🔧 Parameter Format:")
        controller.display.show_status("  • Use quotes for values with spaces: name=\"My Collection\"")
        controller.display.show_status("  • Metadata format: \"key:value,key2:value2\"")
        controller.display.show_status("  • Parameters can be in any order")
        controller.display.show_status("  • Both name and desc are required")
        controller.display.show_status("")
        
        controller.display.show_status("🔗 Related Commands:")
        controller.display.show_status("  • /join-docs <collection-id>     # Add documents to collection")
        controller.display.show_status("  • /show-collection <id>          # View collection details")
        controller.display.show_status("  • /enable-file-search            # Enable search functionality")
    
    async def _show_show_doc_help(self, controller: ChatController) -> None:
        """Show detailed help for show-doc command."""
        controller.display.show_status("📄 Show Document Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Display comprehensive information about a specific document")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Usage:")
        controller.display.show_status("  /show-doc <document-id>")
        controller.display.show_status("  /doc <document-id>          # Short alias")
        controller.display.show_status("  /document <document-id>     # Alternative alias")
        controller.display.show_status("  /file-info <document-id>    # Descriptive alias")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /show-doc file_abc123")
        controller.display.show_status("  /doc doc_456789")
        controller.display.show_status("  /file-info upload-task-123")
        controller.display.show_status("")
        
        controller.display.show_status("📊 Information Displayed:")
        controller.display.show_status("  • Document ID and filename")
        controller.display.show_status("  • File size (human-readable format)")
        controller.display.show_status("  • Content type and purpose")
        controller.display.show_status("  • Processing status with emoji indicators")
        controller.display.show_status("  • Creation and update timestamps")
        controller.display.show_status("  • Task ID for processing tracking")
        controller.display.show_status("  • Custom metadata (if any)")
        controller.display.show_status("  • MD5 hash for integrity verification")
        controller.display.show_status("  • Error information (if processing failed)")
        controller.display.show_status("")
        
        controller.display.show_status("💡 Finding Document IDs:")
        controller.display.show_status("  • Use /documents to list all uploaded document IDs")
        controller.display.show_status("  • Document IDs are shown during upload process")
        controller.display.show_status("  • IDs usually start with 'file_' or 'doc_'")
        controller.display.show_status("")
        
        controller.display.show_status("🔗 Related Commands:")
        controller.display.show_status("  • /documents                     # List all document IDs")
        controller.display.show_status("  • /join-docs <vs-id> <doc-id>   # Add document to collection")
        controller.display.show_status("  • /upload <file>                # Upload new documents")
    
    async def _show_show_collection_help(self, controller: ChatController) -> None:
        """Show detailed help for show-collection command."""
        controller.display.show_status("📚 Show Collection Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Display comprehensive information about a vector store collection")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Usage:")
        controller.display.show_status("  /show-collection <collection-id>")
        controller.display.show_status("  /show-collection <collection-id> --summary    # Include AI summary")
        controller.display.show_status("  /collection <collection-id>                   # Short alias")
        controller.display.show_status("  /vs <collection-id>                          # Vector store alias")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /show-collection vs_abc123")
        controller.display.show_status("  /vs vs_research --summary")
        controller.display.show_status("  /collection vs_docs_456")
        controller.display.show_status("")
        
        controller.display.show_status("📊 Information Displayed:")
        controller.display.show_status("  • Collection ID, name, and description")
        controller.display.show_status("  • File statistics (total, completed, in progress, failed)")
        controller.display.show_status("  • List of document IDs in the collection")
        controller.display.show_status("  • Total storage size (human-readable)")
        controller.display.show_status("  • Creation timestamp")
        controller.display.show_status("  • Custom metadata (if any)")
        controller.display.show_status("  • AI-generated summary (with --summary flag)")
        controller.display.show_status("")
        
        controller.display.show_status("🎯 Smart Features:")
        controller.display.show_status("  • Intelligent file list truncation (shows first 8 + last 2)")
        controller.display.show_status("  • Status emoji indicators for visual clarity")
        controller.display.show_status("  • Optional AI summary for content overview")
        controller.display.show_status("  • Helpful usage tips and related commands")
        controller.display.show_status("")
        
        controller.display.show_status("💡 Finding Collection IDs:")
        controller.display.show_status("  • Use /tools to see active vector stores")
        controller.display.show_status("  • Collection IDs are shown when creating with /new-collection")
        controller.display.show_status("  • IDs usually start with 'vs_'")
        controller.display.show_status("")
        
        controller.display.show_status("🔗 Related Commands:")
        controller.display.show_status("  • /new-collection               # Create new collection")
        controller.display.show_status("  • /join-docs <id>              # Add documents to collection")
        controller.display.show_status("  • /show-doc <doc-id>           # View document details")
        controller.display.show_status("  • /enable-file-search          # Enable search on collections")
    
    async def _show_help_help(self, controller: ChatController) -> None:
        """Show help for the help command itself."""
        controller.display.show_status("❓ File Help Command - Detailed Help")
        controller.display.show_status("=" * 50)
        controller.display.show_status("")
        
        controller.display.show_status("📋 Purpose:")
        controller.display.show_status("  Comprehensive help system for all file management commands")
        controller.display.show_status("")
        
        controller.display.show_status("⚡ Usage:")
        controller.display.show_status("  /file-help                  # General overview of all commands")
        controller.display.show_status("  /file-help <command>        # Detailed help for specific command")
        controller.display.show_status("  /fhelp <command>           # Short alias")
        controller.display.show_status("  /help-files                # Alternative alias")
        controller.display.show_status("")
        
        controller.display.show_status("📝 Examples:")
        controller.display.show_status("  /file-help                 # Show command overview")
        controller.display.show_status("  /file-help upload          # Detailed upload help")
        controller.display.show_status("  /fhelp new-collection      # Help for creating collections")
        controller.display.show_status("  /help-files join-docs      # Help for joining documents")
        controller.display.show_status("")
        
        controller.display.show_status("🎯 Available Help Topics:")
        controller.display.show_status("  • upload, u, up            # File upload help")
        controller.display.show_status("  • documents, docs, files   # Document listing help")
        controller.display.show_status("  • join-docs, join          # Document joining help")
        controller.display.show_status("  • new-collection, new-vs   # Collection creation help")
        controller.display.show_status("  • show-doc, doc           # Document details help")
        controller.display.show_status("  • show-collection, vs     # Collection details help")
        controller.display.show_status("  • file-help, fhelp        # This help system")
        controller.display.show_status("")
        
        controller.display.show_status("✨ Features:")
        controller.display.show_status("  • Alias support - all command aliases work")
        controller.display.show_status("  • Comprehensive examples and use cases")
        controller.display.show_status("  • Related command suggestions")
        controller.display.show_status("  • Workflow guidance and best practices")
        controller.display.show_status("")
        
        controller.display.show_status("💡 Pro Tips:")
        controller.display.show_status("  • Start with /file-help for overview")
        controller.display.show_status("  • Use specific command help when stuck")
        controller.display.show_status("  • Check related commands for workflow ideas")
        controller.display.show_status("  • Commands work with all their aliases")