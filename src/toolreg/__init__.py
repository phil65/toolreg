from __future__ import annotations

from importlib.metadata import version

__version__ = version("ToolReg")

from toolreg.registry.registration import register_tool
from toolreg.registry.example import Example

__all__ = [
    "Example",
    "__version__",
    "register_tool",
]
