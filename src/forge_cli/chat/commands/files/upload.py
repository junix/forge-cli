"""File upload command."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class UploadCommand(ChatCommand):
    """Upload and process files with comprehensive options and real-time progress tracking.

    Usage:
    - /upload <file_path> - Upload a file and track processing progress
    - /upload <file_path> --purpose qa - Upload with specific purpose
    - /upload <file_path> --abstract --summary --keywords --vectorize - Enable specific processing
    - /upload --url <url> --name <filename> --file-type <mime_type> - Upload from URL
    - /upload <file_path> --id <uuid> --skip-exists - Upload with custom ID and skip if exists
    - /upload <file_path> --fast-mode - Enable fast processing mode
    """

    name = "upload"
    description = "Upload and process files with comprehensive options and progress tracking"
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
            controller.display.show_error("Please specify a file path or URL")
            controller.display.show_status("Examples:")
            controller.display.show_status("  /upload ./documents/report.pdf")
            controller.display.show_status("  /upload --url https://example.com/doc.pdf --name doc.pdf --file-type application/pdf")
            controller.display.show_status("  /upload ./file.pdf --abstract --summary --keywords --vectorize")
            return True

        # Parse arguments
        arg_parts = args.strip().split()
        
        # Parse all options
        options = self._parse_upload_options(arg_parts)
        
        # Validate required parameters
        if not options.get("file_path") and not options.get("url"):
            controller.display.show_error("Must provide either file path or --url")
            return True
        
        if options.get("url") and (not options.get("name") or not options.get("file_type")):
            controller.display.show_error("When using --url, must provide --name and --file-type")
            return True

        # Validate file path if provided
        file_path = None
        if options.get("file_path"):
            file_path = Path(options["file_path"]).expanduser().resolve()
            if not file_path.exists():
                controller.display.show_error(f"File not found: {file_path}")
                return True

            if not file_path.is_file():
                controller.display.show_error(f"Path is not a file: {file_path}")
                return True

        # Start upload process
        if file_path:
            controller.display.show_status(f"📤 Starting upload: {file_path.name}")
        else:
            controller.display.show_status(f"📤 Starting upload from URL: {options['url']}")

        try:
            # Import SDK functions
            from forge_cli.sdk import async_upload_file

            # Prepare parse options based on individual flags
            parse_options = self._build_parse_options(options, file_path)
            
            # Display parse options info
            if parse_options and any(v == "enable" for v in parse_options.values()):
                enabled_options = [k for k, v in parse_options.items() if v == "enable"]
                controller.display.show_status(f"📋 Processing options: {', '.join(enabled_options)}")

            # Upload file
            controller.display.show_status("⏳ Uploading file...")
            
            # Prepare upload parameters
            upload_params = {
                "purpose": options.get("purpose", "general"),
                "skip_exists": options.get("skip_exists", False),
                "parse_options": parse_options
            }
            
            # Add optional parameters if provided
            if options.get("id"):
                upload_params["id"] = options["id"]
            if options.get("md5"):
                upload_params["md5"] = options["md5"]
            if options.get("request_id"):
                upload_params["request_id"] = options["request_id"]
            
            # Handle file vs URL upload
            if file_path:
                upload_params["path"] = str(file_path)
                file_result = await async_upload_file(**upload_params)
            else:
                # URL upload parameters
                upload_params.update({
                    "url": options["url"],
                    "name": options["name"],
                    "file_type": options["file_type"]
                })
                file_result = await async_upload_file(**upload_params)

            controller.display.show_status(f"✅ File uploaded! ID: {file_result.id}")
            controller.display.show_status(f"📋 Task ID: {file_result.task_id}")

            # Start progress tracking
            if file_result.task_id:
                filename = file_path.name if file_path else options.get("name", "uploaded_file")
                await self._track_processing_progress(controller, file_result.task_id, filename)
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
                            f"{status_emoji} {task_status.status.upper()}: {filename} ({progress_percent}%)"
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
                            document_id = task_id.replace("upload-", "")
                            controller.display.show_status(f"📄 Document ID: {document_id}")

                            # Save document ID to conversation state
                            controller.conversation.add_uploaded_document(document_id=document_id, filename=filename)
                            controller.display.show_status("💾 Document saved to conversation state")
                        elif task_status.status == "failed":
                            error_msg = "Unknown error"
                            # Try multiple fields for error information
                            if hasattr(task_status, "failure_reason") and task_status.failure_reason:
                                error_msg = task_status.failure_reason
                            elif hasattr(task_status, "error_message") and task_status.error_message:
                                error_msg = task_status.error_message
                            elif (
                                hasattr(task_status, "data") and task_status.data and isinstance(task_status.data, dict)
                            ):
                                error_msg = task_status.data.get("error", error_msg)
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
                controller.display.show_error("⏰ Timeout: Processing took longer than expected")
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
            "parse_pending": "⏳",
        }
        return status_emojis.get(status, "🔄")

    def _parse_upload_options(self, arg_parts: list[str]) -> dict[str, any]:
        """Parse command arguments into options dictionary.
        
        Args:
            arg_parts: List of command arguments
            
        Returns:
            Dictionary containing parsed options
        """
        options = {}
        i = 0
        
        # Parse all arguments and look for file path anywhere
        while i < len(arg_parts):
            arg = arg_parts[i]
            
            # Check if this is a file path (doesn't start with -- and no file_path found yet)
            if not arg.startswith("--") and not options.get("file_path"):
                options["file_path"] = arg
                i += 1
                continue
            
            if arg == "--url" and i + 1 < len(arg_parts):
                options["url"] = arg_parts[i + 1]
                i += 2
            elif arg == "--name" and i + 1 < len(arg_parts):
                options["name"] = arg_parts[i + 1]
                i += 2
            elif arg == "--file-type" and i + 1 < len(arg_parts):
                options["file_type"] = arg_parts[i + 1]
                i += 2
            elif arg == "--purpose" and i + 1 < len(arg_parts):
                options["purpose"] = arg_parts[i + 1]
                i += 2
            elif arg == "--id" and i + 1 < len(arg_parts):
                options["id"] = arg_parts[i + 1]
                i += 2
            elif arg == "--md5" and i + 1 < len(arg_parts):
                options["md5"] = arg_parts[i + 1]
                i += 2
            elif arg == "--request-id" and i + 1 < len(arg_parts):
                options["request_id"] = arg_parts[i + 1]
                i += 2
            elif arg == "--skip-exists":
                options["skip_exists"] = True
                i += 1
            elif arg == "--abstract":
                options["abstract"] = True
                i += 1
            elif arg == "--summary":
                options["summary"] = True
                i += 1
            elif arg == "--outline":
                options["outline"] = True
                i += 1
            elif arg == "--keywords":
                options["keywords"] = True
                i += 1
            elif arg == "--contexts":
                options["contexts"] = True
                i += 1
            elif arg == "--graph":
                options["graph"] = True
                i += 1
            elif arg == "--vectorize":
                options["vectorize"] = True
                i += 1
            elif arg == "--outline-json-style":
                options["outline_json_style"] = True
                i += 1
            elif arg == "--fast-mode":
                options["fast_mode"] = True
                i += 1
            else:
                # Skip unknown arguments
                i += 1
        
        return options

    def _build_parse_options(self, options: dict[str, any], file_path: Path = None) -> dict[str, str] | None:
        """Build parse_options dictionary from parsed options.
        
        Args:
            options: Parsed command options
            file_path: Optional file path for Excel file detection
            
        Returns:
            Dictionary of parse options or None if no processing needed
        """
        # Check if file is Excel format (skip parse options for Excel)
        is_excel_file = False
        if file_path and file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
            is_excel_file = True

        # Build parse options based on flags
        parse_options = {}
        
        # Map option flags to parse option keys
        option_mapping = {
            "abstract": "abstract",
            "summary": "summary", 
            "outline": "outline",
            "keywords": "keywords",
            "contexts": "contexts",
            "graph": "graph",
            "vectorize": "vectorize",
            "outline_json_style": "outline_json_style",
            "fast_mode": "fast_mode"
        }
        
        # Check each option and set to enable if present
        for option_key, parse_key in option_mapping.items():
            if options.get(option_key):
                if is_excel_file and parse_key == "vectorize":
                    # Special handling for Excel files - disable vectorize even if requested
                    parse_options[parse_key] = "disable"
                else:
                    parse_options[parse_key] = "enable"
            else:
                parse_options[parse_key] = "disable"
        
        # If no processing options were enabled, return None
        if not any(v == "enable" for v in parse_options.values()):
            return None
            
        return parse_options
