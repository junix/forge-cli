# Dict-based API Deprecation Timeline

## Overview

This document outlines the deprecation timeline for the legacy dict-based API in favor of the new typed API using Pydantic models and type safety.

## Timeline

### Phase 1: Introduction (Current - v0.5.0)
**Status: ✅ Complete**

- Typed API introduced alongside dict-based API
- Both APIs fully functional
- Migration helpers available
- Documentation and examples provided

### Phase 2: Recommendation (v0.6.0 - Q1 2024)
**Status: 🟡 Active**

- Typed API becomes the recommended approach
- New features only added to typed API
- Documentation defaults to typed examples
- Migration guide prominently featured

### Phase 3: Soft Deprecation (v0.7.0 - Q2 2024)
**Status: ⏳ Planned**

- Dict-based API marked as deprecated
- Deprecation warnings added (can be silenced)
- All internal code migrated to typed API
- Community migration support provided

### Phase 4: Feature Freeze (v0.8.0 - Q3 2024)
**Status: ⏳ Planned**

- No new features for dict-based API
- Only critical bug fixes
- Stronger deprecation warnings
- Migration tools enhanced

### Phase 5: Final Deprecation (v1.0.0 - Q4 2024)
**Status: ⏳ Planned**

- Dict-based API moved to legacy module
- Must explicitly import from `forge_cli.legacy`
- Final warning before removal
- Compatibility layer available as separate package

### Phase 6: Removal (v2.0.0 - Q1 2025)
**Status: ⏳ Planned**

- Dict-based API completely removed
- Legacy compatibility package maintained separately
- Full typed API only

## Migration Guide

### Quick Start

```python
# Old (dict-based)
from forge_cli.sdk import astream_response

async for event_type, event_data in astream_response(
    input_messages=[{"role": "user", "content": "Hello"}],
    model="qwen-max-latest"
):
    text = event_data.get("text", "")

# New (typed)
from forge_cli.sdk import astream_typed_response
from forge_cli.response._types import Request, InputMessage

request = Request(
    input=[InputMessage(role="user", content="Hello")],
    model="qwen-max-latest"
)
async for event_type, response in astream_typed_response(request):
    text = response.text  # Type-safe access
```

### Using Migration Helpers

```python
from forge_cli.response.migration_helpers import MigrationHelper

# Works with both dict and typed
text = MigrationHelper.safe_get_text(event_data)
item_type = MigrationHelper.safe_get_type(item)
```

## Benefits of Migration

1. **Type Safety**: Catch errors at development time
2. **IDE Support**: Full autocomplete and inline documentation
3. **Validation**: Automatic Pydantic validation
4. **Performance**: Optimized serialization/deserialization
5. **Maintainability**: Self-documenting code
6. **Future Features**: New features only in typed API

## Deprecation Warnings

### Phase 3 Warning (Soft)
```
DeprecationWarning: The dict-based API is deprecated and will be removed in v2.0.0.
Please migrate to the typed API. See migration guide: https://...
To silence this warning, set FORGE_CLI_SUPPRESS_DEPRECATION=1
```

### Phase 4 Warning (Strong)
```
DeprecationWarning: The dict-based API is deprecated and will be removed in v2.0.0.
This is the FINAL WARNING before the API moves to legacy status.
Migrate NOW to avoid breaking changes. Guide: https://...
```

### Phase 5 Warning (Final)
```
DeprecationWarning: You are using the legacy dict-based API.
This API will be REMOVED in the next major version.
Import from forge_cli.legacy is temporary. Migrate immediately!
```

## Suppressing Warnings

During transition, warnings can be suppressed:

```python
# Environment variable
export FORGE_CLI_SUPPRESS_DEPRECATION=1

# In code
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="forge_cli")

# Specific to dict API
from forge_cli import disable_deprecation_warnings
disable_deprecation_warnings()
```

## Support Commitment

- **Security fixes**: Until v2.0.0 (removal)
- **Critical bugs**: Until v1.0.0 (final deprecation)
- **General bugs**: Until v0.8.0 (feature freeze)
- **New features**: Already stopped

## Community Resources

- Migration guide: `/src/forge_cli/scripts/migration-example.py`
- Typed examples: `/src/forge_cli/scripts/hello-typed-example.py`
- Compatibility tests: `/src/forge_cli/tests/test_api_compatibility.py`
- Discussion forum: GitHub Discussions
- Migration help: GitHub Issues with `migration` label

## FAQ

**Q: Will my existing code break?**
A: No, not until v2.0.0. You have until Q1 2025 to migrate.

**Q: Can I use both APIs together?**
A: Yes, during the transition period. Use MigrationHelper for compatibility.

**Q: What if I can't migrate by v2.0.0?**
A: A separate legacy compatibility package will be available.

**Q: Are there automated migration tools?**
A: We provide migration helpers and examples. Full automation is planned for v0.8.0.

**Q: Why deprecate the dict API?**
A: Type safety, better performance, IDE support, and maintainability.

## Action Items for Users

1. **Now**: Start using typed API for new code
2. **Soon**: Migrate active projects using migration helpers
3. **By v0.8.0**: Complete migration of critical code
4. **By v1.0.0**: Finish all migrations
5. **Before v2.0.0**: Remove all dict-based API usage

## Maintainer Commitment

We commit to:
- Clear communication at each phase
- Adequate time for migration (1+ year)
- Migration tools and helpers
- Community support
- Compatibility options

The typed API is the future of Forge CLI, providing a better developer experience while maintaining the power and flexibility you expect.