# Utils Module - Utility Functions and Helpers

## Overview

The utils module is designed to house shared utility functions, helper classes, and common tools used throughout the Forge CLI codebase. While currently minimal (containing only `__init__.py`), this module is reserved for future cross-cutting concerns that don't belong to any specific module but are used by multiple components. All utilities follow the project's type-safety principles using Pydantic models and comprehensive type annotations.

## Directory Structure

```
utils/
└── __init__.py      # Module initialization (currently empty)
```

## Purpose and Design Philosophy

### Intended Use Cases

1. **String Manipulation**: Common text processing utilities
2. **Data Validation**: Input validation and sanitization
3. **File Operations**: High-level file handling utilities
4. **Time/Date Helpers**: Formatting and parsing utilities
5. **Network Utilities**: HTTP helpers, retry logic
6. **Caching Utilities**: Simple caching mechanisms
7. **Configuration Helpers**: Config file parsing
8. **Conversion Functions**: Data format conversions

### Design Principles

1. **Type Safety First**: Complete type annotations with Pydantic models where appropriate
2. **Pure Functions**: Utilities should be stateless when possible
3. **Minimal Dependencies**: Leverage existing project dependencies (Pydantic, typing)
4. **Well-Tested**: High test coverage for reliability with type validation
5. **Documented**: Clear docstrings with examples and type information

## Planned Utilities

### String Utilities (`string_utils.py`)

```python
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_citations(text: str) -> List[Tuple[int, int, int]]:
    """Extract citation markers from text.
    
    Returns list of (start_pos, end_pos, citation_num).
    """
    pattern = r'⟦⟦(\d+)⟧⟧'
    return [(m.start(), m.end(), int(m.group(1))) 
            for m in re.finditer(pattern, text)]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def format_bytes(size: int) -> str:
    """Format byte size as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"
```

### Time Utilities (`time_utils.py`)

```python
from datetime import datetime, timedelta
from typing import Optional

def format_duration(seconds: float) -> str:
    """Format duration in seconds as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def parse_relative_time(time_str: str) -> datetime:
    """Parse relative time strings like '5m ago', '2h ago'."""
    patterns = {
        r'(\d+)s(?:econds?)?\s*ago': lambda m: timedelta(seconds=int(m.group(1))),
        r'(\d+)m(?:inutes?)?\s*ago': lambda m: timedelta(minutes=int(m.group(1))),
        r'(\d+)h(?:ours?)?\s*ago': lambda m: timedelta(hours=int(m.group(1))),
        r'(\d+)d(?:ays?)?\s*ago': lambda m: timedelta(days=int(m.group(1)))
    }
    
    for pattern, delta_func in patterns.items():
        match = re.match(pattern, time_str.strip(), re.IGNORECASE)
        if match:
            return datetime.now() - delta_func(match)
    
    raise ValueError(f"Cannot parse relative time: {time_str}")
```

### File Utilities (`file_utils.py`)

```python
import hashlib
from pathlib import Path
from typing import Iterator, Optional

def calculate_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of file contents."""
    hash_func = getattr(hashlib, algorithm)()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def find_files(
    directory: Path,
    pattern: str = "*",
    recursive: bool = True
) -> Iterator[Path]:
    """Find files matching pattern in directory."""
    if recursive:
        return directory.rglob(pattern)
    else:
        return directory.glob(pattern)

def safe_write_file(filepath: Path, content: str, backup: bool = True):
    """Safely write file with optional backup."""
    filepath = Path(filepath)
    
    if backup and filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + '.bak')
        filepath.rename(backup_path)
    
    try:
        filepath.write_text(content, encoding='utf-8')
    except Exception:
        if backup and backup_path.exists():
            backup_path.rename(filepath)
        raise
```

### Network Utilities (`network_utils.py`)

```python
import asyncio
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry async function with exponential backoff."""
    attempt = 0
    current_delay = delay
    
    while attempt < max_attempts:
        try:
            return await func()
        except exceptions as e:
            attempt += 1
            if attempt >= max_attempts:
                raise
            
            await asyncio.sleep(current_delay)
            current_delay *= backoff

def parse_url_components(url: str) -> dict:
    """Parse URL into components."""
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(url)
    return {
        'scheme': parsed.scheme,
        'host': parsed.hostname,
        'port': parsed.port,
        'path': parsed.path,
        'query': parse_qs(parsed.query),
        'fragment': parsed.fragment
    }
```

### Validation Utilities (`validation_utils.py`)

