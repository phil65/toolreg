"""Text manipulation utilities."""

from __future__ import annotations

import datetime
import functools
import inspect
import itertools
import re
from typing import TYPE_CHECKING, Any

from jinjarope import utils

from toolreg.registry.example import Example
from toolreg.registry.register_tool import register_tool


if TYPE_CHECKING:
    from collections.abc import Callable
    import os


CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-letter-ends-with",
    examples=[
        Example(
            title="basic",
            template="""{{ "acccc" | removesuffix("c") }}""",
        )
    ],
)
def removesuffix(text: str, suffix: str) -> str:
    """Return given suffix from text.

    Args:
        text: The text to strip the suffix from
        suffix: The suffix to remove
    """
    return text.removesuffix(suffix)


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-letter-starts-with",
    examples=[
        Example(
            title="basic",
            template="""{{ "ccca" | removeprefix("c") }}""",
        )
    ],
)
def removeprefix(text: str, prefix: str) -> str:
    """Return given prefix from text.

    Args:
        text: The text to strip the prefix from
        prefix: The prefix to remove
    """
    return text.removeprefix(prefix)


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-align-left",
    examples=[Example(title="basic", template="""{{ " abc" | lstrip }}""")],
)
def lstrip(text: str, chars: str | None = None) -> str:
    """Strip given chars from beginning of string.

    Args:
        text: The text to strip the chars from
        chars: The chars to remove
    """
    return text.lstrip(chars)


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-align-right",
    examples=[Example(title="basic", template="""{{ "abc " | rstrip }}""")],
)
def rstrip(text: str, chars: str | None = None) -> str:
    """Strip given chars from end of string.

    Args:
        text: The text to strip the chars from
        chars: The chars to remove
    """
    return text.rstrip(chars)


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-letter-case",
    examples=[
        Example(title="basic", template="""{{ "some_text" | lower_camel_case }}""")
    ],
)
def lower_camel_case(text: str) -> str:
    """Convert given text to lower-camel-case.

    Args:
        text: The string to convert
    """
    if "_" not in text:
        return text
    first, *others = text.split("_")
    return "".join([first.lower(), *map(str.title, others)])


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-letter-case-lower",
    examples=[Example(title="basic", template="""{{ " someText" | snake_case }}""")],
)
def snake_case(text: str) -> str:
    """Convert given text to snake-case.

    Args:
        text: The string to convert
    """
    if "_" in text:
        return text
    return CASE_PATTERN.sub("_", text).lower()


@register_tool(
    typ="filter",
    group="format",
    icon="mdi:code-braces",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ "AVeryLargeCodeBlock(a_parameter=3, another_parameter=4,"""
                """ abc=False)" | format_code }}"""
            ),
        )
    ],
)
@functools.cache
def format_code(code: str, line_length: int = 100) -> str:
    """Format code to given line length using `black`.

    Args:
        code: The code to format
        line_length: Line length limit for formatted code
    """
    code = code.strip()
    if len(code) < line_length:
        return code
    formatter = utils._get_black_formatter()
    return formatter(code, line_length)


@register_tool(
    typ="filter",
    group="format",
    icon="mdi:content-cut",
    examples=[
        Example(
            title="basic",
            template="""{{
"@deprecated
def test(a):
    b = a
" | extract_body }}""",
        )
    ],
)
@functools.cache
def extract_body(src: str) -> str:
    """Get body of source code of given function / class.

    Strips off the signature / decorators.

    Args:
        src: Source code to extract the body from
    """
    lines = src.split("\n")
    src_lines = itertools.dropwhile(lambda x: x.strip().startswith("@"), lines)
    line = next(src_lines).strip()  # type: ignore
    if not line.startswith(("def ", "class ")):
        return line.rsplit(":")[-1].strip()
    if not line.endswith(":"):
        for line in src_lines:
            line = line.strip()
            if line.endswith(":"):
                break
    return "".join(src_lines)


