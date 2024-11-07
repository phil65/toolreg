from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, ClassVar

from upath import UPath

from toolreg.registry.loaders.base import BaseLoader, LoaderError


if TYPE_CHECKING:
    import os


class TomlLoader(BaseLoader):
    """Load tools from TOML configuration files."""

    name = "toml"
    VALID_EXTENSIONS: ClassVar = {".toml"}

    def can_load(self, source: str | os.PathLike[str]) -> bool:
        """Check if source is a TOML file."""
        path = UPath(source)
        return path.is_file() and path.suffix in self.VALID_EXTENSIONS

    def load(self, source: str) -> None:
        """Load tools from a TOML file."""
        path = UPath(source)

        if not self.can_load(source):
            msg = f"Invalid TOML source: {source}"
            raise LoaderError(msg)

        if self.is_loaded(str(path)):
            return

        try:
            content = tomllib.loads(path.read_text(encoding="utf-8"))
            assert content
            # existing TOML loading logic here
            self._mark_loaded(str(path))
        except Exception as exc:
            msg = f"Failed to load {path}"
            raise LoaderError(msg) from exc
