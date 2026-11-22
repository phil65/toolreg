# ToolReg

[![PyPI License](https://img.shields.io/pypi/l/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Package status](https://img.shields.io/pypi/status/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Monthly downloads](https://img.shields.io/pypi/dm/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Distribution format](https://img.shields.io/pypi/format/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Wheel availability](https://img.shields.io/pypi/wheel/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Python version](https://img.shields.io/pypi/pyversions/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Implementation](https://img.shields.io/pypi/implementation/toolreg.svg)](https://pypi.org/project/toolreg/)
[![Releases](https://img.shields.io/github/downloads/phil65/toolreg/total.svg)](https://github.com/phil65/toolreg/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/toolreg)](https://github.com/phil65/toolreg/graphs/contributors)
[![Github Forks](https://img.shields.io/github/forks/phil65/toolreg)](https://github.com/phil65/toolreg/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/toolreg)](https://github.com/phil65/toolreg/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/toolreg)](https://github.com/phil65/toolreg/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/toolreg)](https://github.com/phil65/toolreg/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/toolreg)](https://github.com/phil65/toolreg/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/toolreg)](https://github.com/phil65/toolreg)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/toolreg)](https://github.com/phil65/toolreg/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/toolreg)](https://github.com/phil65/toolreg/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/toolreg)](https://github.com/phil65/toolreg)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/toolreg)](https://github.com/phil65/toolreg)
[![Package status](https://codecov.io/gh/phil65/toolreg/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/toolreg/)
[![PyUp](https://pyup.io/repos/github/phil65/toolreg/shield.svg)](https://pyup.io/repos/github/phil65/toolreg/)

[Read the documentation!](https://phil65.github.io/toolreg/)

ToolReg is a registry for [Jinja2](https://jinja.palletsprojects.com/) filters, tests and
functions. Each registered callable carries metadata (group, icon, aliases, usage examples,
required packages); missing fields are filled in from the signature and docstring. ToolReg also
ships a library of ready-made filters for text, HTML, iterables, serialization, regex, Markdown
and icons.

## Installation

```bash
pip install toolreg
```

Requires Python 3.13 or newer.

## Quickstart

Register a filter with the `register_tool` decorator and put the registry into a Jinja
environment:

```python
import jinja2

from toolreg import Example, register_tool
from toolreg.registry.registration import _registrar


@register_tool(
    typ="filter",
    group="text",
    icon="mdi:format-letter-case-upper",
    examples=[Example(title="basic", template="{{ 'hello' | shout }}")],
)
def shout(value: str) -> str:
    """Convert a string to uppercase and add an exclamation mark."""
    return f"{value.upper()}!"


registry = _registrar.registry
func, tool = registry.get_all()["shout"]
print(tool.group, tool.description)  # text Convert a string to uppercase and ...

env = jinja2.Environment()
env.filters.update({name: f for name, (f, _) in registry.get_all("filter").items()})
print(env.from_string("{{ 'hello' | shout }}").render())  # HELLO!
```

Importing a module from `toolreg.tools` registers its built-in tools:

```python
import toolreg.tools.iterate  # noqa: F401

env.filters.update({name: f for name, (f, _) in registry.get_all("filter").items()})
print(env.from_string("{{ ['apple', 'banana', 'avocado'] | groupby_first_letter }}").render())
# {'A': ['apple', 'avocado'], 'B': ['banana']}
```

## Loading tools from TOML or modules

`ToolLoader` registers tools from a TOML file (or a directory of them) or from all public
functions of a Python module:

```toml
# tools.toml
[upper_filter]
typ = "filter"
import_path = "str.upper"
group = "text"
description = "Convert string to uppercase"
```

```python
from toolreg.registry.loaders import ToolLoader

loader = ToolLoader(registry)
loader.load("tools.toml")  # TOML file or directory
loader.load("textwrap")  # every public function of a module
```

## Features

- `@register_tool` decorator for filters, tests and functions, with groups, aliases, icons
  and Jinja usage examples
- Metadata extraction from signatures and docstrings (Google, NumPy, Sphinx styles)
- Loaders for TOML definitions and Python modules
- Built-in tool modules: `text`, `html`, `iterate`, `serialize`, `regex`, `mkdown`, `icon`,
  `misc`, `inspection`, `tests`
- Typed pydantic models (`Tool`, `Example`)
