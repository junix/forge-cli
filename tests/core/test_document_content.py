import unittest
import uuid

from forge_cli.core.chunk import Chunk
from forge_cli.core.document_content import DocumentContent
from forge_cli.core.page import Page


class TestDocumentContent(unittest.TestCase):
    def test_instantiation_basic_required_id(self):
        """Test DocumentContent instantiation with required 'id' and default optionals."""
        doc_id = "test_id_123"  # Must be provided

        dc = DocumentContent(id=doc_id)

        self.assertEqual(dc.id, doc_id)
        self.assertIsNone(dc.abstract)
        self.assertIsNone(dc.summary)
        self.assertIsNone(dc.outline)
        self.assertEqual(dc.keywords, [])
        self.assertIsInstance(dc.keywords, list)
        self.assertIsNone(dc.language)
        self.assertIsNone(dc.page_count)
        self.assertIsNone(dc.file_type)
        self.assertIsNone(dc.encoding)
        self.assertEqual(dc.metadata, {})
        self.assertIsInstance(dc.metadata, dict)
        self.assertEqual(dc.segments, [])
        self.assertIsInstance(dc.segments, list)

    def test_instantiation_all_fields(self):
        """Test DocumentContent creation with all fields provided."""
        doc_id = str(uuid.uuid4())  # Example of a generated ID, but must be passed
        chunk1 = Chunk(content="First chunk")
        page1 = Page(url="https://example.com/page1", content="Page content")

        dc = DocumentContent(
            id=doc_id,
            abstract="This is an abstract.",
            summary="This is a summary.",
            outline="1. Point one\n2. Point two",
            keywords=["test", "document", "example"],
            language="en",
            page_count=5,
            file_type="application/pdf",
            encoding="UTF-8",
            metadata={"source": "upload", "version": "1.0"},
            segments=[chunk1, page1],
        )

        self.assertEqual(dc.id, doc_id)
        self.assertEqual(dc.abstract, "This is an abstract.")
        self.assertEqual(dc.summary, "This is a summary.")
        self.assertEqual(dc.outline, "1. Point one\n2. Point two")
        self.assertEqual(dc.keywords, ["test", "document", "example"])
        self.assertEqual(dc.language, "en")
        self.assertEqual(dc.page_count, 5)
        self.assertEqual(dc.file_type, "application/pdf")
        self.assertEqual(dc.encoding, "UTF-8")
        self.assertEqual(dc.metadata, {"source": "upload", "version": "1.0"})
        self.assertEqual(len(dc.segments), 2)
        self.assertIs(dc.segments[0], chunk1)
        self.assertIs(dc.segments[1], page1)

    def test_segments_field_mixed_types(self):
        """Test the 'segments' field can correctly hold Page and Chunk objects."""
        doc_id = "segments_test_doc"
        chunk1 = Chunk(content="Generic chunk data")
        page1 = Page(url="https://example.com/page1", content="Content of page 1")
        chunk2 = Chunk(id=str(uuid.uuid4()), content="Another chunk")

        dc = DocumentContent(id=doc_id, segments=[chunk1, page1, chunk2])

        self.assertEqual(dc.id, doc_id)
        self.assertEqual(len(dc.segments), 3)
        self.assertIs(dc.segments[0], chunk1)
        self.assertIsInstance(dc.segments[0], Chunk)
        self.assertIs(dc.segments[1], page1)
        self.assertIsInstance(dc.segments[1], Page)
        self.assertIs(dc.segments[2], chunk2)
        self.assertIsInstance(dc.segments[2], Chunk)

    def test_default_factories_for_keywords_metadata_segments(self):
        """Test default factory behaviors for keywords, metadata, and segments."""
        doc_id = "defaults_test_doc"

        # Instantiated with only the required 'id'
        dc = DocumentContent(id=doc_id)

        self.assertEqual(dc.keywords, [])
        self.assertIsInstance(dc.keywords, list)

        self.assertEqual(dc.metadata, {})
        self.assertIsInstance(dc.metadata, dict)

        self.assertEqual(dc.segments, [])
        self.assertIsInstance(dc.segments, list)

    def test_optional_fields_can_be_none_or_set(self):
        """Test that optional fields can be None or be set with values."""
        doc_id = "optional_fields_test"

        # Initial instantiation (all optionals should be None or default)
        dc1 = DocumentContent(id=doc_id)
        self.assertIsNone(dc1.abstract)
        self.assertIsNone(dc1.file_type)

        # Setting some optional fields
        dc2 = DocumentContent(id=doc_id, abstract="Test Abstract", file_type="text/markdown", language="fr")
        self.assertEqual(dc2.abstract, "Test Abstract")
        self.assertEqual(dc2.file_type, "text/markdown")
        self.assertEqual(dc2.language, "fr")


if __name__ == "__main__":
    unittest.main()
