# Documentation Directory - Project Documentation Hub

## Overview

The `docs/` directory serves as the central documentation hub for the Forge CLI project. It contains comprehensive documentation including Architecture Decision Records (ADRs), API reference materials, historical documentation, and project requirements. This directory follows a structured approach to documentation that supports both developers and users of the Knowledge Forge API.

## Directory Structure

```
docs/
├── CLAUDE.md                          # This documentation file
├── adr/                              # Architecture Decision Records
│   ├── ADR-001-commandline-design.md
│   ├── ADR-002-reasoning-event-handling.md
│   ├── ADR-003-file-search-annotation-display.md
│   ├── ADR-004-snapshot-based-streaming-design.md
│   ├── ADR-005-interactive-chat-mode.md
│   ├── ADR-006-v2-event-based-display-architecture.md
│   ├── ADR-007-typed-only-architecture-migration.md
│   ├── ADR-008-v3-response-snapshot-display-architecture.md
│   ├── ADR-009-code-analyzer-tool.md
│   ├── ADR-010-response-type-guards.md
│   ├── ADR-011-tool-call-architecture.md
│   ├── ADR-012-chat-first-architecture-migration.md
│   ├── ADR-013-modular-chat-command-system.md
│   ├── ADR-014-configuration-system-refactoring.md
│   ├── ADR-015-modular-tool-renderer-architecture.md
│   └── ADR-016-simplified-tool-renderer-architecture.md
├── api_reference/                    # API documentation
│   ├── overview.md                   # API overview and getting started
│   ├── data_models.md               # Data structures and types
│   ├── files_api.md                 # File management endpoints
│   ├── response_generation_api.md   # Response generation endpoints
│   ├── server_status_api.md         # Server status and health
│   ├── tasks_api.md                 # Task management endpoints
│   ├── tools_integration_api.md     # Tool integration endpoints
│   └── vector_stores_api.md         # Vector store endpoints
├── historical/                      # Historical documentation
│   └── DEPRECATION_TIMELINE.md     # Timeline of deprecated features
├── conversation-state-tools.md      # Conversation state management
├── requirement.md                   # Project requirements
└── 财报/                           # Financial reports (example data)
    ├── 北森2023_2024年度报告.pdf
    ├── 北森2024_2025中期报告.pdf
    ├── 小米财报.pdf
    └── 小米集团2024年中期报告.pdf
```

## Documentation Philosophy

### Design Principles

1. **Decision Transparency**: All architectural decisions are documented with rationale
2. **API-First Documentation**: Comprehensive API reference with examples
3. **Historical Context**: Maintain records of deprecated features and migrations
4. **Living Documentation**: Documentation evolves with the codebase
5. **Developer-Focused**: Written for developers building with the Knowledge Forge API

### Documentation Types

#### Architecture Decision Records (ADRs)

- **Purpose**: Document significant architectural decisions and their rationale
- **Format**: Structured markdown with context, decision, and consequences
- **Audience**: Developers, architects, and maintainers
- **Location**: `docs/adr/`

#### API Reference

- **Purpose**: Comprehensive reference for all API endpoints and data models
- **Format**: Detailed markdown with examples and schemas
- **Audience**: API consumers and SDK developers
- **Location**: `docs/api_reference/`

#### Historical Documentation

- **Purpose**: Track deprecated features and migration timelines
- **Format**: Chronological records with migration guides
- **Audience**: Developers maintaining legacy integrations
- **Location**: `docs/historical/`

## Key Documentation Areas

### Architecture Decision Records (ADRs)

The ADR directory contains the complete history of architectural decisions:

**Core Architecture:**

- **ADR-001**: Command-line interface design principles
- **ADR-004**: Snapshot-based streaming design
- **ADR-007**: Migration to typed-only architecture
- **ADR-008**: V3 response-snapshot display architecture (current)

**Type System:**

- **ADR-010**: TypeGuard functions for Response types
- **ADR-011**: Tool call architecture design

**Display System:**

- **ADR-006**: V2 event-based display architecture (legacy)
- **ADR-015**: Modular tool renderer architecture
- **ADR-016**: Simplified tool renderer architecture

**Chat System:**

- **ADR-005**: Interactive chat mode implementation
- **ADR-012**: Chat-first architecture migration
- **ADR-013**: Modular chat command system

**Configuration:**

- **ADR-014**: Configuration system refactoring

### API Reference

Comprehensive documentation for the Knowledge Forge API:

- **overview.md**: Getting started guide and API concepts
- **data_models.md**: Pydantic models and type definitions
- **response_generation_api.md**: Core response generation endpoints
- **files_api.md**: File upload and management
- **vector_stores_api.md**: Vector store operations
- **tools_integration_api.md**: Tool integration patterns
- **tasks_api.md**: Async task management
- **server_status_api.md**: Health checks and monitoring

### Historical Documentation

- **DEPRECATION_TIMELINE.md**: Tracks deprecated features and migration paths

## Usage Guidelines

### For Developers

When working with the documentation:

1. **Read ADRs First**: Understand architectural decisions before making changes
2. **Update Documentation**: Keep docs in sync with code changes
3. **Follow Patterns**: Use existing ADR and API doc formats
4. **Reference Examples**: Use the main CLAUDE.md as a reference for style

### For API Consumers

1. **Start with Overview**: Begin with `api_reference/overview.md`
2. **Check Data Models**: Review `data_models.md` for type definitions
3. **Follow Examples**: Use code examples in API reference docs
4. **Check ADRs**: Understand design rationale for complex features

## Documentation Standards

### ADR Format

```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
Background and problem statement

## Decision
What was decided and why

## Consequences
Positive and negative outcomes
```

### API Documentation Format

```markdown
# Endpoint Name

## Overview
Brief description

## Request
- Method: POST/GET/etc
- URL: /api/endpoint
- Headers: Required headers
- Body: Request schema

## Response
- Status codes
- Response schema
- Examples

## Examples
Code examples in multiple languages
```

## Related Components

- **Main CLAUDE.md** (`/CLAUDE.md`) - Project overview and architecture
- **Source Code** (`src/`) - Implementation of documented features
- **Tests** (`tests/`) - Validation of documented behavior
- **Scripts** (`scripts/`) - Utility scripts referenced in documentation

## Contributing to Documentation

### Adding New ADRs

1. Use the next sequential number (ADR-017, ADR-018, etc.)
2. Follow the standard ADR format
3. Include context, decision, and consequences
4. Update the main CLAUDE.md if the decision affects overall architecture

### Updating API Documentation

1. Keep examples current with the latest API version
2. Include both request and response examples
3. Document error cases and status codes
4. Update data models when types change

### Maintaining Historical Records

1. Document deprecations in DEPRECATION_TIMELINE.md
2. Provide migration guides for breaking changes
3. Keep old documentation accessible for reference

## Best Practices

1. **Keep It Current**: Documentation should reflect the current state of the system
2. **Include Examples**: Every API endpoint should have working examples
3. **Explain Decisions**: ADRs should clearly explain the reasoning behind choices
4. **Link Related Docs**: Cross-reference related documentation
5. **Use Clear Language**: Write for developers who may be new to the project

This documentation directory serves as the authoritative source for understanding the Forge CLI architecture, API usage, and development practices. It supports both the development team and external users of the Knowledge Forge API.
