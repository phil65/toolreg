"""Package utilities for dependency detection."""

from __future__ import annotations

import importlib.util
import logging


logger = logging.getLogger(__name__)


def get_package_name(module_path: str) -> str | None:
    """Get package name from module path by taking first part.

    Args:
        module_path: Import path like "package.module.function"

    Returns:
        Package name if valid module path, None otherwise

    Example:
        >>> get_package_name("requests.sessions")
        'requests'
        >>> get_package_name("os.path")
        'os'
    """
    try:
        # Check if it's a valid module
        if not importlib.util.find_spec(module_path):
            return None

        # Take first part of the path
        return module_path.split(".")[0]

    except Exception:  # noqa: BLE001
        logger.debug("Failed to get package name for %s", module_path)
        return None
