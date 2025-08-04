from __future__ import annotations

"""Command completion for chat interface using prompt_toolkit."""

from collections.abc import Iterator
from typing import Any

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class CommandCompleter(Completer):
    """Auto-completion for chat commands and file references.

    Provides intelligent auto-completion for:
    - Chat commands starting with '/' and shows command descriptions as metadata
    - File references starting with '@' for inline file questioning

    Attributes:
        commands: Dictionary mapping command names to command objects.
        aliases: Dictionary mapping aliases to primary command names.
        all_commands: Sorted list of all commands and aliases with '/' prefix.
        conversation: Conversation state for accessing file lists.
    """

    def __init__(self, commands_dict: dict[str, Any], aliases_dict: dict[str, str], conversation=None) -> None:
        """Initialize the command completer.

        Args:
            commands_dict: Dictionary mapping command names to command objects.
            aliases_dict: Dictionary mapping aliases to primary command names.
            conversation: Conversation state for file auto-completion (optional).
        """
        self.commands = commands_dict
        self.aliases = aliases_dict
        self.conversation = conversation
        self._file_cache = None  # Cache for available files
        self._cache_time = 0  # Timestamp of last cache update
        self._cache_expiry_seconds = 300  # 5 minutes

        # Build list of all command names with leading slash
        self.all_commands: list[str] = []
        for cmd in commands_dict.keys():
            self.all_commands.append(f"/{cmd}")
        for alias in aliases_dict.keys():
            self.all_commands.append(f"/{alias}")
        self.all_commands.sort()

    def get_completions(self, document: Document, complete_event: Any) -> Iterator[Completion]:
        """Generate completions for the current input.

        Args:
            document: The current document state from prompt_toolkit.
            complete_event: The completion event (unused by this implementation).

        Yields:
            Completion objects for matching commands or file references.
        """
        del complete_event  # Unused parameter required by interface
        text = document.text_before_cursor.lstrip()

        # Handle @ file references
        if "@" in text:
            yield from self._get_file_completions(document, text)
            return

        # If text starts with /, show command completions
        if text.startswith("/"):
            # Get the partial command (including the /)
            partial = text.lower()

            # Find all matching commands
            for cmd in self.all_commands:
                if cmd.lower().startswith(partial):
                    # Calculate the completion text (what to add)
                    completion_text = cmd[len(text) :]
                    yield Completion(
                        completion_text,
                        start_position=0,
                        display=cmd,  # Show full command in menu
                        display_meta=self._get_description(cmd),
                    )

        # If just typed /, show all commands
        elif text == "":
            word_before_cursor = document.get_word_before_cursor(WORD=True)
            if word_before_cursor == "/":
                for cmd in self.all_commands:
                    yield Completion(
                        cmd[1:],  # Remove the leading /
                        start_position=-1,  # Replace the /
                        display=cmd,
                        display_meta=self._get_description(cmd),
                    )

    def _get_description(self, cmd_with_slash: str) -> str:
        """Get the description for a command.

        Args:
            cmd_with_slash: Command name with leading slash.

        Returns:
            Description string for the command, or empty string if not found.
        """
        # Remove leading slash
        cmd = cmd_with_slash[1:] if cmd_with_slash.startswith("/") else cmd_with_slash

        # Check if it's an alias
        if cmd in self.aliases:
            actual_cmd = self.commands[self.aliases[cmd]]
            return f"(alias) {actual_cmd.description}"
        elif cmd in self.commands:
            return self.commands[cmd].description
        return ""

    def _get_file_completions(self, document: Document, text: str) -> Iterator[Completion]:
        """Generate file completions for @ syntax.

        Args:
            document: The current document state from prompt_toolkit.
            text: The text before cursor.

        Yields:
            Completion objects for matching files.
        """
        if not self.conversation:
            return

        # Find the @ symbol and extract the partial file reference
        at_pos = text.rfind("@")
        if at_pos == -1:
            return

        # Get the partial file reference after @
        partial_file = text[at_pos + 1 :].lower()

        # Get available files from conversation
        files = self._get_available_files()

        for file_info in files:
            file_id = file_info.get("id", "")
            filename = file_info.get("filename", "")

            # Match against both file ID and filename
            if partial_file in file_id.lower() or partial_file in filename.lower():
                # Use file ID as completion text
                completion_text = file_id[len(partial_file) :]
                display_text = f"@{file_id}"
                meta_text = f"📄 {filename}"

                yield Completion(
                    completion_text,
                    start_position=0,
                    display=display_text,
                    display_meta=meta_text,
                )

    def _get_available_files(self) -> list[dict[str, str]]:
        """Get list of available files for completion.

        Returns:
            List of file info dictionaries.
        """
        if not self.conversation:
            return []

        import time

        # Check if cache is valid
        current_time = time.time()
        cache_is_valid = (
            self._file_cache is not None
            and (current_time - self._cache_time) < self._cache_expiry_seconds
        )

        if cache_is_valid:
            return self._file_cache

        files = []

        # Get uploaded documents
        uploaded_docs = self.conversation.get_uploaded_documents()
        files.extend(uploaded_docs)

        # Get files from vector stores
        vector_store_ids = self.conversation.get_current_vector_store_ids()
        if vector_store_ids:
            # Try to get files from each vector store
            for vs_id in vector_store_ids:
                vs_files = self._get_vector_store_files_sync(vs_id)
                files.extend(vs_files)

        # Cache the result with timestamp
        self._file_cache = files
        self._cache_time = current_time
        return files

    def refresh_file_cache(self):
        """Refresh the file cache. Call this when files might have changed."""
        self._file_cache = None

    def _get_vector_store_files_sync(self, vector_store_id: str) -> list[dict[str, str]]:
        """Get files from a vector store synchronously.

        Args:
            vector_store_id: The vector store ID to query

        Returns:
            List of file info dictionaries
        """
        try:
            import requests
            from ..config import get_base_url

            # Use synchronous requests to avoid async issues
            base_url = get_base_url()
            
            # First try list_documents endpoint if available
            list_url = f"{base_url}/v1/vector_stores/{vector_store_id}/files"
            
            try:
                # Try to get file list directly
                list_response = requests.get(list_url, timeout=3.0)
                
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    files = []
                    
                    # Handle different response formats
                    if "data" in list_data:
                        file_items = list_data["data"]
                    elif "files" in list_data:
                        file_items = list_data["files"]
                    else:
                        file_items = []
                    
                    for item in file_items:
                        file_id = item.get("id") or item.get("file_id")
                        filename = item.get("filename") or item.get("name") or f"file_{file_id[:8]}.txt"
                        
                        if file_id:
                            files.append({"id": file_id, "filename": filename})
                    
                    if files:  # If we got files from list endpoint, return them
                        return files
            except:
                pass  # Fall back to search endpoint
            
            # Fall back to search endpoint
            search_url = f"{base_url}/v1/vector_stores/{vector_store_id}/search"
            
            # Prepare the search payload
            payload = {
                "query": "document content text information file",  # Broad query
                "top_k": 50,  # Get up to 50 documents for completion
            }

            # Make synchronous request
            response = requests.post(search_url, json=payload, timeout=5.0)
            
            if response.status_code != 200:
                return []

            # Extract data from raw response
            response_data = response.json()
            documents = response_data.get("data", [])

            files = []
            seen_file_ids = set()

            for item in documents:
                # Get file_id and filename from the raw response
                file_id = item.get("file_id")
                filename = item.get("filename")
                
                # Try to extract filename from content if not provided
                if not filename and item.get("content"):
                    # Look for filename in content metadata
                    content_lines = item["content"].split("\n")
                    for line in content_lines[:5]:  # Check first 5 lines
                        if "filename:" in line.lower() or "file:" in line.lower():
                            filename = line.split(":", 1)[-1].strip()
                            break
                
                # Default filename if still not found
                if not filename:
                    filename = f"document_{file_id[:8]}.txt" if file_id else "unknown.txt"

                if file_id and file_id not in seen_file_ids:
                    seen_file_ids.add(file_id)
                    files.append({"id": file_id, "filename": filename})

            return files

        except Exception:
            # If anything fails, return empty list
            return []

    async def _get_vector_store_files_async(self, vector_store_id: str) -> list[dict[str, str]]:
        """Get files from a vector store asynchronously.

        Args:
            vector_store_id: The vector store ID to query

        Returns:
            List of file info dictionaries
        """
        try:
            # Make raw HTTP request to avoid Pydantic validation issues
            from forge_cli.config import BASE_URL
            from forge_cli.sdk.http_client import async_make_request

            url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/search"
            payload = {
                "query": "document content text information",  # Broad query
                "top_k": 50,  # Get up to 50 documents for completion
            }

            status_code, response_data = await async_make_request("POST", url, json=payload)

            if status_code != 200 or not response_data:
                return []

            # Extract data from raw response
            documents = response_data.get("data", [])

            files = []
            seen_file_ids = set()

            for item in documents:
                # Get file_id and filename from the raw response
                file_id = item.get("file_id")
                filename = item.get("filename", f"{file_id}.txt" if file_id else "unknown.txt")

                if file_id and file_id not in seen_file_ids:
                    seen_file_ids.add(file_id)
                    files.append({"id": file_id, "filename": filename})

            return files

        except Exception:
            # Silent fail for completion
            return []
