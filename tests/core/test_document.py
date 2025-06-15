import unittest
import uuid
from datetime import UTC, datetime

from forge_cli.core.chunk import Chunk
from forge_cli.core.document import Document
from forge_cli.core.document_content import DocumentContent


class TestDocument(unittest.TestCase):
    def test_instantiation_basic_required_fields(self):
        """Test Document instantiation with required fields and default optionals."""
        doc_id = str(uuid.uuid4())
        md5 = "d41d8cd98f00b204e9800998ecf8427e"  # example md5
        mime = "text/plain"
        doc_title = "My Test Document"

        doc = Document(id=doc_id, md5sum=md5, mime_type=mime, title=doc_title)

        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.md5sum, md5)
        self.assertEqual(doc.mime_type, mime)
        self.assertEqual(doc.title, doc_title)

        self.assertIsNone(doc.author)
        self.assertIsNone(doc.created_at)
        self.assertIsNone(doc.updated_at)
        self.assertIsNone(doc.url)
        self.assertIsNone(doc.content)

        self.assertEqual(doc.metadata, {})
        self.assertIsInstance(doc.metadata, dict)
        self.assertEqual(doc.vector_store_ids, [])
        self.assertIsInstance(doc.vector_store_ids, list)

    def test_instantiation_all_fields(self):
        """Test Document creation with all fields provided."""
        doc_id = str(uuid.uuid4())
        md5 = "c3fce381355973c6fc6262b32f7a8a21"
        mime = "application/pdf"
        doc_title = "Comprehensive Document"

        # Create a DocumentContent object
        dc_id = "dc_content_id_001"  # DocumentContent also requires an id
        doc_content_obj = DocumentContent(
            id=dc_id, abstract="Abstract of content.", segments=[Chunk(content="chunk in content")]
        )

        custom_metadata = {"category": "testing", "status": "draft"}
        vector_ids = ["vs_1", "vs_2"]
        now = datetime.now(UTC)
        specific_url = "https://example.com/document.pdf"
        specific_author = "Test Author"

        doc = Document(
            id=doc_id,
            md5sum=md5,
            mime_type=mime,
            title=doc_title,
            author=specific_author,
            created_at=now,
            updated_at=now,
            url=specific_url,
            metadata=custom_metadata,
            vector_store_ids=vector_ids,
            content=doc_content_obj,
        )

        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.md5sum, md5)
        self.assertEqual(doc.mime_type, mime)
        self.assertEqual(doc.title, doc_title)
        self.assertEqual(doc.author, specific_author)
        self.assertEqual(doc.created_at, now)
        self.assertEqual(doc.updated_at, now)
        self.assertEqual(doc.url, specific_url)
        self.assertEqual(doc.metadata, custom_metadata)
        self.assertEqual(doc.vector_store_ids, vector_ids)
        self.assertIs(doc.content, doc_content_obj)
        self.assertIsInstance(doc.content, DocumentContent)

    def test_content_field_with_document_content(self):
        """Test assigning a DocumentContent object to the 'content' field."""
        doc_id = str(uuid.uuid4())
        md5 = "b026324c6904b2a9cb4b88d6d61c81d1"
        mime = "application/json"
        doc_title = "Document with Content"

        dc_id = "dc_for_doc_002"  # DocumentContent requires an id
        doc_content_obj = DocumentContent(id=dc_id, file_type="text/plain")

        doc_with_content = Document(id=doc_id, md5sum=md5, mime_type=mime, title=doc_title, content=doc_content_obj)
        self.assertIs(doc_with_content.content, doc_content_obj)
        self.assertIsInstance(doc_with_content.content, DocumentContent)

        # Test with content being None (which is its default)
        doc_no_content = Document(
            id=str(uuid.uuid4()), md5sum="another_md5", mime_type="text/xml", title="Doc No Content"
        )
        self.assertIsNone(doc_no_content.content)

    def test_default_factories_for_metadata_and_vector_store_ids(self):
        """Test default factory behaviors for metadata and vector_store_ids."""
        doc_id = str(uuid.uuid4())
        md5 = "6f1ed002ab5595859014ebf0951522d9"
        mime = "image/png"
        doc_title = "Document For Defaults Test"

        doc = Document(id=doc_id, md5sum=md5, mime_type=mime, title=doc_title)

        self.assertEqual(doc.metadata, {})
        self.assertIsInstance(doc.metadata, dict)
        self.assertEqual(doc.vector_store_ids, [])
        self.assertIsInstance(doc.vector_store_ids, list)

    def test_datetime_fields_created_updated_at(self):
        """Test the behavior of created_at and updated_at fields."""
        doc_id = str(uuid.uuid4())
        md5 = "098f6bcd4621d373cade4e832627b4f6"
        mime = "text/calendar"
        doc_title = "Datetime Test Doc"

        # Test when not provided (should be None)
        doc_no_dt = Document(id=doc_id, md5sum=md5, mime_type=mime, title=doc_title)
        self.assertIsNone(doc_no_dt.created_at)
        self.assertIsNone(doc_no_dt.updated_at)

        # Test providing specific datetimes
        specific_created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
        specific_updated_at = datetime(2023, 1, 2, 12, 0, 0, tzinfo=UTC)

        doc_specific_dt = Document(
            id=str(uuid.uuid4()),
            md5sum="anothermd5",
            mime_type=mime,
            title="Specific DT Doc",
            created_at=specific_created_at,
            updated_at=specific_updated_at,
        )
        self.assertEqual(doc_specific_dt.created_at, specific_created_at)
        self.assertEqual(doc_specific_dt.updated_at, specific_updated_at)


if __name__ == "__main__":
    unittest.main()
