from __future__ import annotations

import pytest

from toolreg.tools import text as texttools


GIVEN = """def test(sth, averylongvarname, anotherlongvarname, andanother): pass"""
EXPECTED = """\
def test(
    sth,
    averylongvarname,
    anotherlongvarname,
    andanother,
):
    pass
"""


def test_removesuffix():
    assert texttools.removesuffix("Hello, World!", ", World!") == "Hello"


def test_removeprefix():
    assert texttools.removeprefix("Hello, World!", "Hello, ") == "World!"


def test_lstrip():
    assert texttools.lstrip("   Hello, World!  ") == "Hello, World!  "  # noqa: B005


def test_rstrip():
    assert texttools.rstrip("   Hello, World!  ") == "   Hello, World!"  # noqa: B005


def test_format_code():
    assert texttools.format_code(GIVEN, line_length=50) == EXPECTED
    assert texttools.format_code("invalid code!", line_length=50) == "invalid code!"


def test_format_signature():
    def test_function(a, b, c: int = 1, *args, **kwargs):
        pass

    assert (
        texttools.format_signature(test_function) == "(a, b, c: int = 1, *args, **kwargs)"
    )
    assert (
        texttools.format_signature(test_function, eval_str=False)
        == "(a, b, c: 'int' = 1, *args, **kwargs)"
    )


def test_slugify():
    assert texttools.slugify("Hello, World!") == "hello__world_"


if __name__ == "__main__":
    code = "def test(sth, fsjkdalfjksdalfjsadk, fjskldjfkdsljf, fsdkjlafjkdsafj): pass"
    text = texttools.format_code(code, line_length=50)
    print(text)


if __name__ == "__main__":
    pytest.main([__file__])
