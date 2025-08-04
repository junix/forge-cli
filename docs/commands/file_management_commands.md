# File Management Commands Documentation

This document describes the file management commands for adding and removing files from collections in the Knowledge Forge CLI.

## Overview

The Knowledge Forge CLI provides intuitive commands for managing files within collections:

- `/join-file` / `/join-docs` - Add files to collections
- `/left-file` / `/leave-docs` - Remove files from collections

These commands provide a natural, symmetric interface for file collection management.

## Join Commands

### Join File Command

#### Syntax
```bash
/join-file <collection_id> <file_id>
/join-docs <collection_id> [file_id1] [file_id2] ...
```

#### Aliases
- `/join-file` - Join a single file
- `/join-docs` - Join multiple documents  
- `/join` - Short alias
- `/add-to-collection` - Descriptive alias

#### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_id` | string | ID of the target vector store collection |
| `file_id` | string | ID of the file to add (optional for join-docs) |

#### Examples

##### Basic Usage
```bash
# Join a single file to a collection
/join-file vs_research doc_123

# Join multiple specific files
/join-docs vs_research doc_123 doc_456 doc_789

# Join all uploaded documents
/join-docs vs_research
```

##### Workflow Example
```bash
# 1. Upload documents
/upload /path/to/paper1.pdf
/upload /path/to/paper2.pdf

# 2. Create collection
/new-collection name="Research Papers" desc="AI research collection"

# 3. Join files to collection
/join-docs vs_abc123  # Joins all uploaded documents
```

#### Response Format
```
🔗 Joining 2 document(s) to vector store: vs_abc123
✅ Successfully joined 2 document(s) to vector store
📚 Vector store vs_abc123 added to conversation
  📄 paper1.pdf (ID: doc_123)
  📄 paper2.pdf (ID: doc_456)
```

## Leave Commands

### Leave File Command

#### Syntax
```bash
/left-file <collection_id> <file_id>
/leave-docs <collection_id> <file_id1> [file_id2] ...
```

#### Aliases
- `/left-file` - Remove a single file
- `/leave-docs` - Remove multiple documents
- `/leave-file` - Alternative single file alias
- `/remove-file` - Descriptive single file alias
- `/remove-files` - Descriptive multiple files alias
- `/remove-from-collection` - Full descriptive alias

#### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_id` | string | ID of the target vector store collection |
| `file_id` | string | ID of the file to remove |

#### Examples

##### Basic Usage
```bash
# Remove a single file from collection
/left-file vs_research doc_123

# Remove multiple files from collection
/leave-docs vs_research doc_456 doc_789

# Using alternative aliases
/remove-file vs_research doc_123
/remove-from-collection vs_research doc_456
```

#### Response Format
```
🗑️  Removing 1 file(s) from vector store: vs_research
✅ Successfully removed 1 file(s) from vector store
  🗑️  Removed: doc_123
📁 Remaining files in collection: 5
```

## Command Symmetry

The join/leave commands are designed to be intuitive counterparts:

| Action | Single File | Multiple Files |
|--------|-------------|----------------|
| **Add** | `/join-file vs_123 doc_456` | `/join-docs vs_123 doc_1 doc_2` |
| **Remove** | `/left-file vs_123 doc_456` | `/leave-docs vs_123 doc_1 doc_2` |

## Integration with Other Commands

### Discovery Commands
```bash
# See available collections
/show-collections

# See files in a collection
/show-collection vs_123

# See all uploaded documents
/documents
```

### Management Workflow
```bash
# 1. Check current collection contents
/show-collection vs_research

# 2. Add new files
/join-file vs_research doc_new

# 3. Remove outdated files
/left-file vs_research doc_old

# 4. Verify changes
/show-collection vs_research
```

## Error Handling

### Common Errors

#### Join Commands
```bash
# No uploaded documents
/join-docs vs_123
❌ No uploaded documents found
💡 Use '/upload <file_path>' to upload documents first

# Invalid document ID
/join-file vs_123 invalid_doc
❌ Document ID not found: invalid_doc

# Missing collection ID
/join-file
📋 Usage: /join-docs <vector_store_id> [document_ids...]
```

#### Leave Commands
```bash
# Missing file ID
/left-file vs_123
❌ Both vector store ID and file ID(s) are required

# Collection not found
/left-file invalid_vs doc_123
❌ Failed to remove files from vector store

# Missing arguments
/left-file
📋 Usage: /left-file <vector_store_id> <file_id> [file_id2...]
```

## Best Practices

### 1. File Discovery
Always check available files before joining:
```bash
# Check uploaded documents
/documents

# Check collection contents
/show-collection vs_123
```

### 2. Batch Operations
Use appropriate commands for single vs. multiple files:
```bash
# Good: Single file operations
/join-file vs_research doc_123
/left-file vs_research doc_456

# Good: Multiple file operations  
/join-docs vs_research doc_1 doc_2 doc_3
/leave-docs vs_research doc_4 doc_5
```

### 3. Verification
Verify changes after file operations:
```bash
# After joining/leaving files
/show-collection vs_research
```

### 4. Workflow Organization
```bash
# Organized workflow
/upload /path/to/new_paper.pdf          # 1. Upload
/join-file vs_research doc_new           # 2. Add to collection
/left-file vs_research doc_outdated     # 3. Remove old files
/show-collection vs_research             # 4. Verify
```

## Advanced Usage

### Conditional File Management
```bash
# Add files based on content type
/join-docs vs_papers doc_research1 doc_research2
/join-docs vs_tutorials doc_tutorial1 doc_tutorial2

# Remove files by category
/leave-docs vs_archive doc_old1 doc_old2 doc_old3
```

### Collection Reorganization
```bash
# Move files between collections
/left-file vs_general doc_123           # Remove from general
/join-file vs_specialized doc_123       # Add to specialized
```

## API Integration

These commands use the Knowledge Forge REST API:

### Join Operations
- **Endpoint**: `POST /v1/vector_stores/{id}`
- **Payload**: `{"join_file_ids": ["file1", "file2"]}`

### Leave Operations  
- **Endpoint**: `POST /v1/vector_stores/{id}`
- **Payload**: `{"left_file_ids": ["file1", "file2"]}`

## Related Commands

| Command | Purpose |
|---------|---------|
| `/upload` | Upload files to make them available for joining |
| `/documents` | List all uploaded documents |
| `/show-collection` | View collection contents |
| `/new-collection` | Create new collections |
| `/update-collection` | Bulk file management with other updates |

The join/leave commands provide an intuitive, symmetric interface for file collection management, making it easy to organize and reorganize your document collections as needed.
