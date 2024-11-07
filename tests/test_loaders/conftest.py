"""Test fixtures and utilities for loader tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from toolreg.registry.loaders import ToolLoader
from toolreg.registry.loaders.base import BaseLoader
from toolreg.registry.registration import _registrar


if TYPE_CHECKING:
    from upath import UPath


@pytest.fixture
def example_toml_content() -> str:
    """Provide example TOML content for testing."""
    return """
    [upper_filter]
    typ = "filter"
    import_path = "str.upper"
    group = "text"
    description = "Convert string to uppercase"

    [lower_filter]
    typ = "filter"
    import_path = "str.lower"
    group = "text"
    description = "Convert string to lowercase"
    """


@pytest.fixture
def example_toml_file(tmp_path: UPath, example_toml_content: str) -> UPath:
    """Create a temporary TOML file with example content."""
    path = tmp_path / "tools.toml"
    path.write_text(example_toml_content)
    return path


@pytest.fixture
def tool_loader() -> ToolLoader:
    """Provide a fresh ToolLoader instance."""
    return ToolLoader(_registrar.registry)


class MockLoader(BaseLoader):
    """Mock loader for testing."""

    name = "mock"

    def __init__(self) -> None:
        """Initialize the mock loader."""
        super().__init__()
        self.load_called = False
        self.can_load_called = False
        self.last_source = ""

    def can_load(self, source: str) -> bool:
        """Record call and always return True."""
        self.can_load_called = True
        self.last_source = source
        return True

    def load(self, source: str, *, recursive: bool = True) -> None:
        """Record call."""
        self.load_called = True
        self.last_source = source
        self._mark_loaded(source)


@pytest.fixture
def mock_loader() -> MockLoader:
    """Provide a mock loader instance."""
    return MockLoader()
