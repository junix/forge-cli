#!/usr/bin/env python3
import argparse
import asyncio
import os

# Import SDK functions
from forge_cli.sdk import async_delete_file, async_upload_file


async def upload_file(file_path):
    """Upload a file to the Knowledge Forge API using SDK."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None

    try:
        file_name = os.path.basename(file_path)
        print(f"Uploading '{file_name}' with purpose: general")

        # Call the SDK function to upload the file
        result = await async_upload_file(
            file_path=file_path,
            purpose="general",
        )

        if result:
            print("Upload successful. Server response:")
            print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
            return result
        else:
            print("Failed to upload file.")
            return None

    except Exception as e:
        print(f"Error during upload: {e}")
        return None


async def delete_file(file_id):
    """Delete a file from the Knowledge Forge API using SDK.

    Args:
        file_id (str): The ID of the file to delete.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"Deleting file with ID '{file_id}'")

        # Call the SDK function to delete the file
        result = await async_delete_file(file_id)

        if result:
            print("Delete successful. Server response:")
            print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
            return True
        else:
            print("Failed to delete file.")
            return False

    except Exception as e:
        print(f"Error during file deletion: {e}")
        return False


async def main():
    """Main async function to handle file operations."""
    parser = argparse.ArgumentParser(description="Upload or delete files using Knowledge Forge SDK")
    parser.add_argument("-f", "--file", help="Path to the file to upload")
    parser.add_argument("--delete", help="ID of the file to delete")

    args = parser.parse_args()

    if args.delete:
        await delete_file(args.delete)
    elif args.file:
        await upload_file(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
