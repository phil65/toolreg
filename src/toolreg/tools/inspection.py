"""Module providing inspection utility functions."""

from __future__ import annotations

import contextlib
import functools
import inspect
import logging
import types
from typing import TYPE_CHECKING, Any

from upath import UPath

from toolreg import Example, register_tool


if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


logger = logging.getLogger(__name__)


HasCodeType = (
    types.ModuleType
    | type
    | types.MethodType
    | types.FunctionType
    | types.TracebackType
    | types.FrameType
    | types.CodeType
    | types.BuiltinFunctionType
)


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:family-tree",
    examples=[Example(title="basic", template="""{{ list | list_subclasses }}""")],
)
@functools.cache
def list_subclasses(
    klass: type,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[type]:
    """Return list of all subclasses of given class.

    Args:
        klass: class to get subclasses from
        recursive: whether to also get subclasses of subclasses
        filter_abstract: whether abstract base classes should be included
        filter_generic: whether generic base classes should be included
        filter_locals: whether local base classes should be included
    """
    return list(
        iter_subclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        ),
    )


def iter_subclasses(
    klass: type,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> Iterator[type]:
    """Iterate all subclasses of given class.

    Args:
        klass: class to get subclasses from
        recursive: whether to also get subclasses of subclasses
        filter_abstract: whether abstract base classes should be included
        filter_generic: whether generic base classes should be included
        filter_locals: whether local base classes should be included
    """
    if getattr(klass.__subclasses__, "__self__", None) is None:
        return
    for cls in klass.__subclasses__():
        if recursive:
            yield from iter_subclasses(
                cls,
                filter_abstract=filter_abstract,
                filter_generic=filter_generic,
                filter_locals=filter_locals,
            )
        if filter_abstract and inspect.isabstract(cls):
            continue
        if filter_generic and cls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in cls.__qualname__:
            continue
        yield cls


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:family-tree",
    examples=[Example(title="basic", template="""{{ zip | list_baseclasses }}""")],
)
@functools.cache
def list_baseclasses(
    klass: type,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[type]:
    """Return list of all base classes of given class.

    Args:
        klass: class to get base classes from
        recursive: whether to also get base classes of base classes
        filter_abstract: whether abstract base classes should be included
        filter_generic: whether generic base classes should be included
        filter_locals: whether local base classes should be included
    """
    return list(
        iter_baseclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        ),
    )


def iter_baseclasses(
    klass: type,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> Iterator[type]:
    """Iterate all base classes of given class.

    Args:
        klass: class to get base classes from
        recursive: whether to also get base classes of base classes
        filter_abstract: whether abstract base classes should be included
        filter_generic: whether generic base classes should be included
        filter_locals: whether local base classes should be included
    """
    for cls in klass.__bases__:
        if recursive:
            yield from iter_baseclasses(
                cls,
                recursive=recursive,
                filter_abstract=filter_abstract,
                filter_generic=filter_generic,
                filter_locals=filter_locals,
            )
        if filter_abstract and inspect.isabstract(cls):
            continue
        if filter_generic and cls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in cls.__qualname__:
            continue
        yield cls


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:file-document",
    examples=[Example(title="basic", template="""{{ filters.get_doc | get_doc }}""")],
)
@functools.cache
def get_doc(
    obj: Any,
    *,
    escape: bool = False,
    fallback: str = "",
    from_base_classes: bool = False,
    only_summary: bool = False,
    only_description: bool = False,
) -> str:
    """Get __doc__ for given object.

    Args:
        obj: Object to get docstrings from
        escape: Whether docstrings should get escaped
        fallback: Fallback in case docstrings dont exist
        from_base_classes: Use base class docstrings if docstrings dont exist
        only_summary: Only return first line of docstrings
        only_description: Only return block after first line
    """
    from toolreg.tools import mkdown

    match obj:
        case _ if from_base_classes:
            doc = inspect.getdoc(obj)
        case _ if obj.__doc__:
            doc = inspect.cleandoc(obj.__doc__)
        case _:
            doc = None
    if not doc:
        return fallback
    if only_summary:
        doc = doc.split("\n")[0]
    if only_description:
        doc = "\n".join(doc.split("\n")[1:])
    return mkdown.md_escape(doc) if doc and escape else doc


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:function",
    examples=[Example(title="basic", template="""{{ filters.get_argspec | get_argspec }}""")],
)
def get_argspec(obj: Any, remove_self: bool = True) -> inspect.FullArgSpec:
    """Return a cleaned-up FullArgSpec for given callable.

    ArgSpec is cleaned up by removing `self` from method callables.

    Args:
        obj: A callable python object
        remove_self: Whether to remove "self" argument from method argspecs
    """
    if inspect.isfunction(obj):
        argspec = inspect.getfullargspec(obj)
    elif inspect.ismethod(obj):
        argspec = inspect.getfullargspec(obj)
        if remove_self:
            del argspec.args[0]
    elif inspect.isclass(obj):
        if obj.__init__ is object.__init__:  # to avoid an error
            argspec = inspect.getfullargspec(lambda self: None)
        else:
            argspec = inspect.getfullargspec(obj.__init__)
        if remove_self:
            del argspec.args[0]
    elif isinstance(obj, types.BuiltinFunctionType | types.BuiltinMethodType):
        argspec = inspect.getfullargspec(obj)
        if remove_self:
            del argspec.args[0]
    else:
        msg = f"{obj} is not callable"
        raise TypeError(msg)
    return argspec


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:alert",
    examples=[],
)
def get_deprecated_message(obj: Any) -> str | None:
    """Return deprecated message (created by deprecated decorator).

    Args:
        obj: Object to check
    """
    return obj.__deprecated__ if hasattr(obj, "__deprecated__") else None


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:code-braces",
    examples=[Example(title="basic", template="""{{ filters.get_source | get_source }}""")],
)
@functools.cache
def get_source(obj: HasCodeType) -> str:
    """Get source code for given object.

    Args:
        obj: Object to return source for
    """
    return inspect.getsource(obj)


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:code-array",
    examples=[
        Example(
            title="basic",
            template="""{{ filters.get_source_lines | get_source_lines }}""",
        )
    ],
)
@functools.cache
def get_source_lines(obj: HasCodeType) -> tuple[list[str], int]:
    """Get source lines for given object.

    Args:
        obj: Object to return source lines for
    """
    return inspect.getsourcelines(obj)


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:function",
    examples=[],
)
@functools.cache
def get_signature(obj: Any) -> inspect.Signature:
    """Get signature for given callable.

    Args:
        obj: Callable to get a signature for
    """
    return inspect.signature(obj)


@register_tool(
    typ="filter",
    group="inspect",
    icon="mdi:file-find",
    examples=[Example(title="basic", template="""{{ filters.get_file | get_file }}""")],
)
@functools.cache
def get_members(obj: object, predicate: Callable[[Any], bool] | None = None):
    """Cached version of inspect.getmembers.

    Args:
        obj: Object to get members for
        predicate: Optional predicate for the members
    """
    return inspect.getmembers(obj, predicate)


@functools.cache
def get_file(obj: HasCodeType) -> UPath | None:
    """Cached wrapper for inspect.getfile.

    Args:
        obj: Object to get file for
    """
    with contextlib.suppress(TypeError):
        return UPath(inspect.getfile(obj))
    return None


if __name__ == "__main__":
    print(get_doc(str))
