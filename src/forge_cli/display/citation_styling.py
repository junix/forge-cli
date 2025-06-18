import re
from typing import Literal

CIRCLED_DIGITS = {
    0: "⓿",
    1: "❶",
    2: "❷",
    3: "❸",
    4: "❹",
    5: "❺",
    6: "❻",
    7: "❼",
    8: "❽",
    9: "❾",
    10: "❿",
    11: "⓫",
    12: "⓬",
    13: "⓭",
    14: "⓮",
    15: "⓯",
    16: "⓰",
    17: "⓱",
    18: "⓲",
    19: "⓳",
    20: "⓴",
    21: "㉑",
    22: "㉒",
    23: "㉓",
    24: "㉔",
    25: "㉕",
    26: "㉖",
    27: "㉗",
    28: "㉘",
    29: "㉙",
    30: "㉚",
    31: "㉛",
    32: "㉜",
    33: "㉝",
    34: "㉞",
    35: "㉟",
    36: "㊱",
    37: "㊲",
    38: "㊳",
    39: "㊴",
    40: "㊵",
    41: "㊶",
    42: "㊷",
    43: "㊸",
    44: "㊹",
    45: "㊺",
    46: "㊻",
    47: "㊼",
    48: "㊽",
    49: "㊾",
    50: "㊿",
}

MULTIBOX_DIGITS = {
    0: "󰼎",
    1: "󰼏",
    2: "󰼐",
    3: "󰼑",
    4: "󰼒",
    5: "󰼓",
    6: "󰼔",
    7: "󰼕",
    8: "󰼖",
    9: "󰼗",
    10: "󰿪",
}

SUBSCRIPT_DIGITS = {
    0: "₀",
    1: "₁",
    2: "₂",
    3: "₃",
    4: "₄",
    5: "₅",
    6: "₆",
    7: "₇",
    8: "₈",
    9: "₉",
}

SUPERSCRIPT_DIGITS = {
    0: "⁰",
    1: "¹",
    2: "²",
    3: "³",
    4: "⁴",
    5: "⁵",
    6: "⁶",
    7: "⁷",
    8: "⁸",
    9: "⁹",
}

# Additional cool citation styles
SQUARED_DIGITS = {
    1: "▪",
    2: "◾",
    3: "◼",
    4: "⬛",
    5: "🟫",
    6: "🟪",
    7: "🟦",
    8: "🟩",
    9: "🟧",
    10: "🟥",
}

DIAMOND_DIGITS = {
    1: "◇",
    2: "◈",
    3: "◆",
    4: "◊",
    5: "⬦",
    6: "⬥",
    7: "⬧",
    8: "⬨",
    9: "⬩",
    10: "♦",
}

STAR_DIGITS = {
    1: "★",
    2: "✬",
    3: "✭",
    4: "✮",
    5: "✯",
    6: "✰",
    7: "⭐",
    8: "🌟",
    9: "✨",
    10: "💫",
}

ARROW_DIGITS = {
    1: "▶",
    2: "▷",
    3: "▸",
    4: "▹",
    5: "►",
    6: "➤",
    7: "➜",
    8: "➡",
    9: "⟶",
    10: "⇨",
}

ROMAN_NUMERALS = {
    1: "ⅰ",
    2: "ⅱ",
    3: "ⅲ",
    4: "ⅳ",
    5: "ⅴ",
    6: "ⅵ",
    7: "ⅶ",
    8: "ⅷ",
    9: "ⅸ",
    10: "ⅹ",
    11: "ⅺ",
    12: "ⅻ",
}

PARENTHESIZED_LETTERS = {
    1: "⒜",
    2: "⒝",
    3: "⒞",
    4: "⒟",
    5: "⒠",
    6: "⒡",
    7: "⒢",
    8: "⒣",
    9: "⒤",
    10: "⒥",
    11: "⒦",
    12: "⒧",
    13: "⒨",
    14: "⒩",
    15: "⒪",
    16: "⒫",
    17: "⒬",
    18: "⒭",
    19: "⒮",
    20: "⒯",
    21: "⒰",
    22: "⒱",
    23: "⒲",
    24: "⒳",
    25: "⒴",
    26: "⒵",
}

DOUBLE_CIRCLED_DIGITS = {
    1: "⓵",
    2: "⓶",
    3: "⓷",
    4: "⓸",
    5: "⓹",
    6: "⓺",
    7: "⓻",
    8: "⓼",
    9: "⓽",
    10: "⓾",
}

