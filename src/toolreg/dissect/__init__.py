"""Python docstring parsing and analysis toolkit.

The dissect module provides tools for analyzing, parsing, and manipulating Python
docstrings in various formats including Google-style, NumPy-style, Sphinx, and RST.

Key Components:
    DocStringStyler: The main class for handling docstring styles and formatting.
        Supports automatic style detection, parsing, and example formatting.
        Handles multiple docstring formats including:
        - Google-style docstrings
        - NumPy-style docstrings
        - Sphinx docstrings
        - reStructuredText (RST)
        - Plain docstrings

    Functions:
        inspect_function: Extract documentation and examples from function docstrings
        generate_function_docs: Generate documentation for multiple functions
        detect_docstring_style: Automatically detect the style of a docstring

Usage:
    >>> from toolreg.dissect.docstringstyler import DocStringStyler
    >>> styler = DocStringStyler(current_style="google")
    >>> docstring = '''
    ...     Args:
    ...         x: Parameter
    ...     Returns:
    ...         Result
    ... '''
    >>> sections = styler.parse(docstring)
"""