@register_tool(
    typ="filter",
    group="format",
    icon="mdi:function",
    examples=[
        Example(title="basic", template="""{{ "".removesuffix | format_signature }}""")
    ],
)
@functools.cache
def format_signature(
    fn: Callable[..., Any],
    follow_wrapped: bool = True,
    eval_str: bool = True,
    remove_jinja_arg: bool = False,
) -> str:
    """Format signature of a callable.

    Args:
        fn: The callable to format the signature from
        follow_wrapped: Whether to unwrap the callable
        eval_str: Un-stringize annotations using eval
        remove_jinja_arg: If true, remove the first argument for pass_xyz decorated fns.
    """
    # fallback to non-eval on error
    if eval_str:
        try:
            sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=True)
        except (TypeError, NameError):
            sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=False)
    else:
        sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=False)
    if remove_jinja_arg and hasattr(fn, "jinja_pass_arg"):
        # for @pass_xyz decorated functions
        params = dict(sig._parameters)  # type: ignore[attr-defined]
        params.pop(next(iter(params)))
        sig._parameters = params  # type: ignore[attr-defined]
        # params = dict(sig.parameters)  # Use .parameters instead of ._parameters
        # if remove_jinja_arg and hasattr(fn, "jinja_pass_arg"):
        #     params.pop(next(iter(params)))
        #     sig = sig.replace(parameters=list(params.values()))
        # return str(sig)
    return str(sig)


@register_tool(
    typ="filter",
    group="format",
    icon="mdi:function-variant",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ filters.format_filter_signature | """
                """format_filter_signature("ffs") }}"""
            ),
        )
    ],
)
def format_filter_signature(
    fn: Callable[..., Any],
    filter_name: str,
    follow_wrapped: bool = True,
    eval_str: bool = False,
) -> str:
    """Create a signature for a jinja filter based on filter name and callable.

    Outputs text in shape of
    "code: 'str' | test(line_length: 'int' = 100)"

    Args:
        fn: The callable to format the signature from
        filter_name: Name of the jinja filter
        follow_wrapped: Whether to unwrap the callable
        eval_str: Un-stringize annotations using eval
    """
    sig = inspect.signature(fn, follow_wrapped=follow_wrapped, eval_str=eval_str)
    params = dict(sig.parameters)  # Use .parameters instead of ._parameters
    if hasattr(fn, "jinja_pass_arg"):
        # for @pass_xyz decorated functions
        params.pop(next(iter(params)))
    first_val = params.pop(next(iter(params)))
    sig = sig.replace(parameters=list(params.values()))
    return f"{first_val} | {filter_name}{sig}"


@register_tool(
    typ="filter",
    group="format",
    icon="mdi:link",
    examples=[Example(title="basic", template="""{{ "Ä test" | slugify }}""")],
)
def slugify(text: str | os.PathLike[str]) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Args:
        text: text to get a slug for
    """
    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^0-9a-zA-Z_#]+", "", text)


@register_tool(
    typ="filter",
    group="format",
    icon="mage:folder-2",
    examples=[
        Example(title="basic", template="""{{ "a_foldername" | dirname_to_title }}""")
    ],
)
def dirname_to_title(dirname: str | os.PathLike[str]) -> str:
    """Return a page tile obtained from a directory name.

    Replaces dashes and underscores with spaces and capitalizes the first letter
    in case all letters are lowercase

    Args:
        dirname: directory to get a title for
    """
    title = str(dirname)
    title = title.replace("-", " ").replace("_", " ")
    if title.lower() == title:
        title = title.capitalize()
    return title


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:text",
    examples=[
        Example(title="basic", template="""{{ "<[]>" | escape }}"""),
        Example(title="with_quotes", template="""{{ '"double" quotes' | escape }}"""),
    ],
    required_packages=["markupsafe"],
    aliases=["e"],
)
def escape(text: str) -> str:
    """Escape text using Markupsafe library.

    Args:
        text: text to escape
    """
    import markupsafe

    return markupsafe.escape(text)


@register_tool(
    typ="filter",
    group="time",
    icon="mdi:clock",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ 1594819641.9622827 | format_timestamp("%Y-%m-%d %H:%M:%S") }}"""
            ),
        )
    ],
)
def format_timestamp(timestamp: float, fmt: str) -> str:
    """Format Unix timestamp to date string.

    Args:
        timestamp: Unix timestamp to format
        fmt: Format string according to strftime() format codes

    Returns:
        Formatted date string
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    result = format_code(code, line_length=50)