NEGATIVE_CIRCLED_DIGITS = {
    1: "❶",
    2: "❷",
    3: "❸",
    4: "❹",
    5: "❺",
    6: "❻",
    7: "❼",
    8: "❽",
    9: "❾",
    10: "❿",
    11: "⓿",
    12: "⓫",
    13: "⓬",
    14: "⓭",
    15: "⓮",
    16: "⓯",
    17: "⓰",
    18: "⓱",
    19: "⓲",
    20: "⓳",
}


def symbol_of(
    n: int,
    style: Literal[
        "auto",
        "circled",
        "multibox",
        "subscript",
        "superscript",
        "short",
        "long",
        "squared",
        "diamond",
        "star",
        "arrow",
        "pdf",
        "roman",
        "letters",
        "double_circled",
        "negative_circled",
        "brackets",
        "braces",
        "angles",
    ] = "long",
    max_source: int | None = None,
) -> str:
    assert isinstance(n, int) and n >= 0
    assert style in [
        "auto",
        "circled",
        "multibox",
        "subscript",
        "superscript",
        "short",
        "long",
        "squared",
        "diamond",
        "star",
        "arrow",
        "pdf",
        "roman",
        "letters",
        "double_circled",
        "negative_circled",
        "brackets",
        "braces",
        "angles",
    ]

    if style == "auto":
        max_multibox = max(MULTIBOX_DIGITS.keys())
        max_circled = max(CIRCLED_DIGITS.keys())
        if max_source:
            if n < max_circled and max_source <= max_multibox:
                style = "multibox"
            elif n < max_circled and max_source < max_circled:
                style = "circled"

        if style == "auto":
            style = "superscript"

    if style == "circled":
        return CIRCLED_DIGITS.get(n, f"[[{str(n)}]]")
    elif style == "multibox":
        return MULTIBOX_DIGITS.get(n, f"[[{str(n)}]]")
    elif style == "subscript":
        return "".join(SUBSCRIPT_DIGITS[int(digit)] for digit in str(n))
    elif style == "superscript":
        return "".join(SUPERSCRIPT_DIGITS[int(digit)] for digit in str(n))
    elif style == "short":
        return f"⟦{n}⟧"
    elif style == "long":
        return f"⟦⟦{n}⟧⟧"
    elif style == "squared":
        return SQUARED_DIGITS.get(n, f"■{n}")
    elif style == "diamond":
        return DIAMOND_DIGITS.get(n, f"◆{n}")
    elif style == "star":
        return STAR_DIGITS.get(n, f"★{n}")
    elif style == "arrow":
        return ARROW_DIGITS.get(n, f"→{n}")
    elif style == "pdf":
        return f"󰰘󰯴󰯺{n}"
    elif style == "roman":
        # Convert to uppercase for larger numbers
        if n <= len(ROMAN_NUMERALS):
            return ROMAN_NUMERALS[n]
        else:
            # Convert to traditional roman numerals for larger numbers
            def to_roman(num):
                val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
                syms = [
                    "M",
                    "CM",
                    "D",
                    "CD",
                    "C",
                    "XC",
                    "L",
                    "XL",
                    "X",
                    "IX",
                    "V",
                    "IV",
                    "I",
                ]
                roman_num = ""
                i = 0
                while num > 0:
                    for _ in range(num // val[i]):
                        roman_num += syms[i]
                        num -= val[i]
                    i += 1
                return roman_num.lower()

            return f"({to_roman(n)})"
    elif style == "letters":
        return PARENTHESIZED_LETTERS.get(n, f"({chr(96 + n)})" if n <= 26 else f"({n})")
    elif style == "double_circled":
        return DOUBLE_CIRCLED_DIGITS.get(n, f"⦿{n}")
    elif style == "negative_circled":
        return NEGATIVE_CIRCLED_DIGITS.get(n, f"●{n}")
    elif style == "brackets":
        return f"[{n}]"
    elif style == "braces":
        return f"{{{n}}}"
    elif style == "angles":
        return f"⟨{n}⟩"
    else:
        return f"[[{str(n)}]]"


def style_citations(
    text: str,
    style: Literal[
        "auto",
        "circled",
        "multibox",
        "subscript",
        "superscript",
        "long",
        "page",
        "parenthesis",
        "squared",
        "diamond",
        "star",
        "arrow",
        "pdf",
        "roman",
        "letters",
        "double_circled",
        "negative_circled",
        "brackets",
        "braces",
        "angles",
        "short",
    ] = "superscript",
) -> str:
    """Replace citation markers in the format [citation:<page-id>] with pretty formatted versions.

    Args:
        text: The text containing citation markers
        style: The style to use for the citation numbers
            - "auto": Automatically choose the best style based on the number of citations
            - "circled": ❶ ❷ ❸ (up to 50)
            - "multibox": 󰼏 󰼐 󰼑 (special multibox icons)
            - "subscript": ₁ ₂ ₃
            - "superscript": ¹ ² ³ (default)
            - "short": ⟦1⟧ ⟦2⟧ ⟦3⟧
            - "long": ⟦⟦1⟧⟧ ⟦⟦2⟧⟧ ⟦⟦3⟧⟧
            - "squared": ▪ ◾ ◼ (color squares for first 10)
            - "diamond": ◇ ◈ ◆ (various diamond shapes)
            - "star": ★ ✬ ✭ (various star shapes)
            - "arrow": ▶ ▷ ▸ (various arrow shapes)
            - "pdf": 󰰘󰯴󰯺1 󰰘󰯴󰯺2 󰰘󰯴󰯺3 (PDF-style icons)
            - "roman": ⅰ ⅱ ⅲ (lowercase roman numerals)
            - "letters": ⒜ ⒝ ⒞ (parenthesized letters)
            - "double_circled": ⓵ ⓶ ⓷ (double circles)
            - "negative_circled": ❶ ❷ ❸ (filled circles)
            - "brackets": [1] [2] [3]
            - "braces": {1} {2} {3}
            - "angles": ⟨1⟩ ⟨2⟩ ⟨3⟩
            - "page": Format as (P<page-id>) or (P<page-id1>,P<page-id2>)
            - "parenthesis": Format as (<page-id>)

    Returns:
        The text with citation markers replaced with pretty formatted versions
    """
    import re

    # Find all unique citation markers and count them
    citation_pattern = r"\[\[citation:([^\]]+)\]\]"
    citations = re.findall(citation_pattern, text)

    if style == "page" or style == "parenthesis":
        # Group citations that are next to each other
        deduplicated_text = text
        citation_groups = []

        # First, replace each citation with a unique marker
        for i, citation in enumerate(citations):
            marker = f"__CITATION_MARKER_{i}__"
            deduplicated_text = deduplicated_text.replace(f"[citation:{citation}]", marker, 1)
            citation_groups.append([citation])

        # Process the markers sequentially to group adjacent ones
        final_text = ""
        remaining_text = deduplicated_text
        while remaining_text:
            marker_match = re.search(r"__CITATION_MARKER_(\d+)__", remaining_text)
            if not marker_match:
                final_text += remaining_text
                break

            # Add the text up to the marker
            final_text += remaining_text[: marker_match.start()]
            remaining_text = remaining_text[marker_match.end() :]

            # Get the current marker index
            current_idx = int(marker_match.group(1))

            # Format based on style
            if style == "page":
                page_ids = [f"P{page_id}" for page_id in citation_groups[current_idx]]
                if len(page_ids) == 1:
                    replacement = f"({page_ids[0]})"
                else:
                    replacement = f"({','.join(page_ids)})"
            else:  # parenthesis style
                if len(citation_groups[current_idx]) == 1:
                    replacement = f"({citation_groups[current_idx][0]})"
                else:
                    replacement = f"({','.join(citation_groups[current_idx])})"

            final_text += replacement

        return final_text
    else:
        # Create a mapping from citation page_id to index
        citation_map = {page_id: idx for idx, page_id in enumerate(dict.fromkeys(citations))}

        # Calculate the maximum citation index for auto styling
        max_citation = len(citation_map) - 1 if citation_map else 0

        # Replace each citation marker with its styled version
        styled_text = text
        for page_id, idx in citation_map.items():
            symbol = symbol_of(idx + 1, style=style, max_source=max_citation + 1)
            styled_text = styled_text.replace(f"[citation:{page_id}]", symbol)

        return styled_text


LONG_PATTERN = re.compile(r"⟦⟦(\d+)⟧⟧")


def long2circled(text: str) -> str:
    """
    Convert “long-style” citation markers (⟦⟦n⟧⟧) to their circled-digit
    equivalents (❶ ❷ ❸ …).

    Args:
        text: The full text that may contain ⟦⟦n⟧⟧ markers.

    Returns:
        A copy of *text* where every ⟦⟦n⟧⟧ has been replaced with
        the corresponding character from ``CIRCLED_DIGITS``.
        If *n* is not present in the lookup table, the original marker
        is left unchanged.
    """

    def _replace(match: re.Match[str]) -> str:
        n = int(match.group(1))
        return "[" + CIRCLED_DIGITS.get(n, match.group(0)) + "]() "

    return LONG_PATTERN.sub(_replace, text)
