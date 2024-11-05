from __future__ import annotations

import pytest

from toolreg.tools import misc


def test_match():
    assert misc.match("a", a="hit", b="miss") == "hit"


if __name__ == "__main__":
    pytest.main([__file__])
