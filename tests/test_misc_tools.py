from __future__ import annotations

import pytest

from toolreg.tools import misc


def test_match():
    assert misc.match("a", a="hit", b="miss") == "hit"


if __name__ == "__main__":
    pytest.main([__file__])


def test_resolve_builtin_attribute():
    from toolreg.utils import resolve

    assert resolve.resolve("str") is str
    assert resolve.resolve("str.upper") is str.upper
    assert resolve.resolve("os.path.join") is __import__("os").path.join
