from __future__ import annotations

import functools
import importlib
from typing import TYPE_CHECKING, Any

from toolreg.tools import tests


if TYPE_CHECKING:
    from collections.abc import Callable
    import types


@functools.cache
def resolve(
    name: str,
    module: str | None = None,
) -> types.ModuleType | Callable[..., Any]:
    """Resolve ``name`` to a Python object via imports / attribute lookups.

    If ``module`` is None, ``name`` must be "absolute" (no leading dots).

    If ``module`` is not None, and ``name`` is "relative" (has leading dots),
    the object will be found by navigating relative to ``module``.

    Returns the object, if found.  If not, propagates the error.
    """
    names = name.split(".")
    if not names[0]:
        if module is None:
            msg = "relative name without base module"
            raise ValueError(msg)
        modules = module.split(".")
        names.pop(0)
        while not name[0]:
            modules.pop()
            names.pop(0)
        names = modules + names

    used = names.pop(0)
    if tests.is_python_builtin(used):
        import builtins

        return getattr(builtins, used)
    found = importlib.import_module(used)
    for n in names:
        used += "." + n
        try:
            found = getattr(found, n)
        except AttributeError:
            try:
                importlib.import_module(used)
                found = getattr(found, n)
            except ModuleNotFoundError:
                mod = ".".join(used.split(".")[:-1])
                importlib.import_module(mod)
                found = getattr(found, n)
    return found