```python
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class EmailValidator(BaseModel):
    """Pydantic model for email validation."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

def validate_email(email: str) -> bool:
    """Validate email address format using Pydantic."""
    try:
        EmailValidator(email=email)
        return True
    except Exception:
        return False

def validate_json_schema(data: dict, schema: dict) -> List[str]:
    """Validate data against JSON schema.
    
    Returns list of validation errors.
    """
    errors = []
    
    # Simple implementation - extend for full JSON schema support
    for field, rules in schema.get('properties', {}).items():
        if rules.get('required') and field not in data:
            errors.append(f"Missing required field: {field}")
        
        if field in data:
            value = data[field]
            expected_type = rules.get('type')
            
            if expected_type == 'string' and not isinstance(value, str):
                errors.append(f"Field {field} must be string")
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                errors.append(f"Field {field} must be number")
    
    return errors

def sanitize_input(
    text: str,
    allowed_chars: Optional[str] = None,
    max_length: Optional[int] = None
) -> str:
    """Sanitize user input."""
    if allowed_chars:
        text = ''.join(c for c in text if c in allowed_chars)
    
    if max_length:
        text = text[:max_length]
    
    return text.strip()
```

## Usage Guidelines

### For Language Models

When adding utilities to this module:

1. **Check existing utilities first**:

```python
# Before creating a new utility, check if it exists
from forge_cli.utils import string_utils

# Use existing utility
truncated = string_utils.truncate_text(long_text, 100)
```

2. **Follow naming conventions**:

```python
# Good: Clear, descriptive names
def format_file_size(bytes: int) -> str:
    pass

def validate_api_key(key: str) -> bool:
    pass

# Bad: Unclear or generic names
def process(data):
    pass

def check(value):
    pass
```

3. **Include comprehensive docstrings**:

```python
def merge_configs(base: dict, override: dict, deep: bool = True) -> dict:
    """Merge two configuration dictionaries.
    
    Args:
        base: Base configuration dictionary
        override: Override values to apply
        deep: If True, perform deep merge for nested dicts
        
    Returns:
        Merged configuration dictionary
        
    Examples:
        >>> base = {'a': 1, 'b': {'c': 2}}
        >>> override = {'b': {'d': 3}}
        >>> merge_configs(base, override)
        {'a': 1, 'b': {'c': 2, 'd': 3}}
    """
    # Implementation
```

## Development Guidelines

### Adding New Utilities

1. **Create dedicated module**:

```bash
# Create new utility module
touch src/forge_cli/utils/cache_utils.py
```

2. **Implement with tests**:

```python
# utils/cache_utils.py
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class SimpleCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
```

3. **Export from **init**.py**:

```python
# utils/__init__.py
from . import string_utils
from . import time_utils
from . import file_utils
from . import cache_utils

__all__ = [
    'string_utils',
    'time_utils', 
    'file_utils',
    'cache_utils'
]
```

### Testing Utilities

```python
# tests/test_utils.py
import pytest
from forge_cli.utils import string_utils

def test_truncate_text():
    # Test normal truncation
    result = string_utils.truncate_text("Hello World", 8)
    assert result == "Hello..."
    
    # Test no truncation needed
    result = string_utils.truncate_text("Short", 10)
    assert result == "Short"
    
    # Test custom suffix
    result = string_utils.truncate_text("Long text", 6, "…")
    assert result == "Long…"

def test_format_bytes():
    assert string_utils.format_bytes(0) == "0.00 B"
    assert string_utils.format_bytes(1024) == "1.00 KB"
    assert string_utils.format_bytes(1048576) == "1.00 MB"
```

## Best Practices

1. **Keep utilities focused**: Each function should do one thing well
2. **Avoid state**: Utilities should be pure functions when possible
3. **Handle edge cases**: Empty strings, None values, etc.
4. **Provide defaults**: Sensible defaults for optional parameters
5. **Type everything**: Complete type annotations for safety
6. **Test thoroughly**: High coverage with edge cases
7. **Document well**: Clear examples in docstrings

## Anti-Patterns to Avoid

1. **God utilities**: Don't create catch-all utility modules
2. **Business logic**: Keep utilities generic, not business-specific
3. **Heavy dependencies**: Utilities should be lightweight
4. **Mutable defaults**: Avoid mutable default arguments
5. **Side effects**: Utilities shouldn't modify global state

## Future Enhancements

Planned utility additions:

1. **Async Utilities**: Async-specific helpers
2. **CLI Utilities**: Terminal formatting helpers
3. **Data Utilities**: CSV, JSON, YAML helpers
4. **Security Utilities**: Encryption, hashing helpers
5. **Math Utilities**: Statistical and numerical helpers
6. **Collection Utilities**: Advanced list/dict operations

The utils module serves as a toolkit for common operations, promoting code reuse and maintaining consistency across the Forge CLI codebase. As the project grows, this module will expand with carefully selected, well-tested utilities that benefit multiple components.
