"""Serialization utilities."""

from __future__ import annotations

import configparser
import io
import json
from typing import TYPE_CHECKING, Any, Literal

from jinjarope import deepmerge

from toolreg import Example, register_tool


if TYPE_CHECKING:
    from collections.abc import Callable


SerializeFormatStr = Literal["yaml", "json", "ini", "toml"]


@register_tool(
    typ="filter",
    group="serialize",
    icon="mdi:file-export",
    examples=[
        Example(
            title="basic",
            template="""{{ {"a": "b"} | serialize("toml") }}""",
        )
    ],
)
def serialize(data: Any, fmt: SerializeFormatStr, **kwargs: Any) -> str:
    """Serialize given json-like object to given format.

    Args:
        data: The data to serialize
        fmt: The serialization format
        kwargs: Keyword arguments passed to the dumper function
    """
    match fmt:
        case "yaml":
            import yamling

            return yamling.dump_yaml(data, **kwargs)
        case "json":
            return json.dumps(data, indent=4, **kwargs)
        case "ini":
            config = configparser.ConfigParser(**kwargs)
            config.read_dict(data)
            file = io.StringIO()
            with file as fp:
                config.write(fp)
                return file.getvalue()
        case "toml" if isinstance(data, dict):
            import tomli_w

            return tomli_w.dumps(data, **kwargs)
        case _:
            msg = f"Unsupported format: {fmt}"
            raise TypeError(msg)


def load_ini(data: str) -> dict[str, dict[str, str]]:
    """Load INI format string into a dictionary.

    Args:
        data: INI format string to parse

    Returns:
        Dictionary containing the parsed INI data
    """
    config = configparser.ConfigParser()
    config.read_string(data)
    return {s: dict(config.items(s)) for s in config.sections()}


@register_tool(
    typ="filter",
    group="serialize",
    icon="mdi:file-import",
    examples=[
        Example(
            title="basic",
            template="""{{ "[abc.def]\\nvalue = 1" | deserialize("toml") }}""",
        )
    ],
)
def deserialize(data: str, fmt: SerializeFormatStr, **kwargs: Any) -> Any:
    """Deserialize given string in specified format to a Python object.

    Args:
        data: The data to deserialize
        fmt: The serialization format
        kwargs: Keyword arguments passed to the loader function
    """
    match fmt:
        case "yaml":
            import yamling

            return yamling.load_yaml(data, **kwargs)
        case "json":
            return json.loads(data, **kwargs)
        case "ini":
            return load_ini(data, **kwargs)
        case "toml":
            import tomllib

            return tomllib.loads(data, **kwargs)
        case _:
            msg = f"Unsupported format: {fmt}"
            raise TypeError(msg)


@register_tool(
    typ="filter",
    group="serialize",
    icon="mdi:shovel",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ {"section1": {"section2": {"section3": "Hello, World"} } } """
                """| dig("section1", "section2") }}"""
            ),
        ),
        Example(
            title="keep_path",
            template=(
                """{{ {"section1": {"section2": {"section3": "Hello, World"} } } """
                """| dig("section1", "section2", keep_path=True) }}"""
            ),
        ),
    ],
)
def dig(
    data: dict[str, Any],
    *sections: str,
    keep_path: bool = False,
    dig_yaml_lists: bool = True,
) -> Any:
    """Try to get data with given section path from a dict-list structure.

    If a list is encountered and dig_yaml_lists is true, treat it like a list of
    {"identifier", {subdict}} items, as used in MkDocs config for
    plugins & extensions.
    If Key path does not exist, return None.

    Args:
        data: The data to dig into
        sections: Sections to dig into
        keep_path: Return result with original nesting
        dig_yaml_lists: Also dig into single-key->value pairs, as in yaml
    """
    for i in sections:
        if isinstance(data, dict):
            if child := data.get(i):
                data = child
            else:
                return None
        elif dig_yaml_lists and isinstance(data, list):
            # this part is for yaml-style listitems
            for idx in data:
                if i in idx and isinstance(idx, dict):
                    data = idx[i]
                    break
                if isinstance(idx, str) and idx == i:
                    data = idx
                    break
            else:
                return None
    if not keep_path:
        return data
    result: dict[str, dict] = {}
    new = result
    for sect in sections:
        result[sect] = data if sect == sections[-1] else {}
        result = result[sect]
    return new


@register_tool(
    typ="filter",
    group="serialize",
    icon="mdi:merge",
    examples=[
        Example(
            title="basic",
            template="""{{ {"a": {"b": 1} } | merge({"a": {"c": 2} }) }}""",
        )
    ],
)
def merge(
    target: list | dict,
    *source: list | dict,
    deepcopy: bool = False,
    mergers: dict[type, Callable[[Any, Any, Any], Any]] | None = None,
) -> list | dict:
    """Merge given data structures using mergers provided.

    Args:
        target: Data structure to merge into
        source: Data structures to merge into target
        deepcopy: Whether to deepcopy the target
        mergers: Mergers with strategies for each type (default: additive)
    """
    import copy

    if deepcopy:
        target = copy.deepcopy(target)
    context = deepmerge.DeepMerger(mergers)
    for s in source:
        target = context.merge(s, target)
    return target
