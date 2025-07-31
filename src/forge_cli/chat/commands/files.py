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