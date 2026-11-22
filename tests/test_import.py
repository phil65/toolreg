"""Smoke test: the package imports and reports its version."""

from __future__ import annotations

import toolreg


def test_package_imports() -> None:
    """The package can be imported and exposes a version string."""
    assert isinstance(toolreg.__version__, str)
