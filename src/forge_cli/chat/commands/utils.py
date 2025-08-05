"""Utility functions for chat commands."""

from __future__ import annotations

import re
from typing import Any


def parse_flag_parameters(args: str) -> dict[str, str]:
    """Parse command arguments in flag format.

    Supports flag-based arguments:
    - --flag="quoted value" or --flag=unquoted_value
    - Boolean flags like --json

    Args:
        args: Argument string to parse

    Returns:
        Dictionary of parsed parameters

    Raises:
        ValueError: If parsing fails
    """
    params = {}

    # Regular expression to match --flag=value pairs with optional quotes
    # Supports: --flag="quoted value" or --flag=unquoted_value
    pattern = r'--(\w+(?:-\w+)*)=(?:"([^"]*)"|([^\s]+))'

    matches = re.findall(pattern, args)

    for match in matches:
        key = match[0]
        # Use quoted value if present, otherwise unquoted value
        value = match[1] if match[1] else match[2]
        params[key] = value

    # Also check for boolean flags (flags without values like --json)
    bool_pattern = r"--(\w+(?:-\w+)*)(?=\s|$)"
    bool_matches = re.findall(bool_pattern, args)

    for flag in bool_matches:
        # Only add if it's not already in params (to avoid overriding --flag=value with --flag)
        if flag not in params:
            params[flag] = "true"

    return params


def has_json_flag(params: dict[str, str]) -> bool:
    """Check if the --json flag is present in parameters.

    Args:
        params: Dictionary of parsed parameters

    Returns:
        True if --json flag is present
    """
    return "json" in params