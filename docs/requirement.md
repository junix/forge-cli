# Custom System Prompt Requirements

## Overview

This specification defines the requirements for allowing users to customize the role and response style (tune) in the low effort mode of the Knowledge Forge response service. Users should be able to specify custom assistant roles and response styles to tailor the AI's behavior to their specific needs.

## Business Requirements

### BR-1: User Role Customization

- **Requirement**: Users must be able to specify a custom role for the AI assistant
- **Rationale**: Different use cases require different assistant personas (e.g., technical expert, creative writer, business analyst)
- **Acceptance Criteria**:
  - Users can provide a custom role description in their request
  - The role description replaces or enhances the default company-based role
  - Role customization works in low effort mode without affecting other effort levels

### BR-2: Response Style Tuning

- **Requirement**: Users must be able to customize the response style and tone
- **Rationale**: Different contexts require different communication styles (formal vs casual, technical vs simple, etc.)
- **Acceptance Criteria**:
  - Users can specify tone (e.g., professional, casual, friendly, formal)
  - Users can specify format preferences (e.g., bullet points, paragraphs, structured)
  - Users can specify verbosity level (e.g., concise, detailed, comprehensive)
  - Users can specify language complexity (e.g., simple, technical, academic)

### BR-3: Response Language Selection

- **Requirement**: Users must be able to specify the response language
- **Rationale**: Global users need responses in their preferred language for better comprehension and usability
- **Acceptance Criteria**:
  - Users can specify response language (e.g., Chinese, English, Spanish, French, etc.)
  - Language selection overrides any language hints in the input
  - System maintains consistent language throughout the response
  - Language selection works with all other customization options

### BR-4: Backward Compatibility

- **Requirement**: Existing functionality must remain unchanged when custom parameters are not provided
- **Rationale**: Ensure no breaking changes for current users
- **Acceptance Criteria**:
  - Default behavior remains identical when no custom role/style is specified
  - All existing API contracts are preserved
  - No performance degradation for default use cases

## Functional Requirements

### FR-1: Instructions Field Enhancement

- **Requirement**: Enhance the existing instructions field to support JSON-formatted custom parameters
- **Details**:
  - Parse JSON content from instructions field when present
  - Extract `custom_role` and `response_style` from parsed JSON
  - Maintain backward compatibility with plain text instructions
  - Support both JSON and plain text formats in the same field

### FR-2: JSON Parsing and Validation

- **Requirement**: Implement robust JSON parsing for instructions field content
- **Details**:
  - Detect JSON format vs plain text in instructions field
  - Parse and validate JSON structure when detected
  - Extract custom parameters with proper error handling
  - Fallback to plain text processing for invalid JSON

### FR-3: System Prompt Generation

- **Requirement**: Modify system prompt generation to incorporate parsed custom parameters
- **Details**:
  - Integrate custom role into the role section of system prompts
  - Apply style parameters to the SystemPromptBuilder
  - Maintain proper prompt structure and ordering
  - Combine custom parameters with any remaining plain text instructions

### FR-4: Low Effort Service Integration

- **Requirement**: Update low effort service to parse and use custom parameters when available
- **Details**:
  - Parse instructions field for JSON content
  - Extract custom parameters from parsed JSON
  - Pass parameters to PromptFactory
  - Generate customized system prompts

### FR-5: Template Enhancement

- **Requirement**: Enhance role template to support custom role descriptions
- **Details**:
  - Modify role_definition.j2 template to accept custom role content
  - Maintain company name integration when provided
  - Support fallback to default role when custom role is not specified

## Non-Functional Requirements

### NFR-1: Performance

- **Requirement**: Custom prompt generation must not significantly impact response time
- **Acceptance Criteria**:
  - Less than 50ms additional latency for custom prompt generation
  - Template rendering remains cached and efficient

### NFR-2: Validation

- **Requirement**: Input validation for custom parameters
- **Acceptance Criteria**:
  - Custom role length limits (e.g., max 1000 characters)
  - Style parameter validation against allowed values
  - Graceful handling of invalid parameters

### NFR-3: Security

- **Requirement**: Custom role content must be sanitized
- **Acceptance Criteria**:
  - No injection attacks through custom role content
  - Content filtering for inappropriate material
  - Rate limiting for custom prompt requests

## User Stories

### US-1: Technical Documentation Assistant

**As a** software developer
**I want to** set the AI role as "technical documentation expert"
**So that** responses are focused on code examples and technical accuracy

### US-2: Creative Writing Helper

**As a** content creator
**I want to** set a casual, creative tone with detailed responses
**So that** the AI helps with brainstorming and creative writing tasks

### US-3: Business Analyst Assistant

**As a** business analyst
**I want to** set a professional tone with structured, concise responses
**So that** the AI provides clear business insights and recommendations

### US-4: Educational Tutor

**As a** educator
**I want to** set a patient, encouraging role with simple language
**So that** the AI can effectively help students learn complex topics

### US-5: Multilingual Support

**As a** non-English speaker
**I want to** specify Chinese as my response language
**So that** I can understand the AI responses in my native language

## API Design Requirements

### Request Schema Extension

The custom role and response style parameters should be embedded as JSON string within the request's instructions field:

```json
{
  "model": "string",
  "input": "string|array",
  "effort": "low",
  "instructions": "string (JSON format)"
}
```

#### Instructions Field Content (JSON String)

The `instructions` field should contain a JSON string with the following structure:

```json
{
  "custom_role": "string (optional)",
  "response_style": {
    "tone": "string (optional)",
    "format": "string (optional)",
    "verbosity": "string (optional)",
    "language_level": "string (optional)",
    "language": "string (optional)"
  }
}
```

#### Example Request

```json
{
  "model": "gpt-4",
  "input": "Explain machine learning",
  "effort": "low",
  "instructions": "{\"custom_role\": \"technical documentation expert\", \"response_style\": {\"tone\": \"professional\", \"format\": \"structured\", \"verbosity\": \"detailed\", \"language\": \"english\"}}"
}
```

### Style Parameter Values

- **tone**: professional, casual, friendly, formal, technical, creative
- **format**: bullet_points, paragraphs, structured, conversational
- **verbosity**: concise, detailed, comprehensive
- **language_level**: simple, intermediate, technical, academic
- **language**: chinese, english, spanish, french, german, japanese, korean, portuguese, russian, arabic

## Constraints and Limitations

### C-1: Effort Level Scope

- Custom role/style only applies to low effort mode initially
- Medium and high effort modes maintain existing behavior
- Future expansion to other effort levels is out of scope

### C-2: Template Compatibility

- Must work with existing Jinja2 template system
- No breaking changes to template structure
- Maintain template caching performance

### C-3: Model Compatibility

- Custom prompts must work with all supported LLM models
- No model-specific prompt variations required
- Maintain consistent behavior across models

## Success Metrics

### M-1: Adoption

- 20% of low effort requests use custom parameters within 3 months
- User satisfaction score improvement for customized responses

### M-2: Performance

- No measurable impact on default request latency
- Custom prompt generation under 50ms

### M-3: Quality

- Reduced user complaints about inappropriate response style
- Increased task completion rates for role-specific use cases
