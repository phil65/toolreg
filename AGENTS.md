# AGENTS.md

## Overview

ToolReg is a registry for Jinja2 "tools" (filters, tests, functions). Callables are registered
with metadata (group, icon, aliases, examples, required packages) that is partly extracted from
signatures and docstrings, so environments and docs can be built from the registry. The package
also ships a library of ready-made tools in `toolreg.tools`. Python >= 3.13, pydantic v2.

## Architecture

- `src/toolreg/__init__.py`: public API: `register_tool` (decorator) and `Example`.
- `src/toolreg/registry/`
  - `registry.py`: `ToolRegistry` (name/alias -> `(func, Tool)`), `ItemType` literal.
  - `tool.py`: `Tool` pydantic model; `Tool.from_function()` builds metadata via `dissect`.
  - `registration.py`: `ToolRegistrar` and the module-level `_registrar` /
    `register_tool`. Decorating registers into this **global** registry at import time.
  - `example.py`: `Example` model (Jinja template snippet) and `get_example_value()`.
  - `loaders/`: `ToolLoader` (`__init__.py`) dispatches to `TomlLoader` (file/dir with
    `[name]` tables holding `typ`, `import_path`, ...), `ModuleLoader` (registers every public
    function of an importable module) and `PluginLoader` (stub, does not register anything).
  - `registryevents.py`: event hooks (`RegistryEvents` protocol, metrics/logging handlers,
    `wrap_function`). Not wired into the registry.
- `src/toolreg/dissect/`: docstring/signature analysis (`inspect_function.py`, griffe-based
  `docstringstyler.py`, `categorize.py`).
- `src/toolreg/tools/`: the tool library, one module per group (`text`, `html`, `iterate`,
  `serialize`, `icon`, `regex`, `mkdown`, `misc`, `inspection`, `tests`, `llm`). Importing a
  module registers its tools via `@register_tool`.
- `src/toolreg/utils/`: helpers (`resolve.py` import-path resolution, `slugfield.py`,
  `icons.py` pyconify/material icon index using `resources/icons.json.gzip`, `filetree.py`,
  `codetree.py`, `deepmerge.py`, `decorators.py`).
- `src/toolreg/examples/`: example generation strategies (`examplegenerator.py`, ...).
- `src/toolreg/resources/*.toml`: tool definitions in an older jinjarope-style schema
  (`[filters.name]` with `fn = ...`). They do **not** match the `TomlLoader` schema and are not
  loaded by package code.

Flow: `@register_tool(typ=..., group=...)` -> `ToolRegistrar.register()` ->
`Tool.from_function()` (dissect docstring/signature) -> `ToolRegistry.register()`.

## Where to look

| Task | Location |
| --- | --- |
| Registration / decorator behaviour | `src/toolreg/registry/registration.py` |
| Tool metadata fields | `src/toolreg/registry/tool.py` |
| Load tools from TOML / modules | `src/toolreg/registry/loaders/` |
| Add or change a filter | `src/toolreg/tools/<group>.py` |
| Docstring parsing | `src/toolreg/dissect/` |
| Icons | `src/toolreg/tools/icon.py`, `src/toolreg/utils/icons.py` |
| Tests | `tests/test_<module>_tools.py`, `tests/test_loaders/` |
| CI | `.github/workflows/build.yml`, `.github/workflows/documentation.yml` |

## Commands

```bash
uv sync --all-extras                 # setup (default groups: dev, lint, docs)
uv run pytest                        # tests (asyncio_mode = auto)
uv run ruff check . && uv run ruff format --check .
uv run ty check                      # type check (src only); warnings fail
uv run deptry src                    # dependency declaration check
uv run mkdocs-mknodes build          # docs (README + auto-generated API pages)
uv build
uvx duty lint | test | build | serve   # wrappers from duties.py (duty is not a project dep)
```

## Conventions

- `from __future__ import annotations` everywhere; Google-style docstrings; line length 100.
- Every tool takes `@register_tool(typ=..., group=..., icon="mdi:...", examples=[Example(...)])`.
  `Example.template` is a Jinja snippet using the tool.
- Optional/heavy imports (e.g. `pyconify`, `natsort`, `configz`, `litellm`, `httpx`) are done
  inside the function body, not at module level.
- ty: use targeted `# ty: ignore[rule]`, not mypy-style `# type: ignore[...]`. `Callable`
  has no `__name__` for ty, hence the `missing-attribute` ignores.
- Tests are plain pytest functions mirroring `src/toolreg/tools/<module>.py`.

## Pitfalls

- Copier-managed project (`.copier-answers.yml`, template `copier-phil65`): workflows,
  `duties.py`, `.pre-commit-config.yaml` and most of `pyproject.toml` come from the template.
  Add dependencies below the `# Only add below (Copier)` markers.
- The global registry is shared process-wide; tests that register tools affect each other.
  `ToolLoader()` without an argument creates a separate registry.
- `text.format_code` shells out to `ruff format` with the current working directory, so the
  caller's ruff config (line length) applies.
- `tools/llm.py` calls `load_dotenv()` at import time and needs `litellm` (not a dependency).
- Importing tool modules emits griffe warnings for unannotated parameters; harmless.
- `text.md` (repo root) and `src/toolreg/download_tool.md` are design notes, not docs.
