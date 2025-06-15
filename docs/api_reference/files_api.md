# File Management API

**Base Path:** `/v1/files`

Handles file upload, processing, and management with support for multiple formats and background processing.

## Upload File

**Endpoint:** `POST /v1/files`

```bash
curl -X POST "http://localhost:10000/v1/files" \
  -F "file=@document.pdf" \
  -F "purpose=qa" \
  -F "parse_options={\"abstract\": \"enable\", \"keywords\": \"enable\"}"
```

**Form Data Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | No* | File to upload (max 512MB) |
| `url` | string | No* | URL to download file from |
| `name` | string | No** | File name (required with URL) |
| `file_type` | string | No** | MIME type (required with URL) |
| `purpose` | string | No | Purpose: `qa`, `general` |
| `id` | string | No | Custom UUID for the file |
| `md5` | string | No | MD5 hash for deduplication |
| `parse_options` | string | No | JSON parsing configuration |
| `skip_exists` | boolean | No | Skip if file already exists |

*Either `file` or `url` must be provided
**Required when using `url`

**Parse Options:**

```json
{
  "abstract": "enable|disable",
  "summary": "enable|disable", 
  "outline": "enable|disable",
  "keywords": "enable|disable",
  "contexts": "enable|disable",
  "graph": "enable|disable"
}
```

**Response:**

```json
{
  "id": "file_abc123",
  "object": "file",
  "bytes": 1024000,
  "created_at": 1699061776,
  "filename": "document.pdf",
  "purpose": "qa",
  "task_id": "task_xyz789"
}
```

## Get File Content

**Endpoint:** `GET /v1/files/{file_id}/content`

Retrieves the full content and metadata of a specific file (document).

```bash
curl "http://localhost:10000/v1/files/file_abc123/content"
```

**Response:**

The response is a `Document` object with the following structure:

```json
{
  "id": "string", // Unique document identifier (UUID4)
  "md5sum": "string", // MD5 checksum of the original file
  "mime_type": "string", // MIME type of the original file
  "title": "string", // Title of the document
  "author": "string | null", // Author of the document
  "created_at": "string | null", // ISO 8601 datetime, e.g., "2023-10-26T07:42:05.123Z"
  "updated_at": "string | null", // ISO 8601 datetime
  "url": "string | null", // Original URL of the document, if applicable
  "metadata": {
    "additional_key": "value"
  }, // User-defined metadata
  "vector_store_ids": [
    "string"
  ], // List of vector store IDs this document is part of
  "content": { // DocumentContent object
    "id": "string", // MD5 checksum of the raw binary content (same as Document.md5sum)
    "abstract": "string | null",
    "summary": "string | null",
    "outline": "string | null",
    "keywords": [
      "string"
    ],
    "language": "string | null",
    "page_count": "integer | null",
    "file_type": "string | null", // e.g., "pdf", "docx"
    "segments": [ // List of Page or Chunk objects
      {
        // Example of a Page object
        "id": "string", // Specific format: <md5sum>-P<index:04d>, e.g., "abcdef...-P0001"
        "content": "string | null", // Text content of the page
        "index": "integer | null", // Page number (0-indexed)
        "metadata": {
          "additional_page_meta": "value"
        },
        "url": "string" // URL specific to this page, if any
      },
      {
        // Example of a Chunk object
        "id": "string", // Unique ID for the chunk (UUID4 or other format)
        "content": "string | null", // Text content of the chunk
        "index": "integer | null", // Index of the chunk within the document or a larger context
        "metadata": {
          "source_page_number": 1,
          "additional_chunk_meta": "value"
        }
      }
    ],
    "contexts": [
      // Structure of SingleContext (refer to _types/single_context.py if needed)
      {
        "context_id": "string",
        "text": "string",
        "metadata": {}
      }
    ],
    "images": [
      // Structure of SingleImage (refer to _types/single_image.py if needed)
      {
        "image_id": "string",
        "url": "string",
        "caption": "string | null",
        "metadata": {}
      }
    ],
    "graph": { 
      // Structure of Graph (refer to _types/graph.py if needed)
      "entities": [],
      "relationships": []
    }
  }
}
```

**Field Descriptions:**

* **Document Object:**
  * `id`: (string, UUID4) Unique identifier for the document entry in the system.
  * `md5sum`: (string) MD5 hash of the original uploaded file content.
  * `mime_type`: (string) MIME type of the original file (e.g., "application/pdf").
  * `title`: (string) The title of the document, often derived from filename or metadata.
  * `author`: (string, nullable) Author of the document, if known.
  * `created_at`: (string, ISO 8601 datetime, nullable) Timestamp of when the document was first processed.
  * `updated_at`: (string, ISO 8601 datetime, nullable) Timestamp of the last update to the document's record or content.
  * `url`: (string, nullable) The original URL from which the document was fetched, if applicable.
  * `metadata`: (object, nullable) A key-value store for any additional custom metadata associated with the document.
  * `vector_store_ids`: (array of strings, nullable) List of IDs of vector stores that include this document.
  * `content`: (DocumentContent object, nullable) Detailed parsed content of the document.

* **DocumentContent Object:** (Embedded within `Document.content`)
  * `id`: (string, MD5) MD5 hash of the raw binary content. This should match `Document.md5sum`.
  * `abstract`: (string, nullable) A generated or provided abstract of the document.
  * `summary`: (string, nullable) A generated or provided summary of the document.
  * `outline`: (string, nullable) A generated or provided outline of the document.
  * `keywords`: (array of strings) List of keywords extracted or associated with the document.
  * `language`: (string, nullable) Detected or specified language of the document (e.g., "en", "zh").
  * `page_count`: (integer, nullable) Total number of pages in the document.
  * `file_type`: (string, nullable) The file extension or format type (e.g., "pdf", "txt").
  * `segments`: (array of Page or Chunk objects) The main content of the document, broken down into segments. Each segment can be a `Page` or a `Chunk`.
    * **Page Object:** (Specialized `Chunk`)
      * `id`: (string) Formatted as `<md5sum>-P<index:04d>` (e.g., `d41d8cd98f00b204e9800998ecf8427e-P0001`).
      * `content`: (string, nullable) Text content of the page.
      * `index`: (integer, nullable) The page number (typically 0-indexed).
      * `metadata`: (object, nullable) Metadata specific to this page.
      * `url`: (string) URL that might point directly to this page or a representation of it.
    * **Chunk Object:**
      * `id`: (string, UUID4) Unique identifier for this specific chunk of text.
      * `content`: (string, nullable) The actual text content of the chunk.
      * `index`: (integer, nullable) Positional index of the chunk within a sequence or the document.
      * `metadata`: (object, nullable) Metadata specific to this chunk (e.g., source page, section).
  * `contexts`: (array of SingleContext objects, nullable) Additional contextual information related to the document.
  * `images`: (array of SingleImage objects, nullable) Information about images extracted from or related to the document.
  * `graph`: (Graph object, nullable) A knowledge graph representation derived from the document content, containing entities and relationships.

## Delete File

**Endpoint:** `DELETE /v1/files/{file_id}`

```bash
curl -X DELETE "http://localhost:10000/v1/files/file_abc123"
```

**Response:**

```json
{
  "id": "file_abc123",
  "object": "file",
  "deleted": true
}
```
