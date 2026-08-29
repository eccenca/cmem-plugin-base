# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`cmem-plugin-base` is a Python library providing base classes for developing eccenca Corporate Memory (CMEM) DataIntegration plugins. It is consumed by other plugin packages, not used directly.

## Commands

Uses [task](https://taskfile.dev/) as the task runner and [poetry](https://python-poetry.org/) for dependency management.

```bash
task                    # List all available tasks
poetry install          # Install dependencies

task check              # Run full test suite (linters + pytest)
task check:linters      # Run ruff, mypy, deptry, trivy
task check:pytest       # Run pytest with coverage
task check:ruff         # Lint and format check only
task check:mypy         # Type checking only
task format:fix         # Auto-fix formatting and lint issues

task build              # Build wheel and tarball
task clean              # Remove dist, caches
```

Run a single test file:
```bash
poetry run pytest tests/test_description.py
```

Run a specific test:
```bash
poetry run pytest tests/test_description.py::test_function_name
```

## Architecture

### Plugin System

Plugins are plain Python classes decorated with `@Plugin(...)` from `cmem_plugin_base.dataintegration.description`. Two base types exist:

- **`WorkflowPlugin`** (`plugins.py`) — operator in a DI workflow; implements `execute(inputs, context) -> Entities | None`
- **`TransformPlugin`** (`plugins.py`) — transform operator; implements `transform(inputs) -> Sequence[str]`

The `@Plugin` decorator registers the class in `Plugin.plugins` and generates a `PluginDescription` with metadata (label, description, categories, parameters, icon, actions).

### Parameter Types

`ParameterType[T]` (`types.py`) is the base class for all parameter types. Subclasses implement `from_string()` / `to_string()` and optionally `autocomplete()`. Built-in types live in `cmem_plugin_base/dataintegration/parameter/`:
- `choice.py` — enum-like choices
- `code.py` — code editor (SPARQL, Python, etc.)
- `dataset.py` — CMEM dataset reference
- `graph.py` — named graph URI with autocompletion
- `multiline.py` — multiline text
- `password.py` — encrypted password
- `resource.py` — DI project resource

Parameter types are auto-inferred from `__init__` type annotations; use `PluginParameter(name, param_type=...)` to override.

### Context Classes

Context objects are injected by DataIntegration at runtime; the classes in `context.py` are documentation stubs only (empty method bodies):

- `SystemContext` — DI version, CMEM/DP/DI endpoints, encrypt/decrypt
- `UserContext` — OAuth token, user URI/label
- `TaskContext` — project_id, task_id
- `WorkflowContext` — workflow_id, execution status
- `ExecutionContext` — combines system, user, task, workflow, report
- `PluginContext` — available during plugin creation/update (no task/workflow)
- `ReportContext` / `ExecutionReport` — progress reporting during execution

### Entity Model

Data flows through plugins as `Entities` objects (`entity.py`):
- `Entity(uri, values)` — one instance; `values` is a sequence of sequences of strings
- `EntitySchema(type_uri, paths)` — schema with ordered `EntityPath` list
- `Entities(entities, schema)` — lazy iterator of entities + schema

### Testing Utilities

`cmem_plugin_base/testing.py` provides concrete implementations of all context classes for use in tests (`TestExecutionContext`, `TestPluginContext`, etc.). These fetch real OAuth tokens via `cmempy` — tests that instantiate them require a running CMEM environment configured via `.env`.

### Discovery

`discovery.py` provides `import_modules()` which walks installed packages under the `cmem` namespace and collects all `@Plugin`-decorated classes into a `PluginDiscoveryResult`.

## Code Style

- Line length: 100
- Ruff with `select = ["ALL"]` and specific ignores (see `pyproject.toml`)
- mypy strict; `context.py`, `plugins.py`, `types.py` have `disable_error_code = "empty-body"` because they contain abstract-style stub methods
- Python ≥ 3.13 required