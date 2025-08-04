# API Reference - Knowledge Forge API Documentation

## Overview

The API Reference directory contains comprehensive documentation for the Knowledge Forge API, providing detailed information about endpoints, data models, request/response formats, and integration patterns. This documentation serves as the authoritative reference for developers building applications with the Knowledge Forge API.

## Directory Structure

```
api_reference/
├── CLAUDE.md                      # This documentation file
├── overview.md                    # API overview and getting started guide
├── data_models.md                # Data structures and Pydantic models
├── files_api.md                  # File upload and management endpoints
├── response_generation_api.md    # Core response generation endpoints
├── server_status_api.md          # Server health and status endpoints
├── tasks_api.md                  # Async task management endpoints
├── tools_integration_api.md      # Tool integration and configuration
└── vector_stores_api.md          # Vector store operations and queries
```

## Documentation Structure

### Core API Documentation

#### overview.md - Getting Started

- **Purpose**: Introduction to the Knowledge Forge API
- **Content**: Authentication, base concepts, quick start examples
- **Audience**: New developers and API consumers
- **Key Topics**:
  - API authentication and configuration
  - Basic request/response patterns
  - Error handling and status codes
  - Rate limiting and best practices

#### data_models.md - Type Definitions

- **Purpose**: Comprehensive data model reference
- **Content**: Pydantic models, type definitions, validation rules
- **Audience**: SDK developers and type-aware consumers
- **Key Topics**:
  - Request and response models
  - Tool definition types
  - Validation schemas and constraints
  - Type safety patterns

### Core Functionality APIs

#### response_generation_api.md - Response Generation

- **Purpose**: Core AI response generation endpoints
- **Content**: Streaming and non-streaming response creation
- **Key Endpoints**:
  - `POST /api/responses` - Create responses
  - `GET /api/responses/{id}` - Retrieve responses
  - `POST /api/responses/stream` - Streaming responses
- **Features**:
  - Multi-turn conversations
  - Tool integration
  - Response customization
  - Streaming event types

#### files_api.md - File Management

- **Purpose**: File upload, processing, and management
- **Content**: File operations and metadata handling
- **Key Endpoints**:
  - `POST /api/files` - Upload files
  - `GET /api/files/{id}` - Retrieve file info
  - `DELETE /api/files/{id}` - Delete files
- **Features**:
  - Multiple file format support
  - Async processing with tasks
  - Metadata extraction
  - File validation

#### vector_stores_api.md - Vector Operations

- **Purpose**: Vector store creation and semantic search
- **Content**: Vector store management and querying
- **Key Endpoints**:
  - `POST /api/vector_stores` - Create vector stores
  - `GET /api/vector_stores/{id}` - Get vector store info
  - `POST /api/vector_stores/{id}/query` - Semantic search
  - `POST /api/vector_stores/{id}/files` - Add files
- **Features**:
  - Semantic search with filtering
  - Batch file operations
  - Query result ranking
  - Metadata management

### Supporting APIs

#### tasks_api.md - Task Management

- **Purpose**: Async task monitoring and management
- **Content**: Task lifecycle and status tracking
- **Key Endpoints**:
  - `GET /api/tasks/{id}` - Get task status
  - `POST /api/tasks/{id}/cancel` - Cancel tasks
- **Features**:
  - Progress tracking
  - Error handling
  - Task cancellation
  - Status notifications

#### tools_integration_api.md - Tool Integration

- **Purpose**: Tool configuration and integration patterns
- **Content**: Tool definitions and usage patterns
- **Key Topics**:
  - File search tool configuration
  - Web search tool setup
  - Code analyzer integration
  - Custom tool development
- **Features**:
  - Tool type definitions
  - Configuration validation
  - Result processing
  - Error handling

#### server_status_api.md - Health and Monitoring

- **Purpose**: Server health checks and system status
- **Content**: Monitoring endpoints and health indicators
- **Key Endpoints**:
  - `GET /api/health` - Health check
  - `GET /api/status` - System status
