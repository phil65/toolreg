"""Module for handling mixed async/sync file reading with UPath objects."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, TypeVar

from upath import UPath


if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Sequence

T = TypeVar("T", str, bytes)
type PathType = str | os.PathLike[str]


def read_text_files_sync(paths: Sequence[PathType]) -> dict[UPath, str]:
    """Synchronous wrapper for read_text_files.

    Args:
        paths: Sequence of path-like objects to read. Can be strings, PathLike objects,
              or UPath objects

    Returns:
        Dictionary mapping UPaths to their text contents
    """
    return asyncio.run(read_text_files(paths))


def read_binary_files_sync(paths: Sequence[PathType]) -> dict[UPath, bytes]:
    """Synchronous wrapper for read_binary_files.

    Args:
        paths: Sequence of path-like objects to read. Can be strings, PathLike objects,
              or UPath objects

    Returns:
        Dictionary mapping UPaths to their binary contents
    """
    return asyncio.run(read_binary_files(paths))


async def _read_files_generic(
    paths: Sequence[PathType],
    sync_read: Callable[[UPath], T],
    async_read: Callable[[UPath], Coroutine[None, None, tuple[UPath, T]]],
) -> dict[UPath, T]:
    """Generic function to read contents of multiple paths.

    Args:
        paths: Sequence of path-like objects to read
        sync_read: Function to read file synchronously
        async_read: Function to read file asynchronously

    Returns:
        Dictionary mapping UPaths to their contents
    """
    upaths = [UPath(p) for p in paths]
    results: dict[UPath, T] = {}
    async_tasks: list[asyncio.Task[tuple[UPath, T]]] = []
    sync_paths: list[UPath] = []

    for path in upaths:
        if path.fs.async_impl:
            task = asyncio.create_task(async_read(path), name=f"read_{path}")
            async_tasks.append(task)
        else:
            sync_paths.append(path)

    if async_tasks:
        async_results = await asyncio.gather(*async_tasks)
        results.update(dict(async_results))

    for path in sync_paths:
        results[path] = sync_read(path)

    return results


async def read_text_files(paths: Sequence[PathType]) -> dict[UPath, str]:
    """Read contents of multiple paths as text, using async when possible.

    This function intelligently handles both synchronous and asynchronous file reads.
    For paths that support async operations (path.fs.async_impl = True), it will read them
    concurrently using asyncio Tasks. For paths that don't support async, it falls back
    to synchronous reading.

    Args:
        paths: Sequence of path-like objects to read. Can be strings, PathLike objects,
              or UPath objects

    Returns:
        Dictionary mapping UPaths to their text contents
    """
    return await _read_files_generic(
        paths, sync_read=lambda p: p.read_text(), async_read=_read_text_async
    )


async def read_binary_files(paths: Sequence[PathType]) -> dict[UPath, bytes]:
    """Read contents of multiple paths as binary, using async when possible.

    This function intelligently handles both synchronous and asynchronous file reads.
    For paths that support async operations (path.fs.async_impl = True), it will read them
    concurrently using asyncio Tasks. For paths that don't support async, it falls back
    to synchronous reading.

    Args:
        paths: Sequence of path-like objects to read. Can be strings, PathLike objects,
              or UPath objects

    Returns:
        Dictionary mapping UPaths to their binary contents
    """
    return await _read_files_generic(
        paths, sync_read=lambda p: p.read_bytes(), async_read=_read_binary_async
    )


async def _read_text_async(path: UPath) -> tuple[UPath, str]:
    """Helper function to read a single file asynchronously as text.

    Args:
        path: UPath object to read

    Returns:
        Tuple of (path, content)
    """
    content = path.fs.cat_file(path.path)
    if isinstance(content, bytes):
        content = content.decode()
    return path, content


async def _read_binary_async(path: UPath) -> tuple[UPath, bytes]:
    """Helper function to read a single file asynchronously as binary.

    Args:
        path: UPath object to read

    Returns:
        Tuple of (path, content)
    """
    content = path.fs.cat_file(path.path)
    if isinstance(content, str):
        content = content.encode()
    return path, content
