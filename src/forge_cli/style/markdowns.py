"""
Markdown text processing utilities for italicizing content.

Provides two approaches:
1. Quick regex-based italicization for simple documents
2. Robust AST-based processing that respects code blocks and formatting
"""
from __future__ import annotations

import re
from pathlib import Path

try:
    import mdformat
    from markdown_it import MarkdownIt
    from markdown_it.token import Token

    HAS_MARKDOWN_IT = True
except ImportError:
    HAS_MARKDOWN_IT = False


def italicize_naive(text: str) -> str:
    """
    Quick-and-dirty italicization using regex.

    Wraps non-empty lines with asterisks for italic formatting.
    WARNING: This will also affect code blocks and existing emphasis.

    Args:
        text: Markdown text to italicize

    Returns:
        Text with lines wrapped in asterisks

    Limitations:
        - Affects code blocks and fenced regions
        - Duplicates existing emphasis markers
        - Best for simple documents without complex formatting
    """
    # Add * … * around anything that is not already an italic marker
    return re.sub(r"^(.*\S.*)", r"*\1*", text, flags=re.MULTILINE)


def _wrap_text_tokens(tokens: list) -> None:
    """
    Recursively walk the token list, wrapping literal text in *...*.
    Code, HTML, and link destinations are untouched.

    Args:
        tokens: List of markdown-it Token objects to process
    """
    if not HAS_MARKDOWN_IT:
        return

    for tok in tokens:
        # Text nodes that are *not* within code/HTML
        if tok.type == "text" and not tok.markup:
            tok.content = f"*{tok.content}*"
        # Dive into children (nested inline tokens)
        if tok.children:
            _wrap_text_tokens(tok.children)


def italicize_markdown(text: str, use_robust: bool = True) -> str:
    """
    Italicize markdown text with optional robust AST-based processing.

    Args:
        text: Markdown text to italicize
        use_robust: If True, use AST-based processing that respects code blocks.
                   If False or markdown-it-py not available, use regex approach.

    Returns:
        Italicized markdown text

    Raises:
        ImportError: If use_robust=True but markdown-it-py is not installed
    """
    if not use_robust or not HAS_MARKDOWN_IT:
        return italicize_naive(text)

    # Robust AST-based approach
    md = MarkdownIt()
    tree = md.parse(text)
    _wrap_text_tokens(tree)

    # mdformat reflows the modified AST back to valid Markdown
    rendered = ""
    for token in tree:
        if hasattr(token, "content"):
            rendered += token.content
        if hasattr(token, "children") and token.children:
            for child in token.children:
                if hasattr(child, "content"):
                    rendered += child.content

    try:
        return mdformat.text(rendered)
    except:
        # Fallback if mdformat fails
        return rendered


def italicize_file(
    input_path: Path | str, output_path: Path | str | None = None, use_robust: bool = True, in_place: bool = False
) -> Path:
    """
    Italicize a markdown file.

    Args:
        input_path: Path to input markdown file
        output_path: Path for output file. If None, adds .italic suffix
        use_robust: Whether to use AST-based processing
        in_place: If True, modify the input file directly

    Returns:
        Path to the output file

    Example:
        # Create new italicized file
        output = italicize_file("document.md")

        # Modify in place
        italicize_file("document.md", in_place=True)

        # Use simple regex approach
        italicize_file("simple.md", use_robust=False)
    """
    input_path = Path(input_path)

    if in_place:
        output_path = input_path
    elif output_path is None:
        output_path = input_path.with_suffix(".italic.md")
    else:
        output_path = Path(output_path)

    # Read input file
    text = input_path.read_text(encoding="utf-8")

    # Process text
    italicized = italicize_markdown(text, use_robust=use_robust)

    # Write output
    output_path.write_text(italicized, encoding="utf-8")

    return output_path


# CLI convenience functions
def main():
    """Simple CLI interface for italicizing markdown files."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Italicize markdown files")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--in-place", action="store_true", help="Modify input file directly")
    parser.add_argument("--simple", action="store_true", help="Use simple regex approach instead of AST")

    args = parser.parse_args()

    try:
        output_path = italicize_file(args.input, args.output, use_robust=not args.simple, in_place=args.in_place)
        print(f"Saved italicized file → {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
