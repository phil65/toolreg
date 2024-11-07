"""Tests for the TOML loader."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from toolreg.registry.loaders.base import LoaderError
from toolreg.registry.loaders.toml_loader import TomlLoader


if TYPE_CHECKING:
    from upath import UPath


def test_can_load_valid_toml(temp_toml: UPath) -> None:
    """Test can_load with valid TOML file."""
    loader = TomlLoader()
    assert loader.can_load(str(temp_toml))


def test_can_load_invalid_file() -> None:
    """Test can_load with non-TOML file."""
    loader = TomlLoader()
    assert not loader.can_load("not_a_toml_file.txt")


def test_load_invalid_toml(tmp_path: UPath) -> None:
    """Test loading invalid TOML content."""
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("invalid = toml [ content")

    loader = TomlLoader()
    with pytest.raises(LoaderError):
        loader.load(str(invalid_toml))


def test_load_same_file_twice(temp_toml: UPath) -> None:
    """Test loading the same file twice only loads once."""
    loader = TomlLoader()
    loader.load(str(temp_toml))
    assert loader.is_loaded(str(temp_toml))

    # Second load should be a no-op
    loader.load(str(temp_toml))
