# Knowledge Forge Constants Module

## Overview

The Constants module provides centralized definitions for standard constants used throughout Knowledge Forge, ensuring consistency in naming conventions, reducing magic strings, and providing a single source of truth for system-wide identifiers and metadata keys.

## Architecture

```
constants/
├── metadata_keys.py    # Standard metadata field names and keys
└── tool_names.py       # Tool name constants and identifiers
```

## Features

### Metadata Standardization
- **Document Metadata**: Standardized field names for document properties, source information, and processing details
- **Chunk Metadata**: Consistent identifiers for chunk properties, relationships, and content characteristics
- **Citation Metadata**: Standard fields for citation tracking, confidence scores, and source references
- **Processing Metadata**: Timestamp, version, and method tracking for all processing operations

### Tool Identification
- **Search Tools**: Standardized identifiers for file search, web search, semantic search, and hybrid search tools
- **Document Tools**: Constants for document parsers, extractors, analyzers, and conversion tools
- **Analysis Tools**: Identifiers for sentiment analysis, entity extraction, and topic classification tools
- **Integration Tools**: Standard names for database queries, API calls, and data transformation tools

### System Integration
- **Validation Framework**: Built-in validation rules for metadata fields and tool names
- **Category Organization**: Logical grouping of constants by functional domain
- **Extension Patterns**: Structured approach for adding new constants while maintaining consistency
- **Namespace Management**: Organized access to related constants through namespace classes

## Integration Patterns

### Document Processing Pipeline
Provides standardized metadata fields used throughout the document ingestion, parsing, chunking, and indexing pipeline, ensuring consistent data structure across all processing stages.

### Tool System Integration
Defines standard tool identifiers used by the tool execution framework, enabling consistent tool registration, validation, and execution across the system.

### Citation System Support
Supplies standardized metadata keys for the citation system, ensuring consistent tracking of source references, confidence scores, and citation relationships. Supports both display and reference ID management patterns.

### Validation and Quality Assurance
Enables system-wide validation of metadata completeness and tool name correctness, supporting quality assurance and error prevention throughout the application.

## Best Practices

### Naming Conventions
- Use descriptive, uppercase constants with underscore separation
- Follow domain-specific prefixes (DOCUMENT_, CHUNK_, TOOL_, etc.)
- Maintain consistent naming patterns across related constants
- Document the purpose and usage of each constant

### Metadata Management
- Always use defined constants instead of magic strings
- Validate metadata completeness using required field sets
- Implement type checking for critical metadata fields
- Maintain backward compatibility when evolving constants

### Tool Integration
- Register tools using standard tool name constants
- Validate tool names before execution
- Use category-based tool organization for management
- Implement proper error handling for unknown tool types

### Extension Guidelines
- Follow established naming conventions for new constants
- Group related constants in appropriate modules
- Update validation rules when adding new constants
- Document integration patterns for new constant categories

## Related Modules

- **_types/**: Core data types that use standardized metadata keys
- **tools/**: Tool system that relies on tool name constants
- **citation/**: Citation system using citation metadata constants
- **chunking/**: Document chunking using chunk metadata keys
- **doc_parser/**: Document parsing using document metadata keys
- **rag/**: RAG pipeline using all metadata and tool constants

## Key ADRs

### Metadata & Constants
- **ADR-027**: Chunk Formatting Citation Index - Metadata key usage in chunk formatting
- **ADR-034**: Chunk Metadata Property Access - Standardized metadata access patterns
- **ADR-043**: Type-Based Tool Call Detection - Tool name constant usage in detection

### Citation System
- 🆕 **ADR-071**: Citation Display vs Reference ID Separation - Citation metadata key standards

### Context Management
- 🆕 **ADR-072**: Response Chunk Compression Strategies - Metadata keys for compression tracking
