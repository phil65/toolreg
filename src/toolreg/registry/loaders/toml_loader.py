"""TOML-based tool loader."""

from __future__ import annotations

import logging
import tomllib
from typing import TYPE_CHECKING, Any, ClassVar

from upath import UPath

from toolreg.registry import tool
from toolreg.registry.loaders.base import BaseLoader, LoaderError
from toolreg.utils import resolve


if TYPE_CHECKING:
    import os


logger = logging.getLogger(__name__)


class TomlLoader(BaseLoader):
    """Load tools from TOML configuration files."""

    name = "toml"
    VALID_EXTENSIONS: ClassVar[set[str]] = {".toml"}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TOML loader."""
        super().__init__(*args, **kwargs)
        self._processed_files: set[str] = set()
        self.metadata_kwargs = kwargs

    def can_load(self, source: str | os.PathLike[str]) -> bool:
        """Check if source is a TOML file or directory containing TOML files."""
        path = UPath(source)
        return (path.is_file() and path.suffix in self.VALID_EXTENSIONS) or path.is_dir()

    def load(
        self,
        source: str | os.PathLike[str],
        *,
        recursive: bool = True,
        key_path: str | None = None,
    ) -> None:
        """Load tools from a TOML file or directory.

        Args:
            source: Path to TOML file or directory containing TOML files
            recursive: If True, search directories recursively. Defaults to True.
            key_path: Nested path in the TOML file to load tools from. Defaults to None.

        Raises:
            LoaderError: If loading or registration fails
        """
        path = UPath(source)

        if path.is_file():
            self._load_file(path, key_path=key_path)
        elif path.is_dir():
            pattern = "**/*.toml" if recursive else "*.toml"
            for toml_path in path.glob(pattern):
                self._load_file(toml_path, key_path=key_path)
        else:
            msg = f"Invalid source path: {source}"
            raise LoaderError(msg)

    def _load_file(self, path: UPath, key_path: str | None = None) -> None:
        """Load and process tools from a single TOML file.

        Args:
            path: Path to the TOML file
            key_path: Nested path in the TOML file to load tools from. Defaults to None.

        Raises:
            LoaderError: If file parsing or tool registration fails
        """
        # Use resolved absolute path as identifier
        path_id = str(path.resolve())

        if path_id in self._processed_files:
            logger.debug("Skipping already processed file: %s", path)
            return

        try:
            content = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            msg = f"Failed to parse TOML file {path}"
            raise LoaderError(msg) from exc

        if key_path:
            keys = key_path.split("/")
            for key in keys:
                content = content.get(key, {})
                if not content:
                    msg = f"Invalid nested path {key_path} in TOML file {path}"
                    raise LoaderError(msg)

        for name, config in content.items():
            try:
                # Merge config with metadata_kwargs to override fields
                merged_config = {**config, **self.metadata_kwargs}
                metadata = tool.Tool.model_validate({
                    "name": name,
                    **merged_config,
                })

                try:
                    func = resolve.resolve(metadata.import_path)
                    if not callable(func):
                        msg = f"Resolved object {metadata.import_path} is not callable"
                        raise LoaderError(msg)
                except (ImportError, AttributeError) as exc:
                    msg = f"Failed to import {metadata.import_path}"
                    raise LoaderError(msg) from exc

                self._registry.register(func, metadata)
                logger.info("Registered tool %r from %s", name, path)

            except Exception:
                logger.exception(
                    "Failed to load tool %r from %s",
                    name,
                    path,
                )

        # Mark as processed after successful loading
        self._processed_files.add(path_id)
