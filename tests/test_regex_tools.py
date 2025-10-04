from __future__ import annotations

import pytest

from toolreg.tools import regex


def test_re_replace():
    assert regex.re_replace("Hello, World!", "World", "Universe") == "Hello, Universe!"
    assert (
        regex.re_replace("Hello, World!", "world", "Universe", ignorecase=True)
        == "Hello, Universe!"
    )
    assert (
        regex.re_replace(
            "Hello, World! Hello, World!",
            "World",
            "Universe",
            count=1,
        )
        == "Hello, Universe! Hello, World!"
    )


def test_re_findall():
    assert regex.re_findall("Hello, World! Hello, Universe!", "Hello") == [
        "Hello",
        "Hello",
    ]
    assert regex.re_findall(
        "Hello, World! Hello, Universe!",
        "hello",
        ignorecase=True,
    ) == ["Hello", "Hello"]
    assert regex.re_findall("Hello, World! Hello, Universe!", "Goodbye") == []


def test_re_search():
    assert regex.re_search("Hello, World! Hello, Universe!", "World") == "World"
    assert (
        regex.re_search("Hello, World! Hello, Universe!", "world", ignorecase=True)
        == "World"
    )
    assert regex.re_search("Hello, World! Hello, Universe!", "Goodbye") is None
    assert regex.re_search("A\nB", "^B", multiline=True)
    with pytest.raises(ValueError, match=r"Unknown*"):
        regex.re_search("A\nB", "^B", "x")


def test_re_escape():
    assert regex.re_escape("Hello, World!") == "Hello,\\ World!"
    assert regex.re_escape("Hello, World!", "posix_basic") == "Hello, World!"
    assert regex.re_escape("[a]", "posix_basic") == "\\[a\\]"
    with pytest.raises(NotImplementedError):
        regex.re_escape("Hello, World!", "unknown")  # type: ignore[arg-type]


if __name__ == "__main__":
    pytest.main([__file__])
