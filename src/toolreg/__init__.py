"""ToolReg: main package.

A tool register.
"""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("toolreg")
__title__ = "ToolReg"

__author__ = "Philipp Temminghoff"
__author_email__ = "philipptemminghoff@googlemail.com"
__copyright__ = "Copyright (c) 2024 Philipp Temminghoff"
__license__ = "MIT"
__url__ = "https://github.com/phil65/toolreg"
__version__ = version("ToolReg")

from toolreg.registry.registration import register_tool
from toolreg.registry.example import Example

__all__ = [
    "Example",
    "__version__",
    "register_tool",
]
