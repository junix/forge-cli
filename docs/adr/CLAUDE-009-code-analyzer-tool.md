# ADR-009: Code Analyzer Tool Integration

## Status
Draft

## Context
The Forge CLI aims to provide a comprehensive suite of tools for developers. Analyzing source code for quality, potential issues, or specific patterns is a common developer task that can be enhanced by AI and integrated into the existing CLI framework. This ADR proposes the integration of a new 'Code Analyzer' tool.

## Decision
We will implement a 'Code Analyzer' tool within the Forge CLI, adhering to the existing SDK-first, async, and modular processor architecture.

### 1. Functionality
The Code Analyzer tool will:
- Accept a file path or directory path to source code.
- Optionally accept specific analysis types (e.g., "complexity", "style_check", "custom_query").
- Perform analysis on the specified code.
- Stream results, including identified issues, code snippets, and suggestions.

### 2. CLI Integration
- **Tool Invocation**: The tool will be invokable via `forge-cli -t code-analyzer`.
- **Primary Argument**: A `--path <path_to_code>` argument will specify the target code.
- **Optional Query**: A `-q <query_string>` or specific arguments like `--analysis-types type1 type2` can be used to guide the analysis (e.g., "find all TODO comments", "identify functions with high cyclomatic complexity").
- **Example**: `forge-cli -t code-analyzer --path ./my_project -q "Find unused imports"`

### 3. SDK Integration
- A new SDK function `async_analyze_code` will be added to `forge_cli.sdk`.
- **Signature**: `async def async_analyze_code(path: str, analysis_types: Optional[List[str]] = None, query: Optional[str] = None, output_format: str = "text", **kwargs) -> AsyncIterator[Tuple[str, dict]]:` (Signature is an example, may evolve).
- This function will handle communication with the Knowledge Forge API endpoint responsible for code analysis.

### 4. Processor Architecture
- A new `CodeAnalyzerProcessor` will be created in `src/forge_cli/processors/tool_calls/code_analyzer.py`.
- It will handle events specific to the code analyzer tool.
- It will be registered in `ProcessorRegistry` for the `code_analyzer_call` event type.

### 5. Event Types
The following new event types will be introduced:
- `response.code_analyzer_call.analyzing`: Indicates the start of a code analysis process.
- `response.code_analyzer_call.progress`: (Optional) Indicates progress of a long-running analysis.
- `response.code_analysis_item.added`: Streams individual findings or results from the analysis (e.g., a specific issue found in a file).
- `response.code_analyzer_call.completed`: Indicates the completion of the code analysis.

### 6. Output and Display
- The `RichDisplay` will be updated to present code analysis results in a structured and readable format, potentially including code snippets, line numbers, and severity of findings.
- `PlainDisplay` and `JsonDisplay` will provide simpler text-based or structured JSON output for automation and integration with other tools.

### 7. Configuration
- New configuration options specific to the Code Analyzer (e.g., default analysis types, ignored file patterns) might be added to `SearchConfig` or a dedicated `CodeAnalyzerConfig` model if complexity warrants.

## Consequences

### Positive
- **Enhanced Developer Productivity**: Provides a powerful, integrated tool for code analysis within the familiar CLI environment.
- **Leverages Existing Architecture**: Fits well into the current modular design (SDK, processors, display strategies).
- **Extensible**: Can be expanded with more analysis types and capabilities over time.
- **AI-Powered Insights**: Can potentially leverage AI models for more sophisticated code understanding and suggestions beyond traditional static analysis.

### Negative
- **Increased Complexity**: Adds a new tool and its associated components (processor, SDK functions, event types) to the codebase.
- **API Dependency**: Requires a corresponding backend API endpoint in Knowledge Forge to perform the actual code analysis.
- **Scope Definition**: The scope of analysis (languages supported, types of checks) needs to be clearly defined and potentially managed.

## Alternatives Considered

1.  **External Static Analyzer Integration**: Wrapping existing external static analysis tools. Rejected because the goal is to leverage the Knowledge Forge API and potentially AI-driven analysis, not just run local linters.
2.  **Separate CLI Tool**: Creating a completely separate CLI tool for code analysis. Rejected to keep a unified experience within `forge-cli` and leverage its existing infrastructure.

## References
- ADR-001: Command-Line Interface Design
- (Link to future API documentation for Code Analyzer if available)
