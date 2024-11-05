"""Tool loading functionality for registering tools from TOML files.

This module provides functionality to load and register tools from TOML configuration
files. It supports loading from both individual files and directories, with automatic
validation and registration of tools.

Example TOML structure:
    [uppercase]
    type = "filter"
    group = "text"
    import_path = "string.upper"
    description = "Convert string to uppercase"
    icon = "mdi:format-letter-case-upper"

    [uppercase.examples.basic]
    template = "{{ 'hello' | uppercase }}"
    title = "Basic Example"
    description = "Convert to uppercase"
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

import tomli
from upath import UPath

from toolreg.registry import registry, tool
from toolreg.utils import resolve


if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)

VALID_EXTENSIONS: Final[set[str]] = {".toml"}


class ToolLoadError(Exception):
    """Base exception for tool loading errors.

    This exception is raised when critical errors occur during the tool loading
    process, such as invalid TOML syntax or unreachable import paths.
    """


class ToolLoader:
    """Load and register tools from TOML configuration files.

    This class handles the loading of tool definitions from TOML files and
    registers them with the global ToolRegistry. It supports loading from both
    individual files and directories, with validation of tool metadata and
    automatic registration.

    The loader keeps track of processed files to avoid duplicate loading and
    provides detailed logging for debugging purposes.

    Example:
        ```python
        loader = ToolLoader()

        # Load from multiple sources
        loader.load([
            UPath("tools/core.toml"),
            UPath("tools/filters/"),
        ])
        ```
    """

    def __init__(self) -> None:
        """Initialize the ToolLoader.

        Sets up the registry connection and initializes the set of loaded files.
        """
        self._registry = registry.ToolRegistry()
        self._loaded_files: set[UPath] = set()

    def load(self, paths: Sequence[UPath | str], *, recursive: bool = True) -> None:
        """Load and register tools from the specified paths.

        This method processes each provided path, loading tool definitions from
        TOML files and registering them with the global registry. It can handle
        both individual files and directories.

        Args:
            paths: Sequence of paths to process. Can be either files or directories.
                  Strings are automatically converted to UPath objects.
            recursive: If True, directories are scanned recursively for TOML files.
                      Defaults to True.

        Raises:
            ToolLoadError: If critical errors occur during loading that prevent
                          proper tool registration.

        Note:
            - Invalid paths are logged as warnings but don't stop processing
            - Individual tool loading failures are logged but don't stop the process
            - Files are only loaded once, even if referenced multiple times

        Example:
            ```python
            loader = ToolLoader()
            loader.load([
                UPath("tools/core.toml"),    # Single file
                UPath("tools/filters/"),      # Directory
                "custom/extra.toml",          # String path
            ])
            ```
        """
        upaths = [UPath(p) for p in paths]
        pattern = "**/*.toml" if recursive else "*.toml"

        for path in upaths:
            try:
                if path.is_file() and path.suffix in VALID_EXTENSIONS:
                    self._load_file(path)
                elif path.is_dir():
                    for toml_path in path.glob(pattern):
                        if toml_path not in self._loaded_files:
                            self._load_file(toml_path)
                else:
                    logger.warning("Invalid path: %s", path)
            except Exception:
                logger.exception("Failed to process %s", path)

    def _load_file(self, path: UPath) -> None:
        """Load and process tools from a single TOML file.

        Args:
            path: Path to the TOML file to process

        Raises:
            ToolLoadError: If the file cannot be read or parsed

        Note:
            Individual tool loading failures within a file are logged but don't
            prevent other tools in the same file from being loaded.
        """
        try:
            content = tomli.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            msg = f"Failed to load {path}: {exc}"
            raise ToolLoadError(msg) from exc

        for name, config in content.items():
            try:
                metadata = tool.Tool.model_validate({
                    "name": name,
                    **config,
                })

                try:
                    func = resolve.resolve(metadata.import_path)
                    assert callable(func)
                except (ImportError, AttributeError) as exc:
                    msg = f"Failed to import {metadata.import_path}"
                    raise ToolLoadError(msg) from exc

                self._registry.register(func, metadata)
                logger.info("Registered tool %r from %s", name, path)

            except Exception:
                logger.exception(
                    "Failed to load tool %r from %s",
                    name,
                    path,
                )

        self._loaded_files.add(path)


if __name__ == "__main__":
    import sys

    # Configure logging for demonstration
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
    )

    # Example usage
    loader = ToolLoader()
    loader.load(
        paths=[
            UPath("tools/text.toml"),
            UPath("tools/filters/"),
        ],
    )
