#!/usr/bin/env python3
"""Common utilities and data structures for Knowledge Forge commands."""

import json
import os

from pydantic import BaseModel, Field


class FileEntry(BaseModel):
    """Represents a file entry in the test dataset."""

    file_id: str
    path: str
    questions: list[str] = Field(default_factory=list)


class TestDataset(BaseModel):
    """Represents the test dataset configuration."""

    files: list[FileEntry] = Field(default_factory=list)
    vectorstore_id: str = ""

    @classmethod
    def from_json(cls, json_path: str) -> "TestDataset":
        """Load TestDataset from a JSON file.

        Args:
            json_path: Path to the JSON file containing test dataset configuration.

        Returns:
            TestDataset instance with loaded data.

        Raises:
            FileNotFoundError: If the JSON file doesn't exist.
            json.JSONDecodeError: If the JSON file is invalid.
            ValidationError: If the JSON data doesn't match the expected schema.
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Test dataset file not found: {json_path}")

        with open(json_path) as f:
            data = json.load(f)

        # Use Pydantic's validation to parse the data
        return cls.model_validate(data)

    def to_dict(self) -> dict:
        """Convert TestDataset to a dictionary.

        Returns:
            Dictionary representation of the dataset.
        """
        return self.model_dump()

    def save_to_json(self, json_path: str) -> None:
        """Save TestDataset to a JSON file.

        Args:
            json_path: Path where the JSON file should be saved.
        """
        with open(json_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)

    def get_file_by_id(self, file_id: str) -> FileEntry | None:
        """Get a file entry by its ID.

        Args:
            file_id: The file ID to search for.

        Returns:
            FileEntry if found, None otherwise.
        """
        for file_entry in self.files:
            if file_entry.file_id == file_id:
                return file_entry
        return None

    def add_file(self, file_id: str, path: str, questions: list[str] | None = None) -> None:
        """Add a new file entry to the dataset.

        Args:
            file_id: The file ID.
            path: The file path.
            questions: List of questions for this file. Defaults to empty list.
        """
        if questions is None:
            questions = []
        self.files.append(FileEntry(file_id=file_id, path=path, questions=questions))

    def remove_file_by_id(self, file_id: str) -> bool:
        """Remove a file entry by its ID.

        Args:
            file_id: The file ID to remove.

        Returns:
            True if the file was removed, False if not found.
        """
        for i, file_entry in enumerate(self.files):
            if file_entry.file_id == file_id:
                self.files.pop(i)
                return True
        return False


def load_test_dataset(json_path: str = "test-dataset.json") -> TestDataset:
    """Convenience function to load test dataset from default or specified path.

    Args:
        json_path: Path to the JSON file. Defaults to "test-dataset.json".

    Returns:
        TestDataset instance.
    """
    return TestDataset.from_json(json_path)


# Example usage
if __name__ == "__main__":
    # Load test dataset
    dataset = load_test_dataset()

    print(f"Vector Store ID: {dataset.vectorstore_id}")
    print(f"Number of files: {len(dataset.files)}")

    # List all files
    for file_entry in dataset.files:
        print(f"  - File ID: {file_entry.file_id}")
        print(f"    Path: {file_entry.path}")
        if file_entry.questions:
            print(f"    Questions: {len(file_entry.questions)}")

    # Example: Get a specific file
    file_id = "f8e5d7c6-b9a8-4321-9876-543210abcdef"
    file_entry = dataset.get_file_by_id(file_id)
    if file_entry:
        print(f"\nFound file: {file_entry.path}")

    # Example: Add a new file
    dataset.add_file(
        "new-file-id-here", "/path/to/new/file.pdf", questions=["What is the main topic?", "What are the key findings?"]
    )

    # Example: Save back to JSON
    # dataset.save_to_json("test-dataset-updated.json")
