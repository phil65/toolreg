"""Module for handling mixed async/sync file reading with UPath objects."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from upath import UPath


if TYPE_CHECKING:
    from collections.abc import Sequence


async def read_paths(paths: Sequence[UPath]) -> dict[UPath, str | bytes]:
    """Read contents of multiple paths, using async when possible.

    Args:
        paths: Sequence of UPath objects to read

    Returns:
        Dictionary mapping paths to their contents
    """
    results: dict[UPath, str | bytes] = {}
    async_tasks: list[asyncio.Task[tuple[UPath, str | bytes]]] = []
    sync_paths: list[UPath] = []

    # Separate paths into async and sync operations
    # In the future, we might check if morefs (Async local file system) is installed
    for path in paths:
        if path.fs.async_impl:
            # Create task for async reading
            task = asyncio.create_task(_read_async(path), name=f"read_{path}")
            async_tasks.append(task)
        else:
            sync_paths.append(path)

    # Handle async reads
    if async_tasks:
        async_results = await asyncio.gather(*async_tasks)
        results.update(dict(async_results))

    # Handle sync reads
    for path in sync_paths:
        results[path] = path.read_text()

    return results


async def _read_async(path: UPath) -> tuple[UPath, str | bytes]:
    """Helper function to read a single file asynchronously.

    Args:
        path: UPath object to read

    Returns:
        Tuple of (path, content)
    """
    return path, path.fs.cat_file(path.path)


if __name__ == "__main__":

    async def main():
        paths = [
            UPath("pyproject.toml"),  # Sync local file
            UPath("https://picsum.photos/100/100"),  # Async if using HTTP filesystem
        ]
        results = await read_paths(paths)
        for path, content in results.items():
            print(f"{path}: {len(content)} characters")

    # Run with:
    asyncio.run(main())
