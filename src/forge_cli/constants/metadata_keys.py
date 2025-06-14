"""
Constants for metadata keys used in Chunk objects.

This module defines standard keys for storing document information in Chunk metadata.
Using these constants ensures consistency across the codebase when accessing
document-related information from Chunk objects.
"""

# Document metadata keys
DOC_ID_KEY = "doc_id"
DOC_TITLE_KEY = "doc_title"
DOC_URL_KEY = "doc_url"
DOC_SOURCE_KEY = "doc_source"  # Optional, for tracking document source
DOCUMENT_TITLE_KEY = "document_title"  # Alternative to doc_title used in some places

# Segment metadata keys
SEGMENT_TYPE_KEY = "segment_type"  # "chunk", "page", "summary", "keywords", "whole_document"
SEGMENT_INDEX_KEY = "segment_index"
PAGE_INDEX_KEY = "page_index"
PAGE_NUMBER_KEY = "page_number"
PAGE_URL_KEY = "page_url"
URL_KEY = "url"  # Generic URL key

# Content metadata keys
ABSTRACT_KEY = "abstract"
SUMMARY_KEY = "summary"
KEYWORDS_KEY = "keywords"
LANGUAGE_KEY = "language"

# File metadata keys
FILE_ID_KEY = "file_id"
FILES_KEY = "files"
FILES_UPDATED_AT_KEY = "files_updated_at"
PARENT_MD5_KEY = "parent_md5"

# Quality metadata keys
IS_SCANNED_KEY = "is_scanned"
TEXT_EXTRACTION_CONFIDENCE_KEY = "text_extraction_confidence"

# Search/retrieval metadata keys
SCORE_KEY = "score"
DISTANCE_KEY = "distance"
QUERY_KEY = "query"

# Collection metadata keys
COLLECTION_NAME_KEY = "collection_name"

# Other metadata keys
ERROR_KEY = "error"
MIME_TYPE_KEY = "mime_type"
AUTHOR_KEY = "author"
CREATED_AT_KEY = "created_at"
