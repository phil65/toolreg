from __future__ import annotations

import re
from typing import Final

from toolreg.dissect.docstringstyle import DocstringStyle


# Combine patterns into a dictionary
DOCSTRING_PATTERNS: Final[dict[DocstringStyle, list[re.Pattern[str]]]] = {
    DocstringStyle.GOOGLE: [
        re.compile(r"\s*Args:\s*$", re.MULTILINE),
        re.compile(r"\s*Returns:\s*$", re.MULTILINE),
        re.compile(r"\s*Raises:\s*$", re.MULTILINE),
    ],
    DocstringStyle.NUMPY: [
        re.compile(r"\s*Parameters\s*\n\s*----------\s*$", re.MULTILINE),
        re.compile(r"\s*Returns\s*\n\s*-------\s*$", re.MULTILINE),
    ],
    DocstringStyle.SPHINX: [
        re.compile(r":param\s+\w+:", re.MULTILINE),
        re.compile(r":returns?:", re.MULTILINE),
        re.compile(r":raises?\s+\w+:", re.MULTILINE),
    ],
    DocstringStyle.RST: [
        re.compile(r"\.\.\s+\w+::", re.MULTILINE),
        re.compile(r"^\s*\.\.\s+note::", re.MULTILINE),
        re.compile(r"^\s*\.\.\s+warning::", re.MULTILINE),
    ],
}
