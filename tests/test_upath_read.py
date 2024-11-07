"""Tests for upath_read module."""

from __future__ import annotations

import pytest
from upath import UPath

from toolreg.utils import upath_read


@pytest.fixture
def tmp_upath(tmp_path):
    """A pytest fixture that wraps the standard tmp_path fixture with a UPath object."""
    return UPath(tmp_path)


@pytest.fixture
def text_content() -> str:
    """Sample text content for testing."""
    return "Hello, World!"


@pytest.fixture
def binary_content() -> bytes:
    """Sample binary content for testing."""
    return b"Hello, Binary World!"


@pytest.fixture
def temp_text_file(tmp_upath: UPath, text_content: str) -> UPath:
    """Create a temporary text file for testing."""
    file_path = tmp_upath / "test.txt"
    file_path.write_text(text_content)
    return file_path


@pytest.fixture
def temp_binary_file(tmp_upath: UPath, binary_content: bytes) -> UPath:
    """Create a temporary binary file for testing."""
    file_path = tmp_upath / "test.bin"
    file_path.write_bytes(binary_content)
    return file_path


@pytest.mark.asyncio
async def test_read_text_files(
    temp_text_file: UPath,
    text_content: str,
) -> None:
    """Test reading text files."""
    results = await upath_read.read_text_files([temp_text_file])
    assert results[temp_text_file] == text_content
    assert isinstance(results[temp_text_file], str)


@pytest.mark.asyncio
async def test_read_binary_files(
    temp_binary_file: UPath,
    binary_content: bytes,
) -> None:
    """Test reading binary files."""
    results = await upath_read.read_binary_files([temp_binary_file])
    assert results[temp_binary_file] == binary_content
    assert isinstance(results[temp_binary_file], bytes)


@pytest.mark.asyncio
async def test_read_text_files_empty_list() -> None:
    """Test reading an empty list of text files."""
    results = await upath_read.read_text_files([])
    assert results == {}


@pytest.mark.asyncio
async def test_read_binary_files_empty_list() -> None:
    """Test reading an empty list of binary files."""
    results = await upath_read.read_binary_files([])
    assert results == {}


@pytest.mark.asyncio
async def test_read_text_files_nonexistent_file(tmp_upath: UPath) -> None:
    """Test reading a nonexistent text file raises an error."""
    nonexistent_file = tmp_upath / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        await upath_read.read_text_files([nonexistent_file])


@pytest.mark.asyncio
async def test_read_binary_files_nonexistent_file(tmp_upath: UPath) -> None:
    """Test reading a nonexistent binary file raises an error."""
    nonexistent_file = tmp_upath / "nonexistent.bin"
    with pytest.raises(FileNotFoundError):
        await upath_read.read_binary_files([nonexistent_file])


@pytest.mark.asyncio
async def test_read_text_files_multiple(tmp_upath: UPath, text_content: str) -> None:
    """Test reading multiple text files."""
    file1 = tmp_upath / "test1.txt"
    file2 = tmp_upath / "test2.txt"
    file1.write_text(text_content)
    file2.write_text(text_content)

    results = await upath_read.read_text_files([file1, file2])
    assert len(results) == 2  # noqa: PLR2004
    assert all(isinstance(content, str) for content in results.values())
    assert all(content == text_content for content in results.values())


@pytest.mark.asyncio
async def test_read_binary_files_multiple(
    tmp_upath: UPath, binary_content: bytes
) -> None:
    """Test reading multiple binary files."""
    file1 = tmp_upath / "test1.bin"
    file2 = tmp_upath / "test2.bin"
    file1.write_bytes(binary_content)
    file2.write_bytes(binary_content)

    results = await upath_read.read_binary_files([file1, file2])
    assert len(results) == 2  # noqa: PLR2004
    assert all(isinstance(content, bytes) for content in results.values())
    assert all(content == binary_content for content in results.values())


@pytest.mark.asyncio
async def test_read_text_files_with_str_path(tmp_path, text_content: str) -> None:
    """Test reading text files using string paths."""
    file_path = tmp_path / "test.txt"
    file_path.write_text(text_content)

    # Use string path instead of UPath
    str_path = str(file_path)
    results = await upath_read.read_text_files([str_path])

    upath = UPath(str_path)
    assert results[upath] == text_content
    assert isinstance(results[upath], str)


@pytest.mark.asyncio
async def test_read_binary_files_with_pathlike(tmp_path, binary_content: bytes) -> None:
    """Test reading binary files using PathLike objects."""
    file_path = tmp_path / "test.bin"
    file_path.write_bytes(binary_content)

    # Use PathLike object
    results = await upath_read.read_binary_files([file_path])

    upath = UPath(file_path)
    assert results[upath] == binary_content
    assert isinstance(results[upath], bytes)


@pytest.mark.asyncio
async def test_read_text_files_mixed_path_types(
    tmp_path, tmp_upath: UPath, text_content: str
) -> None:
    """Test reading text files using mixed path types."""
    # Create files with different path types
    str_path = str(tmp_path / "str_file.txt")
    pathlike_path = tmp_path / "pathlike_file.txt"
    upath_path = tmp_upath / "upath_file.txt"

    # Write content to all files
    for path in [str_path, pathlike_path, upath_path]:
        UPath(path).write_text(text_content)

    # Read using mixed path types
    results = await upath_read.read_text_files([str_path, pathlike_path, upath_path])

    # Check results
    assert len(results) == 3  # noqa: PLR2004
    for path in results:
        assert isinstance(path, UPath)
        assert results[path] == text_content
        assert isinstance(results[path], str)
