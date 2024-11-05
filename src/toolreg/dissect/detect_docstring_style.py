from __future__ import annotations

from enum import StrEnum, auto
import re
from typing import TYPE_CHECKING, Final

import griffe


if TYPE_CHECKING:
    from collections.abc import Callable


class DocstringStyle(StrEnum):
    """Enumeration of supported docstring styles."""

    GOOGLE = auto()
    NUMPY = auto()
    SPHINX = auto()
    RST = auto()
    PLAIN = auto()


# Combine patterns into a dictionary
_DOCSTRING_PATTERNS: Final[dict[DocstringStyle, list[re.Pattern[str]]]] = {
    DocstringStyle.GOOGLE: [
        re.compile(r"\s*Args:\s*$", re.MULTILINE),
        re.compile(r"\s*Returns:\s*$", re.MULTILINE),
        re.compile(r"\s*Raises:\s*$", re.MULTILINE),
    ],
    DocstringStyle.NUMPY: [
        re.compile(r"\s*Parameters\s*\n\s*----------\s*$", re.MULTILINE),
        re.compile(r"\s*Returns\s*\n\s*-------\s*$", re.MULTILINE),
    ],
    DocstringStyle.SPHINX: [
        re.compile(r":param\s+\w+:", re.MULTILINE),
        re.compile(r":returns?:", re.MULTILINE),
        re.compile(r":raises?\s+\w+:", re.MULTILINE),
    ],
    DocstringStyle.RST: [
        re.compile(r"\.\.\s+\w+::", re.MULTILINE),
        re.compile(r"^\s*\.\.\s+note::", re.MULTILINE),
        re.compile(r"^\s*\.\.\s+warning::", re.MULTILINE),
    ],
}

# Compile patterns once for better performance
_GOOGLE_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"\s*Args:\s*$", re.MULTILINE),
    re.compile(r"\s*Returns:\s*$", re.MULTILINE),
    re.compile(r"\s*Raises:\s*$", re.MULTILINE),
]

_NUMPY_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"\s*Parameters\s*\n\s*----------\s*$", re.MULTILINE),
    re.compile(r"\s*Returns\s*\n\s*-------\s*$", re.MULTILINE),
]

_SPHINX_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r":param\s+\w+:", re.MULTILINE),
    re.compile(r":returns?:", re.MULTILINE),
    re.compile(r":raises?\s+\w+:", re.MULTILINE),
]

_RST_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"\.\.\s+\w+::", re.MULTILINE),
    re.compile(r"^\s*\.\.\s+note::", re.MULTILINE),
    re.compile(r"^\s*\.\.\s+warning::", re.MULTILINE),
]


def detect_docstring_style(docstring: str) -> DocstringStyle:
    """Detect the style of a given docstring.

    Args:
        docstring: The docstring to analyze.

    Returns:
        The detected docstring style.

    Examples:
        >>> doc = '''
        ...     Args:
        ...         x: Some parameter
        ...     Returns:
        ...         The result
        ... '''
        >>> detect_docstring_style(doc)
        DocstringStyle.GOOGLE
    """
    if not docstring:
        return DocstringStyle.PLAIN

    # Clean the docstring for consistent analysis
    cleaned_docstring = docstring.strip()

    for style, patterns in _DOCSTRING_PATTERNS.items():
        if any(pattern.search(cleaned_docstring) for pattern in patterns):
            return style

    # If no specific style is detected, assume it's plain
    return DocstringStyle.PLAIN


def parse_docstring(
    docstring: str,
    style: str = "google",
) -> list[griffe.DocstringSection]:
    """Parse a docstring using griffe parser.

    Args:
        docstring: The docstring to parse
        style: The docstring style to use (google, numpy, sphinx)

    Returns:
        A Docstring object containing the parsed docstring

    Raises:
        ValueError: If an invalid style is provided
    """
    parser_funcs: dict[str, Callable[..., list[griffe.DocstringSection]]] = {
        "google": griffe.parse_google,
        "numpy": griffe.parse_numpy,
        "sphinx": griffe.parse_sphinx,
    }

    if style.lower() == "auto":
        style = detect_docstring_style(docstring).name.lower()

    parser_func = parser_funcs.get(style.lower())
    if not parser_func:
        msg = f"Invalid docstring style: {style}. Must be one of: google, numpy, sphinx"
        raise ValueError(msg)

    doc = griffe.Docstring(docstring)
    return parser_func(doc)


if __name__ == "__main__":
    import inspect

    def test(a: int = 0, b: str = "abc"):
        return f"{a} {b}"

    result = detect_docstring_style(inspect.getdoc(test) or "")
    docs = griffe.Docstring(inspect.getdoc(test) or "")
    print(result)
    example = parse_docstring(inspect.getdoc(test) or "", style="google")
