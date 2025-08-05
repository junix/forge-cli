# ADR-014: Command JSON Flag Refactoring

## Status: Implemented

## Context

The forge-cli chat commands had inconsistent patterns for JSON output:
- `/show-doc-json` - Separate command for JSON output  
- `/topk --json` - Flag-based approach

This inconsistency led to:
- Command proliferation (separate commands for each output format)
- Confusion about which pattern to follow
- Maintenance burden of duplicate commands

## Decision

Standardize all commands to use `--json` flags instead of separate JSON commands.

### Migration Pattern

```bash
# OLD: Separate commands
/show-doc <doc-id>          # Formatted output
/show-doc-json <doc-id>     # JSON output

# NEW: Unified with flags
/show-doc <doc-id>              # Formatted output (default)
/show-doc --id=<doc-id> --json  # JSON output
```

## Implementation

### 1. Created Shared Utilities

`chat/commands/utils.py`:
- `parse_flag_parameters()` - Parse `--flag=value` arguments
- `has_json_flag()` - Check for `--json` flag

### 2. Refactored Commands

All commands now support both simple and flag-based formats:

#### `/show-doc`
```bash
/show-doc doc_123              # Simple format
/show-doc --id=doc_123 --json  # Flag format with JSON
```

#### `/show-collection`
```bash
/show-collection vs_123              # Simple format
/show-collection --id=vs_123 --json  # Flag format with JSON
```

#### `/show-collections`
```bash
/show-collections         # Simple format
/show-collections --json  # Flag format with JSON
```

#### `/show-documents`
```bash
/show-documents         # Simple format
/show-documents --json  # Flag format with JSON
```

#### `/show-pages`
```bash
/show-pages doc_123 1 5                          # Simple format
/show-pages --id=doc_123 --start=1 --end=5 --json  # Flag format with JSON
```

### 3. Removed Obsolete Commands

- Deleted `/show-doc-json` command and its implementation
- Removed from command registry
- Deleted `show_document_json.py` file

## Benefits

1. **Consistency**: All commands follow the same pattern
2. **Flexibility**: Users can choose output format without learning new commands
3. **Maintainability**: Single implementation per command
4. **Extensibility**: Easy to add new output formats (e.g., `--csv`, `--xml`)
5. **Discoverability**: Flags are self-documenting in help text

## Migration Guide

For users upgrading:

```bash
# Replace this:
/show-doc-json doc_123

# With this:
/show-doc --id=doc_123 --json
# Or simply:
/show-doc doc_123  # Then add --json when needed
```

## Future Work

1. Consider adding more output formats:
   - `--csv` for tabular data
   - `--yaml` for configuration-friendly output
   - `--table` for rich table formatting

2. Standardize error output:
   - JSON errors should have consistent structure
   - Consider `--quiet` flag for minimal output

3. Add format detection:
   - Auto-detect when output is piped
   - Default to JSON when stdout is not a TTY

## Testing

All refactored commands should be tested with:
1. Simple format (no flags)
2. Flag format with `--json`
3. Invalid arguments
4. Error cases (missing resources, API failures)

## Related

- ADR-001: Command-line interface design principles
- `/topk` command: Already implements this pattern