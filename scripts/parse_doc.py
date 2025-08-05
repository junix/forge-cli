#!/usr/bin/env python3
"""
Parse a document using the Knowledge Forge API and dump the result to JSON.

This script uploads a file to the Knowledge Forge API, waits for processing,
and then dumps the parsed document content to a JSON file named <doc-id>.json.

Usage:
    python parse_doc.py -f <path>
    python parse_doc.py --file <path>

Examples:
    python parse_doc.py -f document.pdf
    python parse_doc.py --file /path/to/document.docx

Environment:
    KNOWLEDGE_FORGE_URL: API endpoint (default: http://localhost:9999)
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
import httpx
from datetime import datetime


class ForgeAPIClient:
    """Simple HTTP client for Knowledge Forge API using httpx."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")
        self.base_url = self.base_url.rstrip('/')
        
    async def upload_file(self, file_path: str, purpose: str = "general"):
        """Upload a file and return the response."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        async with httpx.AsyncClient() as client:
            with open(path, 'rb') as f:
                files = {'file': (path.name, f, 'application/octet-stream')}
                data = {'purpose': purpose}
                
                response = await client.post(
                    f"{self.base_url}/v1/files",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()
    
    async def check_task_status(self, task_id: str):
        """Check the status of a processing task."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/v1/tasks/{task_id}")
            response.raise_for_status()
            return response.json()
    
    async def wait_for_task_completion(self, task_id: str, poll_interval: int = 2, max_attempts: int = 60):
        """Wait for a task to complete by polling its status."""
        attempts = 0
        
        while attempts < max_attempts:
            task_status = await self.check_task_status(task_id)
            status = task_status.get('status', 'unknown')
            
            if status in ["completed", "failed", "cancelled"]:
                return task_status
                
            await asyncio.sleep(poll_interval)
            attempts += 1
            
        raise TimeoutError(f"Task {task_id} did not complete within the allowed time")
    
    async def fetch_document(self, document_id: str):
        """Fetch document content by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/v1/files/{document_id}/content")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()


async def parse_document(file_path: str):
    """Parse a document and save the result to JSON."""
    client = ForgeAPIClient()
    
    print(f"Uploading file: {file_path}")
    
    try:
        # Upload the file
        upload_result = await client.upload_file(file_path)
        file_id = upload_result.get('id')
        task_id = upload_result.get('task_id')
        
        print(f"File uploaded successfully. ID: {file_id}")
        
        # Wait for processing if there's a task ID
        if task_id:
            print(f"Waiting for file processing (task: {task_id})...")
            task_status = await client.wait_for_task_completion(task_id)
            status = task_status.get('status', 'unknown')
            
            if status == 'failed':
                error = task_status.get('error', 'Unknown error')
                print(f"Processing failed: {error}")
                return False
                
            print(f"Processing completed with status: {status}")
        
        # Fetch the processed document
        print(f"Fetching document content...")
        document = await client.fetch_document(file_id)
        
        if not document:
            print(f"Failed to fetch document with ID: {file_id}")
            return False
            
        # Save to JSON file
        doc_id = document.get('id', file_id)
        output_file = f"{doc_id}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
            
        print(f"Document successfully parsed and saved to: {output_file}")
        
        # Print summary information
        print("\n=== Document Summary ===")
        print(f"Document ID: {doc_id}")
        print(f"Title: {document.get('title', 'Unknown')}")
        print(f"MD5: {document.get('md5sum', 'Unknown')}")
        print(f"MIME Type: {document.get('mime_type', 'Unknown')}")
        
        if document.get('content'):
            content = document['content']
            print(f"Language: {content.get('language', 'Unknown')}")
            print(f"Page Count: {content.get('page_count', 0)}")
            print(f"Segments: {len(content.get('segments', []))}")
            
            if content.get('summary'):
                summary = content['summary']
                print(f"\nSummary Preview:")
                print(f"{summary[:200]}{'...' if len(summary) > 200 else ''}")
                
        return True
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parse a document using Knowledge Forge API and dump to JSON"
    )
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Path to the file to parse'
    )
    
    args = parser.parse_args()
    
    # Run the async function
    success = asyncio.run(parse_document(args.file))
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()