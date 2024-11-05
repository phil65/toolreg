from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum, auto

import griffe


type DocstringSections = list[griffe.DocstringSection]
type ExampleFormatter = Callable[[str], str]
type StyleType = str | DocstringStyle


class DocstringStyle(StrEnum):
    """Enumeration of supported docstring styles."""

    GOOGLE = auto()
    NUMPY = auto()
    SPHINX = auto()
    RST = auto()
    PLAIN = auto()

    @classmethod
    def is_valid(cls, style: str) -> bool:
        """Check if a style string is valid.

        Args:
            style: Style string to validate

        Returns:
            True if style is valid
        """
        return style.lower() in ("google", "numpy", "sphinx", "plain", "auto")