- **Features**:
  - Service availability
  - Performance metrics
  - Dependency status
  - Version information

## Documentation Standards

### API Endpoint Format

Each endpoint is documented with:

```markdown
## Endpoint Name

### Overview
Brief description of the endpoint's purpose

### Request
- **Method**: HTTP method (GET, POST, etc.)
- **URL**: `/api/endpoint/path`
- **Headers**: Required headers
- **Authentication**: Auth requirements
- **Parameters**: Query parameters
- **Body**: Request body schema

### Response
- **Status Codes**: Possible HTTP status codes
- **Headers**: Response headers
- **Body**: Response schema
- **Examples**: Sample responses

### Examples
- cURL examples
- Python SDK examples
- JavaScript examples
```

### Data Model Format

Data models are documented with:

```markdown
## Model Name

### Description
Purpose and usage of the model

### Fields
- **field_name** (type): Description and constraints
- **optional_field** (type, optional): Description with default

### Validation Rules
- Field constraints and validation logic
- Cross-field validation rules

### Examples
- JSON examples
- Pydantic model usage
```

## Usage Guidelines

### For API Consumers

1. **Start with Overview**: Read `overview.md` for basic concepts
2. **Check Data Models**: Review `data_models.md` for type definitions
3. **Find Your Endpoint**: Use specific API docs for implementation
4. **Follow Examples**: Use provided code examples as starting points
5. **Handle Errors**: Implement proper error handling patterns

### For SDK Developers

1. **Understand Types**: Study `data_models.md` thoroughly
2. **Follow Patterns**: Use established request/response patterns
3. **Implement Validation**: Use Pydantic models for type safety
4. **Handle Streaming**: Implement proper streaming event handling
5. **Test Thoroughly**: Validate against documented schemas

### For Integration Developers

1. **Review Tools API**: Understand tool integration patterns
2. **Check Task Management**: Implement async task handling
3. **Monitor Health**: Use health endpoints for monitoring
4. **Handle Rate Limits**: Implement proper rate limiting
5. **Follow Best Practices**: Use recommended patterns and practices

## Related Components

- **SDK Implementation** (`../../src/forge_cli/sdk/`) - Python SDK implementing these APIs
- **Response Types** (`../../src/forge_cli/response/_types/`) - Type definitions
- **Main Documentation** (`../CLAUDE.md`) - Project overview
- **ADRs** (`../adr/`) - Architectural decisions behind API design

## Contributing to API Documentation

### Adding New Endpoints

1. **Follow Format**: Use the standard endpoint documentation format
2. **Include Examples**: Provide working code examples
3. **Document Errors**: Include error cases and status codes
4. **Update Models**: Add new types to `data_models.md`
5. **Cross-Reference**: Link to related endpoints and concepts

### Updating Existing Documentation

1. **Keep Current**: Ensure examples work with latest API version
2. **Maintain Compatibility**: Document breaking changes clearly
3. **Update Types**: Keep data models in sync with implementation
4. **Test Examples**: Verify all code examples are functional
5. **Update Cross-References**: Maintain links to related documentation

## Best Practices

### Documentation Quality

1. **Clear Examples**: Every endpoint should have working examples
2. **Complete Schemas**: Document all request/response fields
3. **Error Handling**: Include comprehensive error documentation
4. **Type Safety**: Use proper type annotations throughout
5. **Consistent Format**: Follow established documentation patterns

### API Design Principles

1. **RESTful Design**: Follow REST principles for endpoint design
2. **Type Safety**: Use Pydantic models for validation
3. **Error Consistency**: Standardize error response formats
4. **Versioning**: Plan for API evolution and versioning
5. **Performance**: Document performance characteristics and limits

This API reference serves as the comprehensive guide for integrating with the Knowledge Forge API, providing all necessary information for successful implementation and integration.
