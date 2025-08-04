# Update Commands Documentation

This document describes the update commands for modifying documents and collections in the Knowledge Forge CLI.

## Overview

The Knowledge Forge CLI provides comprehensive update commands for both documents and collections:

- `/update-collection` - Update collection metadata, files, and settings
- `/update-document` - Update document metadata, properties, and user data

## Collection Update Command

### Syntax

```bash
/update-collection <collection_id> [options]
```

### Aliases

- `/update-vs`
- `/modify-collection`
- `/modify-vs`
- `/edit-collection`

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--name` | string | Update collection name |
| `--description` | string | Update collection description |
| `--metadata` | string | Update metadata (key:value,key:value format) |
| `--expires-after` | integer | Set expiration time in seconds |
| `--add-files` | string | Add files (comma-separated file IDs) |
| `--remove-files` | string | Remove files (comma-separated file IDs) |

### Examples

#### Basic Updates
```bash
# Update collection name
/update-collection vs_123 --name="New Collection Name"

# Update description
/update-collection vs_123 --description="Updated description"

# Set expiration
/update-collection vs_123 --expires-after=3600
```

#### Metadata Updates
```bash
# Update metadata
/update-collection vs_123 --metadata="domain:research,priority:high,status:active"
```

#### File Management
```bash
# Add files to collection
/update-collection vs_123 --add-files="file1,file2,file3"

# Remove files from collection
/update-collection vs_123 --remove-files="file4,file5"

# Add and remove files in one command
/update-collection vs_123 --add-files="new1,new2" --remove-files="old1,old2"
```

#### Combined Updates
```bash
# Update multiple properties at once
/update-collection vs_123 --name="Research Papers" --description="AI research collection" --add-files="doc1,doc2"
```

## Document Update Command

### Syntax

```bash
/update-document <document_id> [options]
```

### Aliases

- `/update-doc`
- `/modify-document`
- `/modify-doc`
- `/edit-document`
- `/edit-doc`

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--title` | string | Update document title |
| `--author` | string | Update document author |
| `--owner` | string | Update document owner |
| `--is-favorite` | boolean | Set favorite status (true/false) |
| `--read-progress` | float | Set reading progress (0.0 to 1.0) |
| `--bookmarks` | string | Set bookmarks (comma-separated page numbers) |
| `--highlights` | string | Set highlights (comma-separated text snippets) |
| `--notes` | string | Set notes (comma-separated notes) |
| `--related-docs` | string | Set related documents (comma-separated doc IDs) |
| `--permissions` | string | Set permissions (comma-separated permissions) |
| `--metadata` | string | Update metadata (key:value,key:value format) |
| `--vector-store-ids` | string | Set vector store associations (comma-separated IDs) |

### Examples

#### Basic Updates
```bash
# Update title and author
/update-document doc_123 --title="New Document Title" --author="John Doe"

# Mark as favorite
/update-document doc_123 --is-favorite=true

# Update owner
/update-document doc_123 --owner="user456"
```

#### Progress & Bookmarks
```bash
# Set reading progress to 75%
/update-document doc_123 --read-progress=0.75

# Add bookmarks
/update-document doc_123 --bookmarks="10,25,50,75"
```

#### Notes & Highlights
```bash
# Add notes
/update-document doc_123 --notes="Important finding,Follow up needed,Key insight"

# Add highlights
/update-document doc_123 --highlights="key insight,important quote,critical data"
```

#### Metadata & Relations
```bash
# Update metadata
/update-document doc_123 --metadata="category:research,priority:high,status:reviewed"

# Set related documents
/update-document doc_123 --related-docs="doc_456,doc_789,doc_101"

# Associate with vector stores
/update-document doc_123 --vector-store-ids="vs_abc,vs_def"
```

#### Combined Updates
```bash
# Update multiple properties
/update-document doc_123 --title="Research Paper" --author="Dr. Smith" --is-favorite=true --read-progress=0.5
```

## Response Format

### Successful Collection Update
```
🔄 Updating collection: vs_123
  📝 Name: New Collection Name
  📄 Description: Updated description
  🏷️  Metadata: 3 key(s)
  ➕ Adding files: 2 file(s)
✅ Collection updated successfully!
📦 Name: New Collection Name
🆔 ID: vs_123
📄 Description: Updated description
📁 Files: 5
```

### Successful Document Update
```
🔄 Updating document: doc_123
  📝 Title: New Document Title
  👤 Author: John Doe
  ⭐ Favorite: true
  📊 Read progress: 75.0%
✅ Document updated successfully!
📄 ID: doc_123
📝 Title: New Document Title
🕒 Updated: 2024-01-15T10:30:00Z
```

## Error Handling

### Common Errors

1. **Missing ID**: Collection/document ID is required
2. **No Parameters**: At least one update parameter is required
3. **Invalid Progress**: Read progress must be between 0.0 and 1.0
4. **Invalid Expiration**: Expires-after must be a number
5. **Not Found**: Collection/document doesn't exist
6. **Permission Denied**: Insufficient permissions to update

### Error Examples

```bash
# Missing ID
/update-collection
❌ Collection ID is required

# No parameters
/update-collection vs_123
❌ At least one update parameter is required

# Invalid progress
/update-document doc_123 --read-progress=1.5
❌ read_progress must be between 0.0 and 1.0
```

## Best Practices

### 1. Incremental Updates
Update only the fields you need to change:
```bash
# Good: Update only what's needed
/update-document doc_123 --title="New Title"

# Avoid: Updating everything unnecessarily
```

### 2. Metadata Format
Use consistent key:value format for metadata:
```bash
# Good: Clear key-value pairs
--metadata="category:research,priority:high,status:active"

# Avoid: Inconsistent formatting
--metadata="category research, priority=high"
```

### 3. File Management
Use descriptive file operations:
```bash
# Good: Clear intent
/update-collection vs_123 --add-files="new_research_paper,updated_analysis"

# Good: Batch operations
/update-collection vs_123 --add-files="file1,file2" --remove-files="old_file1,old_file2"
```

### 4. Progress Tracking
Use decimal values for progress:
```bash
# Good: Precise progress
--read-progress=0.75  # 75%

# Good: Common values
--read-progress=0.0   # Not started
--read-progress=0.5   # Half way
--read-progress=1.0   # Complete
```

## Integration with Other Commands

### Workflow Examples

```bash
# 1. Create collection
/new-collection name="Research Papers" desc="AI research collection"

# 2. Add documents
/upload /path/to/paper1.pdf
/upload /path/to/paper2.pdf

# 3. Update collection with documents
/update-collection vs_123 --add-files="file_abc,file_def"

# 4. Update document metadata
/update-document file_abc --title="Transformer Architecture" --metadata="category:deep_learning"

# 5. Track reading progress
/update-document file_abc --read-progress=0.8 --bookmarks="15,23,45"
```

## API Compatibility

These commands use the Knowledge Forge REST API endpoints:

- Collection updates: `POST /v1/vector_stores/{id}`
- Document updates: `POST /v1/files/{id}/content`

The commands provide a user-friendly interface to these API endpoints with proper error handling and validation.
