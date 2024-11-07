"""Test fixtures for loader tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from toolreg.registry.loaders import ToolLoader
from toolreg.registry.loaders.base import BaseLoader


if TYPE_CHECKING:
    from upath import UPath


@pytest.fixture
def temp_toml(tmp_path: UPath) -> UPath:
    """Create a temporary TOML file for testing."""
    content = """
    [tool.example]
    name = "example_tool"
    version = "1.0.0"
    """
    path = tmp_path / "test.toml"
    path.write_text(content)
    return path


@pytest.fixture
def tool_loader() -> ToolLoader:
    """Provide a fresh ToolLoader instance."""
    return ToolLoader()


class MockLoader(BaseLoader):
    """Mock loader for testing."""

    name = "mock"

    def __init__(self) -> None:
        """Initialize the mock loader."""
        super().__init__()
        self.load_called = False
        self.can_load_called = False

    def can_load(self, source: str) -> bool:
        """Record call and always return True."""
        self.can_load_called = True
        self.last_source = source
        return True

    def load(self, source: str) -> None:
        """Record call."""
        self.load_called = True
        self.last_source = source
        self._mark_loaded(source)


@pytest.fixture
def mock_loader() -> MockLoader:
    """Provide a mock loader instance."""
    return MockLoader()
