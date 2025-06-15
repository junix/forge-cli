import unittest
import uuid

# Assuming the Chunk model is in src.models.chunk
# Adjust the import path if necessary
from forge_cli.core.chunk import Chunk


class TestChunk(unittest.TestCase):
    def test_chunk_instantiation_with_optional_fields(self):
        """Test Chunk creation with all fields provided."""
        chunk_id = str(uuid.uuid4())
        content = "This is a test chunk."
        index = 1
        metadata = {"source": "test_document.txt"}
        chunk = Chunk(id=chunk_id, content=content, index=index, metadata=metadata)
        self.assertEqual(chunk.id, chunk_id)
        self.assertEqual(chunk.content, content)
        self.assertEqual(chunk.index, index)
        self.assertEqual(chunk.metadata, metadata)

    def test_chunk_instantiation_without_optional_fields(self):
        """Test Chunk creation with minimal fields and default ID."""
        content = "Another test chunk."
        # id, index, and metadata have defaults or are Optional
        chunk = Chunk(content=content)

        self.assertIsNotNone(chunk.id)
        self.assertTrue(isinstance(uuid.UUID(chunk.id, version=4), uuid.UUID))  # Check if it's a valid UUIDv4
        self.assertEqual(chunk.content, content)
        self.assertIsNone(chunk.index)  # Default for index is None
        self.assertEqual(chunk.metadata, {})  # Default metadata should be empty dict

    def test_chunk_metadata(self):
        """Test the metadata field can store and retrieve arbitrary key-value pairs."""
        content = "Chunk with metadata."
        metadata = {"author": "John Doe", "page": 5, "active": True}
        # Minimal instantiation, relying on default id and index
        chunk = Chunk(content=content, metadata=metadata)

        self.assertEqual(chunk.metadata["author"], "John Doe")
        self.assertEqual(chunk.metadata["page"], 5)
        self.assertTrue(chunk.metadata["active"])

        # Pydantic models are generally mutable unless configured otherwise
        chunk.metadata["new_key"] = "new_value"
        self.assertEqual(chunk.metadata["new_key"], "new_value")

        # Test with empty metadata
        chunk_empty_meta = Chunk(content="content", metadata={})
        self.assertEqual(chunk_empty_meta.metadata, {})

        # Test with metadata being None (Pydantic uses the provided None, doesn't trigger default_factory)
        chunk_none_meta = Chunk(content="content", metadata=None)
        self.assertIsNone(chunk_none_meta.metadata)

    def test_chunk_id_generation_and_usage(self):
        """Test ID is generated if not provided, and used if provided."""
        # ID generated (content is optional, but providing it for clarity)
        chunk_generated_id = Chunk(content="content1")
        self.assertIsNotNone(chunk_generated_id.id)
        self.assertTrue(isinstance(uuid.UUID(chunk_generated_id.id, version=4), uuid.UUID))
        self.assertIsNone(chunk_generated_id.index)  # Check default

        # ID provided
        provided_id = str(uuid.uuid4())
        chunk_provided_id = Chunk(id=provided_id, content="content2", index=0)
        self.assertEqual(chunk_provided_id.id, provided_id)
        self.assertEqual(chunk_provided_id.index, 0)


if __name__ == "__main__":
    unittest.main()
