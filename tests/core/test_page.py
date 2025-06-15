import unittest
import uuid

# Assuming the Page model is in src.forge_cli.core.page
# Adjust the import path if necessary
from src.forge_cli.core.page import Page
from src.forge_cli.core.chunk import Chunk # To compare behavior or check instance

class TestPage(unittest.TestCase):

    def test_page_instantiation_with_specific_and_inherited_fields(self):
        """Test Page creation with its specific fields and inherited Chunk fields."""
        page_id = str(uuid.uuid4())
        content = "This is the content of a page."
        url = "https://example.com/my-page"
        metadata = {"source": "web"}
        index = 0

        page = Page(
            id=page_id,
            content=content,
            url=url,
            metadata=metadata,
            index=index
        )

        self.assertEqual(page.id, page_id)
        self.assertEqual(page.content, content)
        self.assertEqual(page.url, url)
        self.assertEqual(page.metadata, metadata)
        self.assertEqual(page.index, index)
        self.assertTrue(isinstance(page, Chunk)) # Verify inheritance

    def test_page_instantiation_minimal(self):
        """Test Page creation with minimal fields (assuming url is key)."""
        # This test depends on knowing which fields are truly optional or required for Page
        # For now, let's assume 'url' is a primary specific field.
        # And 'content' might be optional in Chunk, 'id' has default factory.
        url = "https://example.com/another-page"
        page = Page(url=url) # Potentially add other fields if instantiation fails

        self.assertIsNotNone(page.id) # Inherited from Chunk
        self.assertTrue(isinstance(uuid.UUID(page.id, version=4), uuid.UUID))
        self.assertEqual(page.url, url)
        self.assertIsNone(page.content) # Default from Chunk
        self.assertEqual(page.metadata, {}) # Default from Chunk
        self.assertIsNone(page.index) # Default from Chunk

    def test_page_url_field(self):
        """Test the Page-specific 'url' field."""
        url1 = "https://example.com/page1"
        page1 = Page(url=url1, content="Content for page 1")
        self.assertEqual(page1.url, url1)

        # Test with a different URL
        url2 = "http://sub.example.org/another/path?query=true"
        page2 = Page(url=url2)
        self.assertEqual(page2.url, url2)

    def test_page_inherits_chunk_id_generation(self):
        """Test that Page instances correctly use Chunk's id generation."""
        page = Page(url="https://example.com/test-id-gen")
        self.assertIsNotNone(page.id)
        self.assertTrue(isinstance(uuid.UUID(page.id, version=4), uuid.UUID))

        # Test providing an ID
        specific_id = str(uuid.uuid4())
        page_with_id = Page(id=specific_id, url="https://example.com/specific-id")
        self.assertEqual(page_with_id.id, specific_id)

    def test_page_inherits_chunk_metadata_default(self):
        """Test that Page instances correctly use Chunk's metadata default."""
        page = Page(url="https://example.com/test-metadata")
        self.assertIsNotNone(page.metadata)
        self.assertEqual(page.metadata, {})

        custom_metadata = {"key": "value"}
        page_with_meta = Page(url="https://example.com/custom-meta", metadata=custom_metadata)
        self.assertEqual(page_with_meta.metadata, custom_metadata)


if __name__ == '__main__':
    unittest.main()
