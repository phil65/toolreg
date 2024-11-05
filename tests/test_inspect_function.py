# from __future__ import annotations

# import textwrap
# from typing import Any

# import pytest

# from toolreg import inspect_function


# def create_test_function(docstring: str) -> Any:
#     """Create a function with the given docstring for testing."""

#     def test_func() -> None:
#         pass

#     test_func.__doc__ = docstring
#     return test_func


# @pytest.mark.parametrize(
#     "example_format,expected_count",
#     [
#         # Standard doctest format
#         (
#             """
#     Examples:
#         >>> print("hello")
#         hello
#     """,
#             1,
#         ),
#         # Markdown code block format
#         (
#             """
#     Examples:
#         ```python
#         >>> print("hello")
#         hello
#         ```
#     """,
#             1,
#         ),
#         # Multiple markdown blocks
#         (
#             """
#     Examples:
#         Basic usage:
#         ```python
#         >>> print("hello")
#         hello
#         ```

#         Advanced usage:
#         ```python
#         >>> print("world")
#         world
#         ```
#     """,
#             2,
#         ),
#         # Mixed format examples
#         (
#             """
#     Examples:
#         Standard example:
#         >>> print("hello")
#         hello

#         Markdown example:
#         ```python
#         >>> print("world")
#         world
#         ```
#     """,
#             2,
#         ),
#         # Indented code blocks
#         (
#             """
#     Examples:
#         Here's an example:
#             >>> print("hello")
#             hello

#         Another one:
#             >>> print("world")
#             world
#     """,
#             2,
#         ),
#         # Examples with descriptions
#         (
#             """
#     Examples:
#         Basic example - prints a greeting:
#         >>> print("hello")
#         hello

#         Advanced example - with formatting:
#         >>> print(f"hello {name}")
#         hello world
#     """,
#             2,
#         ),
#     ],
# )
# def test_example_formats(example_format: str, expected_count: int) -> None:
#     """Test parsing of different example section formats."""
#     func = create_test_function(textwrap.dedent(example_format))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == expected_count


# def test_rst_style_examples() -> None:
#     """Test parsing of RST-style examples."""
#     docstring = """
#     Process input data.

#     .. code-block:: python

#         >>> data = [1, 2, 3]
#         >>> process_data(data)
#         [2, 4, 6]

#     Another example:

#     .. code-block:: python

#         >>> process_data([])
#         []
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 2


# def test_examples_with_setup() -> None:
#     """Test examples that include setup code."""
#     docstring = """
#     Examples:
#         Setup:
#         ```python
#         >>> import numpy as np
#         >>> data = np.array([1, 2, 3])
#         ```

#         Usage:
#         ```python
#         >>> result = process_array(data)
#         >>> print(result)
#         [2, 4, 6]
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 2


# f


# def test_examples_with_markdown_formatting() -> None:
#     """Test examples that include markdown formatting."""
#     docstring = """
#     Examples:
#         *Basic* example:
#         ```python
#         >>> print("hello")
#         hello
#         ```

#         **Advanced** example:
#         >>> print("world")
#         world

#         __Complex__ example with `inline code`:
#         ```python
#         >>> complex_function()
#         result
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 3


# def test_examples_with_nested_code_blocks() -> None:
#     """Test examples with nested code blocks."""
#     docstring = """
#     Examples:
#         Outer example:
#         ```python
#         >>> def inner_function():
#         ...     '''
#         ...     Inner docstring with code:
#         ...     ```python
#         ...     >>> print("nested")
#         ...     ```
#         ...     '''
#         ...     pass
#         >>> inner_function()
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 1


# def test_examples_with_special_characters() -> None:
#     """Test examples containing special characters."""
#     docstring = """
#     Examples:
#         Unicode example:
#         >>> print("Hello, 世界!")
#         Hello, 世界!

#         Regex example:
#         ```python
#         >>> import re
#         >>> pattern = r"\\w+\\s\\d+"
#         >>> re.match(pattern, "test 123")
#         <re.Match object>
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 2


# def test_examples_with_comments() -> None:
#     """Test examples that include comments."""
#     docstring = """
#     Examples:
#         # This is a comment
#         >>> print("hello")  # inline comment
#         hello

#         ```python
#         # Setup
#         >>> x = 1
#         # Processing
#         >>> y = x + 1
#         # Result
#         >>> print(y)
#         2
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 2


# def test_examples_with_blank_lines() -> None:
#     """Test examples with blank lines between code blocks."""
#     docstring = """
#     Examples:
#         First example:
#         >>> print("one")
#         one


#         Second example:
#         >>> print("two")
#         two


#         ```python
#         # Third example
#         >>> print("three")
#         three
#         ```
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     assert len(result["examples"]) == 3


# def test_invalid_markdown_blocks() -> None:
#     """Test handling of invalid markdown code blocks."""
#     docstring = """
#     Examples:
#         ```python
#         >>> print("unclosed block

#         >>> print("another example")
#         example
#     """

#     func = create_test_function(textwrap.dedent(docstring))
#     result = inspect_function.inspect_function(func)

#     assert "examples" in result
#     # Should still capture the valid example even if markdown is malformed
#     assert len(result["examples"]) >= 1


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])
