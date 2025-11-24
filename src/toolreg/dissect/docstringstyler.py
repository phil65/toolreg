"""Module for managing and formatting docstring styles."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import griffe

from toolreg.dissect import docstring_patterns
from toolreg.dissect.docstringstyle import DocstringStyle


type DocstringSections = list[griffe.DocstringSection]
type ExampleFormatter = Callable[[str], str]
type StyleType = str | DocstringStyle


class DocStringStyler:
    """A class to manage docstring styles and example formatting.

    Args:
        current_style: The current docstring style to use
        example_formatter: Optional function to format example strings

    Raises:
        ValueError: If an invalid current style is provided
    """

    VALID_STYLES: Final[set[str]] = {"google", "numpy", "sphinx", "plain", "auto"}

    def __init__(
        self,
        current_style: StyleType = "google",
        example_formatter: ExampleFormatter | None = None,
    ) -> None:
        self._current_style: StyleType = str(current_style).lower()
        self._example_formatter: ExampleFormatter = example_formatter or (lambda x: x)

    def format_example(self, example: str) -> str:
        """Format an example string using the configured formatter.

        Args:
            example: The example string to format

        Returns:
            The formatted example string
        """
        return self._example_formatter(example)

    def parse(self, docstring: str) -> DocstringSections:
        """Parse a docstring using the current style.

        Args:
            docstring: The docstring to parse

        Returns:
            List of parsed docstring sections
        """
        return parse_docstring(docstring, style=self._current_style)

    @property
    def style(self) -> str:
        """Get the current style."""
        return self._current_style

    @style.setter
    def style(self, new_style: StyleType) -> None:
        """Set the current style.

        Args:
            new_style: The new style to use

        Raises:
            ValueError: If an invalid style is specified
        """
        if not DocstringStyle.is_valid(str(new_style)):
            msg = f"Invalid style: {new_style}. Must be one of: {', '.join(self.VALID_STYLES)}"
            raise ValueError(msg) from None
        self._current_style = str(new_style).lower()

    @property
    def example_formatter(self) -> ExampleFormatter:
        """Get the current example formatter function."""
        return self._example_formatter

    @example_formatter.setter
    def example_formatter(self, formatter: ExampleFormatter) -> None:
        """Set a new example formatter function.

        Args:
            formatter: The new formatter function to use

        Raises:
            TypeError: If formatter is not callable
        """
        if not callable(formatter):
            msg = "Example formatter must be callable"
            raise TypeError(msg) from None
        self._example_formatter = formatter


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

    for style, patterns in docstring_patterns.DOCSTRING_PATTERNS.items():
        if any(pattern.search(cleaned_docstring) for pattern in patterns):
            return style

    # If no specific style is detected, assume it's plain
    return DocstringStyle.PLAIN


def parse_plain_docstring(
    docstring: griffe.Docstring,
) -> list[griffe.DocstringSection]:
    """Parse a plain docstring into a simple description section.

    Args:
        docstring: The docstring to parse

    Returns:
        A list containing a single DocstringSection with the description
    """
    return [griffe.DocstringSectionText(value=docstring.value.strip(), title=None)]


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
        "plain": parse_plain_docstring,
    }

    if style.lower() == "auto":
        style = detect_docstring_style(docstring).name.lower()

    parser_func = parser_funcs.get(style.lower())
    if not parser_func:
        options = ", ".join(parser_funcs.keys())
        msg = f"Invalid docstring style: {style}. Must be one of: {options}"
        raise ValueError(msg)

    doc = griffe.Docstring(docstring)
    return parser_func(doc)


if __name__ == "__main__":
    import inspect
    from textwrap import dedent

    def example_function(x: int, y: str) -> str:
        """A sample function to demonstrate docstring parsing.

        Args:
            x: Some integer value
            y: Some string value

        Returns:
            A formatted string

        Examples:
            >>> example_function(42, "test")
            '42: test'

            >>> example_function(1, "hello")
            '1: hello'
        """
        return f"{x}: {y}"

    # Create a custom example formatter
    def markdown_formatter(example: str) -> str:
        return dedent(f"""
        ```python
        {example}
        ```
        """).strip()

    # Initialize the styler with custom formatter
    styler = DocStringStyler(current_style="google", example_formatter=markdown_formatter)

    # Get the docstring from our example function
    docstring = inspect.getdoc(example_function)

    if docstring:
        # Detect the style
        detected = detect_docstring_style(docstring)
        print(f"Detected style: {detected}")

        # Parse the docstring
        sections = styler.parse(docstring)
        print("\nParsed sections:")
        for section in sections:
            print(f"- {section.__class__.__name__}")

        # Format an example
        example = "print('Hello, World!')"
        formatted = styler.format_example(example)
        print("\nFormatted example:")
        print(formatted)

        # Try different style
        styler.style = "numpy"
        print(f"\nChanged style to: {styler.style}")
        numpy_sections = styler.parse(docstring)
        print(f"Number of sections parsed: {len(numpy_sections)}")
