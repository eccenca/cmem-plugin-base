# Migrate from cmempy to cmem-client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `cmem-cmempy` with `cmem-client` (eccenca's typed, httpx-based successor) as the HTTP client library backing `cmem-plugin-base`, across production code, the public `cmem_plugin_base.testing` helpers, and the integration test suite.

**Architecture:** `cmempy` works through global `os.environ` mutation (`setup_cmempy_user_access`) that every subsequent cmempy call implicitly reads. `cmem-client` is object-based: you build a `cmem_client.client.Client` from a `Config` + `AuthProvider` and call methods on it. `cmem-client` ships a purpose-built bridge for this exact library — `Client.from_context(context)` reads straight from `cmem_plugin_base`'s `PluginContext`/`ExecutionContext` — but one call site (`typed_entities/file.py`'s `File.read_stream(project_id)`) has no context object at all, only a bare `project_id`, because it's a public method downstream plugins already call. For that site we keep an **ambient fallback**: `setup_cmem_client()` still sets the same `OAUTH_GRANT_TYPE` / `OAUTH_ACCESS_TOKEN` / `CMEM_BASE_URI` environment variables cmempy used to set, and `File.read_stream` builds `Client.from_env()` when no explicit client is passed in. This was chosen over a hard signature break (rejected — breaks every downstream plugin holding a `File`) and over inventing new contextvar plumbing (rejected — env vars already do this job and cmem-client already has an `Client.from_env()` entry point that reads them).

**Tech Stack:** `cmem-client` (PyPI `cmem-client`, pin `^0.16.0`), `httpx` (transitive, used by cmem-client), `pydantic` (already a direct dependency), `pytest` / `pytest-dotenv` for the existing `needs_cmem`-gated integration tests.

## Global Constraints

- Python `>=3.13` (already the floor in `pyproject.toml`; `cmem-client` requires `>=3.13,<4`, so no floor change needed).
- No new `cmem.cmempy*` imports may remain anywhere in `cmem_plugin_base/` or `tests/` once this plan is complete — verify with `grep -rn "cmem\.cmempy" cmem_plugin_base tests`.
- `cmem-cmempy` is removed entirely from `pyproject.toml` (both `[tool.poetry.dependencies]` and dev group — it isn't in the dev group today, but double-check after `poetry lock`).
- Public function names `setup_cmempy_user_access` and `setup_cmempy_super_user_access` in `cmem_plugin_base.dataintegration.utils` are **kept as deprecated wrappers** around the new `setup_cmem_client` / `setup_cmem_client_super_user_access` functions — downstream plugins may call them directly today, so removing them outright would be a breaking release. They keep their exact old signature and `None` return type.
- `File.read_stream()` and its convenience methods (`is_text`, `is_bytes`, `read_text`, `read_bytes`, `text_stream`, `bytes_stream`) gain an **optional, additive** `client: Client | None = None` parameter — non-breaking for existing callers.
- `write_to_dataset()` keeps its exact signature (`dataset_id`, `file_resource`, `context: UserContext | None`) but its **return type changes from `requests.Response` to `None`**, and the exception raised on an HTTP failure changes from `requests.exceptions.HTTPError` to `httpx.HTTPStatusError`. This is an unavoidable, intentional breaking change inherent to swapping `requests`-based `cmempy` for `httpx`-based `cmem-client` — call it out explicitly in the CHANGELOG (Task 10).
- Every task that touches a `@needs_cmem`-marked test requires a live Corporate Memory instance reachable via `CMEM_BASE_URI` (plus `OAUTH_CLIENT_ID`/`OAUTH_CLIENT_SECRET` or whichever `OAUTH_GRANT_TYPE` is configured) to actually execute; if none is available in your environment, run `poetry run pytest -k "not needs_cmem" ...` — no, `needs_cmem` is a `skipif`, not a `-k` filter, so just run `poetry run pytest` and confirm the marked tests are reported as **skipped**, not failed/errored, plus run `ruff`/`mypy` which don't need a live instance.

---

### Task 1: Swap the dependency

**Files:**
- Modify: `pyproject.toml:28-32`

**Interfaces:**
- Produces: `cmem_client` importable at `>=0.16.0,<0.17.0` for every later task.

- [ ] **Step 1: Edit the dependency**

In `pyproject.toml`, under `[tool.poetry.dependencies]`, replace:

```toml
cmem-cmempy = "^25.4.0"
```

with:

```toml
cmem-client = "^0.16.0"
```

- [ ] **Step 2: Re-lock**

```bash
poetry lock
poetry install
```

Expected: lock file updates, `cmem-cmempy` disappears from `poetry.lock`, `cmem-client` (and its transitive deps `httpx`, `pyjwt`, `rdflib`) appear.

- [ ] **Step 3: Confirm the import works**

```bash
poetry run python -c "from cmem_client.client import Client; print(Client)"
```

Expected: prints `<class 'cmem_client.client.Client'>` with no import error.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml poetry.lock
git commit -m "build: replace cmem-cmempy dependency with cmem-client"
```

---

### Task 2: Replace the auth/env helpers in `utils/__init__.py`

**Files:**
- Modify: `cmem_plugin_base/dataintegration/utils/__init__.py`

**Interfaces:**
- Consumes: `cmem_client.client.Client`, `cmem_client.config.Config`, `cmem_client.auth_provider.prefetched_token.PrefetchedToken`, `cmem_client.auth_provider.client_credentials.ClientCredentialsFlow`.
- Produces: `setup_cmem_client(context: UserContext | None) -> Client`, `setup_cmem_client_super_user_access() -> Client`, `write_to_dataset(...) -> None`. Kept for backward compatibility: `setup_cmempy_user_access(context) -> None`, `setup_cmempy_super_user_access() -> None`. These four names are what Tasks 3–7 import.

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `cmem_plugin_base/dataintegration/utils/__init__.py` with:

```python
"""Utils for dataintegration plugins."""

import os
import re
from typing import IO

from cmem_client.auth_provider.client_credentials import ClientCredentialsFlow
from cmem_client.auth_provider.prefetched_token import PrefetchedToken
from cmem_client.client import Client
from cmem_client.config import Config

from cmem_plugin_base.dataintegration.context import UserContext


def generate_id(name: str) -> str:
    """Generate a valid DataIntegration identifier from a string.

    Characters that are not allowed in an identifier are removed.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def setup_cmem_client(context: UserContext | None) -> Client:
    """Build a cmem-client Client for the given user context.

    Also sets OAUTH_GRANT_TYPE/OAUTH_ACCESS_TOKEN/CMEM_BASE_URI in the process
    environment, mirroring what cmempy used to do, so that code building a
    Client via Client.from_env() (e.g. File.read_stream's ambient fallback)
    picks up the same identity without being passed a context.
    """
    if context is None:
        raise ValueError("No UserContext given.")
    token = context.token()
    if token is None:
        raise ValueError("UserContext has no token.")
    os.environ["OAUTH_GRANT_TYPE"] = "prefetched_token"
    os.environ["OAUTH_ACCESS_TOKEN"] = token
    if "CMEM_BASE_URI" not in os.environ:
        os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]
    config = Config(url_base=os.environ["CMEM_BASE_URI"])
    return Client(config=config, auth=PrefetchedToken(prefetched_token=token))


def setup_cmempy_user_access(context: UserContext | None) -> None:
    """Set up environment for accessing CMEM.

    Deprecated: use setup_cmem_client(context) instead, which returns a
    ready-to-use cmem_client.Client instead of only mutating the environment.
    """
    setup_cmem_client(context)


def setup_cmem_client_super_user_access() -> Client:
    """Build a cmem-client Client using client-credentials (super user) authentication.

    Uses an already-working environment if present. If not, falls back to the
    configured DI service account (DATAINTEGRATION_CMEM_SERVICE_CLIENT[_SECRET]).
    """
    try:
        os.environ["OAUTH_GRANT_TYPE"] = "client_credentials"
        if "CMEM_BASE_URI" not in os.environ:
            os.environ["CMEM_BASE_URI"] = os.environ["DEPLOY_BASE_URL"]
        if "OAUTH_CLIENT_ID" not in os.environ:
            os.environ["OAUTH_CLIENT_ID"] = os.environ["DATAINTEGRATION_CMEM_SERVICE_CLIENT"]
        if "OAUTH_CLIENT_SECRET" not in os.environ:
            os.environ["OAUTH_CLIENT_SECRET"] = os.environ[
                "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET"
            ]
    except KeyError as error:
        raise ValueError("Super user configuration not available.") from error
    config = Config(url_base=os.environ["CMEM_BASE_URI"])
    auth = ClientCredentialsFlow(
        config=config,
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    )
    return Client(config=config, auth=auth)


def setup_cmempy_super_user_access() -> None:
    """Set up environment for accessing CMEM as a super user.

    Deprecated: use setup_cmem_client_super_user_access() instead, which
    returns a ready-to-use cmem_client.Client instead of only mutating the
    environment.
    """
    setup_cmem_client_super_user_access()


def split_task_id(task_id: str) -> tuple:
    """Split a combined task ID.

    Args:
        task_id (str): The combined task ID.

    Returns:
        The project and task ID

    Raises:
        ValueError: in case the task ID is not splittable

    """
    try:
        project_part = task_id.split(":", maxsplit=1)[0]
        task_part = task_id.split(":")[1]
    except IndexError as error:
        raise ValueError(f"{task_id} is not a valid task ID.") from error
    return project_part, task_part


def write_to_dataset(  # noqa: ANN201
    dataset_id: str, file_resource: IO | None = None, context: UserContext | None = None
):
    """Write to a dataset.

    Args:
        dataset_id (str): The combined task ID.
        file_resource (file stream): Already opened byte file stream
        context (UserContext):
            The user context to setup environment for accessing CMEM.

    Returns:
        None

    Raises:
        ValueError: in case the task ID is not splittable
        ValueError: missing parameter
        httpx.HTTPStatusError: if the upload request fails

    """
    client = setup_cmem_client(context)
    project_id, task_id = split_task_id(dataset_id)

    client.datasets.post_file_resource(
        project_id=project_id,
        dataset_id=task_id,
        file_resource=file_resource,
    )
```

- [ ] **Step 2: Type-check and lint just this file**

```bash
poetry run ruff check cmem_plugin_base/dataintegration/utils/__init__.py
poetry run ruff format --check cmem_plugin_base/dataintegration/utils/__init__.py
poetry run mypy -p cmem_plugin_base.dataintegration.utils
```

Expected: no errors. If `ruff format --check` fails, run `poetry run ruff format cmem_plugin_base/dataintegration/utils/__init__.py` and re-check.

- [ ] **Step 3: Commit**

```bash
git add cmem_plugin_base/dataintegration/utils/__init__.py
git commit -m "refactor: rebuild cmem_plugin_base.dataintegration.utils on cmem-client"
```

---

### Task 3: Migrate `DatasetParameterType` (`parameter/dataset.py`)

**Files:**
- Modify: `cmem_plugin_base/dataintegration/parameter/dataset.py`

**Interfaces:**
- Consumes: `setup_cmem_client` from Task 2. `client.datasets` is a dict-like `DatasetsRepository` keyed by dataset id (bare `Dataset.id`, not `project:id`), each value a `Dataset` with `.id: str`, `.project_id: str`, `.data.type: str`, `.metadata: dict` (has `"label"` key). `client.datasets.get_task(project_id, task_id) -> TaskResponse` with `.label: str | None`.

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `cmem_plugin_base/dataintegration/parameter/dataset.py` with:

```python
"""DI Dataset Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmem_client


class DatasetParameterType(StringParameterType):
    """Dataset parameter type."""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    dataset_type: str | None = None

    def __init__(self, dataset_type: str | None = None):
        """Dataset parameter type."""
        self.dataset_type = dataset_type

    def label(
        self, value: str, depend_on_parameter_values: list[Any], context: PluginContext
    ) -> str | None:
        """Return the label for the given dataset."""
        client = setup_cmem_client(context.user)
        task = client.datasets.get_task(project_id=context.project_id, task_id=value)
        return f"{task.label}"

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match all provided query terms."""
        client = setup_cmem_client(context.user)
        datasets = [
            dataset for dataset in client.datasets.values() if dataset.project_id == context.project_id
        ]

        result = []
        for dataset in datasets:
            identifier = dataset.id
            title = dataset.metadata.get("label", identifier)
            label = f"{title} ({identifier})"
            if self.dataset_type is not None and self.dataset_type != dataset.data.type:
                # Ignore datasets of other types
                continue
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=identifier, label=label))  # noqa: PERF401
            if len(query_terms) == 0:
                # add any dataset to list if no search terms are given
                result.append(Autocompletion(value=identifier, label=label))
        result.sort(key=lambda x: x.label)  # type: ignore[return-value, arg-type]
        return list(set(result))
```

- [ ] **Step 2: Run the existing dataset parameter tests**

```bash
poetry run pytest tests/parameter_types -k dataset -v
```

Expected: tests pass if a live CMEM (`CMEM_BASE_URI`) is configured, or are reported `SKIPPED` (not failed) otherwise, since they're `@needs_cmem`-marked.

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check cmem_plugin_base/dataintegration/parameter/dataset.py
poetry run ruff format --check cmem_plugin_base/dataintegration/parameter/dataset.py
poetry run mypy -p cmem_plugin_base.dataintegration.parameter.dataset
```

- [ ] **Step 4: Commit**

```bash
git add cmem_plugin_base/dataintegration/parameter/dataset.py
git commit -m "refactor: migrate DatasetParameterType to cmem-client"
```

---

### Task 4: Migrate `GraphParameterType` (`parameter/graph.py`)

**Files:**
- Modify: `cmem_plugin_base/dataintegration/parameter/graph.py`

**Interfaces:**
- Consumes: `setup_cmem_client`. `client.graphs` is a dict-like `GraphsRepository` keyed by graph IRI, each value a `Graph` with `.iri: str`, `.label: GraphLabel | None` (`.title: str`), `.assigned_classes: list[str]`, plus **extra fields not on the pydantic model** (`diProjectGraph`, `systemResource`) reachable via `.model_extra` (the `Graph` model uses `extra="allow"`, same `/graphs/list` endpoint cmempy's `get_graphs_list()` hit).

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `cmem_plugin_base/dataintegration/parameter/graph.py` with:

```python
"""Knowledge Graph Parameter Type."""

import re
from typing import Any

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmem_client

IRI_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:.+$")


class GraphParameterType(StringParameterType):
    """Knowledge Graph parameter type."""

    allow_only_autocompleted_values: bool = False

    autocomplete_value_with_labels: bool = True

    classes: set[str] | None = None

    def __init__(
        self,
        show_di_graphs: bool = False,
        show_system_graphs: bool = False,
        show_graphs_without_class: bool = False,
        classes: list[str] | None = None,
        allow_only_autocompleted_values: bool = True,
    ):
        """Knowledge Graph parameter type.

        :param show_di_graphs: show DI project graphs
        :param show_system_graphs: show system graphs such as shape and query catalogs
        :param classes: allowed classes of the shown graphs
            - if None -> defaults to di:Dataset, void:Dataset and shui:QueryCatalog
        :param allow_only_autocompleted_values: allow entering new graph URLs
        """
        self.name = "scheme:string"
        self._validate_graph()
        self.show_di_graphs = show_di_graphs
        self.show_system_graphs = show_system_graphs
        self.show_graphs_without_class = show_graphs_without_class
        self.allow_only_autocompleted_values = allow_only_autocompleted_values
        if classes:
            self.classes = set(classes)
        else:
            self.classes = {
                "https://vocab.eccenca.com/di/Dataset",
                "http://rdfs.org/ns/void#Dataset",
                "https://vocab.eccenca.com/shui/QueryCatalog",
            }

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match ALL provided query terms"""
        client = setup_cmem_client(context.user)
        result = []
        for graph in client.graphs.values():
            iri = graph.iri
            title = graph.label.title if graph.label else iri
            label = f"{title} ({iri})"
            assigned_classes = set(graph.assigned_classes)
            extra = graph.model_extra or {}
            # ignore DI project graphs
            if self.show_di_graphs is False and extra.get("diProjectGraph") is True:
                continue
            # ignore system resource graphs
            if self.show_system_graphs is False and extra.get("systemResource") is True:
                continue
            # show graphs without assigned classes only if explicitly wanted
            if len(assigned_classes) == 0:
                if self.show_graphs_without_class is True:
                    result.append(Autocompletion(value=iri, label=label))
                continue
            # ignore graphs which do not match the requested classes
            if (
                self.classes is not None
                and len(assigned_classes) > 0
                and len(self.classes.intersection(assigned_classes)) == 0
            ):
                continue
            # if no search terms are given: add all remaining graphs to list
            if len(query_terms) == 0:
                result.append(Autocompletion(value=iri, label=label))
                continue
            # show only graphs which match the given terms
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=iri, label=label))
                    continue
        result.sort(key=lambda x: x.label)  # type: ignore[return-value, arg-type]
        return list(set(result))

    def _validate_graph(self) -> None:
        """Verify that graph name is valid aka it has at least a scheme and something after it"""
        is_valid = bool(IRI_PATTERN.match(self.name))
        if not is_valid:
            raise ValueError(f"Could not validate graph IRI '{self.name}'")
```

- [ ] **Step 2: Run the graph parameter tests**

```bash
poetry run pytest tests/parameter_types -k graph -v
```

Expected: pass or skip (see Task 3 Step 2 note).

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check cmem_plugin_base/dataintegration/parameter/graph.py
poetry run ruff format --check cmem_plugin_base/dataintegration/parameter/graph.py
poetry run mypy -p cmem_plugin_base.dataintegration.parameter.graph
```

- [ ] **Step 4: Commit**

```bash
git add cmem_plugin_base/dataintegration/parameter/graph.py
git commit -m "refactor: migrate GraphParameterType to cmem-client"
```

---

### Task 5: Migrate `ResourceParameterType` (`parameter/resource.py`)

**Files:**
- Modify: `cmem_plugin_base/dataintegration/parameter/resource.py`

**Interfaces:**
- Consumes: `setup_cmem_client`. `client.files.get_resources(project_id: str) -> list[ResourceResponse]`, each with `.full_path: str`, `.name: str`.

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `cmem_plugin_base/dataintegration/parameter/resource.py` with:

```python
"""DI Resource Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmem_client


class ResourceParameterType(StringParameterType):
    """Resource parameter type."""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match ALL provided query terms."""
        client = setup_cmem_client(context.user)
        resources = client.files.get_resources(context.project_id)
        result = [
            Autocompletion(
                value=resource.full_path,
                label=resource.name,
            )
            for resource in resources
        ]
        if query_terms:
            result = [_ for _ in result if _.value.find(query_terms[0]) > -1]

        if not result and query_terms:
            result = [
                Autocompletion(value=f"{query_terms[0]}", label=f"{query_terms[0]} (New resource)")
            ]

        return result
```

- [ ] **Step 2: Run the resource parameter tests**

```bash
poetry run pytest tests/parameter_types -k resource -v
```

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check cmem_plugin_base/dataintegration/parameter/resource.py
poetry run ruff format --check cmem_plugin_base/dataintegration/parameter/resource.py
poetry run mypy -p cmem_plugin_base.dataintegration.parameter.resource
```

- [ ] **Step 4: Commit**

```bash
git add cmem_plugin_base/dataintegration/parameter/resource.py
git commit -m "refactor: migrate ResourceParameterType to cmem-client"
```

---

### Task 6: Migrate `typed_entities/file.py` (the hybrid client/ambient-fallback site)

**Files:**
- Modify: `cmem_plugin_base/dataintegration/typed_entities/file.py`

**Interfaces:**
- Consumes: `cmem_client.client.Client`, `client.datasets.get_file_resource(project_id, file_name) -> AbstractContextManager[httpx.Response]` (streaming; defined on `DatasetsRepository`, not `FilesRepository` — call `.read()` inside the `with` block to get full bytes).
- Produces: `File.read_stream(self, project_id: str, client: Client | None = None) -> IO[bytes]` and the same additive `client` parameter threaded through `is_text`, `is_bytes`, `read_text`, `read_bytes`, `text_stream`, `bytes_stream`. All existing single-argument callers keep working unchanged (ambient fallback via `Client.from_env()`, which reads the same `OAUTH_GRANT_TYPE`/`OAUTH_ACCESS_TOKEN`/`CMEM_BASE_URI` env vars `setup_cmem_client` sets in Task 2).

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `cmem_plugin_base/dataintegration/typed_entities/file.py` with:

```python
"""File entities"""

import gzip
import io
import zipfile
from abc import abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import IO

from cmem_client.client import Client

from cmem_plugin_base.dataintegration.entity import Entity, EntityPath
from cmem_plugin_base.dataintegration.typed_entities import instance_uri, path_uri, type_uri
from cmem_plugin_base.dataintegration.typed_entities.typed_entities import (
    TypedEntitySchema,
)


def _is_gzip(stream: io.BufferedReader) -> bool:
    """Check if a stream contains gzip-compressed data."""
    head = stream.read(2)
    stream.seek(0)
    return head == b"\x1f\x8b"


def _prepare_stream_for_processing(
    input_stream: IO[bytes],
) -> tuple[io.TextIOWrapper | IO[bytes], bool]:
    """Prepare a file stream for processing.

    This utility function:
    1. Detects if the stream is gzip compressed
    2. Decompresses if needed
    3. Detects if the content is text or binary
    4. Returns appropriate stream wrapper

    Args:
        input_stream: The input stream to process (should be in binary mode)

    Returns:
        A tuple containing:
        - The processed stream (TextIOWrapper for text, original stream for binary)
        - Boolean indicating if the content is text (True) or binary (False)

    """
    buffered = io.BufferedReader(input_stream)  # type: ignore[type-var]

    decompressed_stream = gzip.GzipFile(fileobj=buffered) if _is_gzip(buffered) else buffered  # type: ignore[arg-type]

    sample = decompressed_stream.read(1024)
    decompressed_stream.seek(0)

    try:
        sample.decode("utf-8")
        is_text = True
        stream_for_processing = io.TextIOWrapper(decompressed_stream, encoding="utf-8")
    except UnicodeDecodeError:
        is_text = False
        stream_for_processing = decompressed_stream  # type: ignore[assignment]

    return stream_for_processing, is_text


class _TextToBytesWrapper:
    """Helper class to wrap a text stream and provide a bytes interface."""

    def __init__(self, text_stream: io.TextIOWrapper) -> None:
        self._text_stream = text_stream

    def read(self, size: int = -1) -> bytes:
        """Read and encode text as bytes."""
        text_content = self._text_stream.read(size)
        return text_content.encode("utf-8") if text_content else b""

    def readline(self, size: int = -1) -> bytes:
        """Read a line and encode as bytes."""
        text_line = self._text_stream.readline(size)
        return text_line.encode("utf-8") if text_line else b""

    def __iter__(self) -> Iterator[bytes]:
        """Iterate over lines as bytes."""
        for line in self._text_stream:
            yield line.encode("utf-8")

    def close(self) -> None:
        """Close the underlying text stream."""
        self._text_stream.close()

    def __enter__(self) -> "_TextToBytesWrapper":  # noqa: PYI034
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class File:
    """A file entity that can be held in a FileEntitySchema.

    :param path: The file path.
    :param file_type: The type of the file (one of: "Local", "Project").
    :param mime: The MIME type of the file, if known.
    :param entry_path: If the file path points to a archive, the entry within the archive.
    """

    def __init__(self, path: str, file_type: str, mime: str | None, entry_path: str | None) -> None:
        self.path = path
        self.file_type = file_type
        self.mime = mime
        self.entry_path = entry_path

    @abstractmethod
    def read_stream(self, project_id: str, client: Client | None = None) -> IO[bytes]:
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.

        Args:
            project_id: The project ID.
            client: An already configured cmem_client.Client. If omitted, a client
                is built from the ambient environment (CMEM_BASE_URI/OAUTH_* vars),
                matching the identity set up by
                cmem_plugin_base.dataintegration.utils.setup_cmem_client.
        """

    def is_text(self, project_id: str, client: Client | None = None) -> bool:
        """Check if the file contains text data.

        Returns True if the file content can be decoded as UTF-8 text, False otherwise.
        This method automatically handles gzip decompression if needed.
        """
        with self.read_stream(project_id, client) as stream:
            _, is_text = _prepare_stream_for_processing(stream)
            return is_text

    def is_bytes(self, project_id: str, client: Client | None = None) -> bool:
        """Check if the file contains binary data.

        Returns True if the file content is binary (cannot be decoded as UTF-8), False otherwise.
        This method automatically handles gzip decompression if needed.
        """
        return not self.is_text(project_id, client)

    def read_text(self, project_id: str, client: Client | None = None) -> str:
        """Read the file content as text.

        Returns the file content as a string. Automatically handles gzip decompression if needed.
        Raises UnicodeDecodeError if the file content is not valid UTF-8 text.
        """
        with self.read_stream(project_id, client) as stream:
            processed_stream, is_text = _prepare_stream_for_processing(stream)
            if not is_text:
                raise UnicodeDecodeError("utf-8", b"", 0, 0, "File content is not valid UTF-8 text")
            return processed_stream.read()  # type: ignore[return-value]

    def read_bytes(self, project_id: str, client: Client | None = None) -> bytes:
        """Read the file content as bytes.

        Returns the file content as bytes. Automatically handles gzip decompression if needed.
        """
        with self.read_stream(project_id, client) as stream:
            processed_stream, is_text = _prepare_stream_for_processing(stream)
            if is_text:
                content = processed_stream.read()  # type: ignore[attr-defined]
                return content.encode("utf-8") if isinstance(content, str) else content
            return processed_stream.read()  # type: ignore[return-value]

    @contextmanager
    def text_stream(self, project_id: str, client: Client | None = None) -> Iterator[io.TextIOWrapper]:
        """Get a text stream for memory-efficient processing.

        Returns a context manager that yields a text stream for reading file content.
        Automatically handles gzip decompression if needed.
        Raises UnicodeDecodeError if the file content is not valid UTF-8 text.

        Example:
            ```python
            with file.text_stream(project_id) as stream:
                for line in stream:
                    process_line(line)
            ```

        """
        with self.read_stream(project_id, client) as raw_stream:
            processed_stream, is_text = _prepare_stream_for_processing(raw_stream)
            if not is_text:
                raise UnicodeDecodeError("utf-8", b"", 0, 0, "File content is not valid UTF-8 text")
            yield processed_stream  # type: ignore[misc]

    @contextmanager
    def bytes_stream(self, project_id: str, client: Client | None = None) -> Iterator[IO[bytes]]:
        """Get a binary stream for memory-efficient processing.

        Returns a context manager that yields a binary stream for reading file content.
        Automatically handles gzip decompression if needed.

        Example:
            ```python
            with file.bytes_stream(project_id) as stream:
                while chunk := stream.read(8192):
                    process_chunk(chunk)
            ```

        """
        with self.read_stream(project_id, client) as raw_stream:
            processed_stream, is_text = _prepare_stream_for_processing(raw_stream)
            if is_text:
                # Convert text stream back to bytes for consistent API
                text_stream = processed_stream  # type: ignore[assignment]
                # Create a bytes stream by encoding the text stream
                yield _TextToBytesWrapper(text_stream)  # type: ignore[arg-type,misc]
            else:
                yield processed_stream  # type: ignore[misc]


class LocalFile(File):
    """A file that's located on the local file system."""

    def __init__(self, path: str, mime: str | None = None, entry_path: str | None = None) -> None:
        super().__init__(path, "Local", mime, entry_path)

    def read_stream(self, project_id: str, client: Client | None = None) -> IO[bytes]:  # noqa: ARG002
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.
        """
        if self.entry_path:
            archive = zipfile.ZipFile(self.path, "r")
            try:
                return archive.open(self.entry_path, "r")
            except KeyError as err:
                archive.close()
                raise FileNotFoundError(
                    f"Entry '{self.entry_path}' not found in archive '{self.path}'."
                ) from err
        else:
            if not Path(self.path).is_file():
                raise FileNotFoundError(f"File '{self.path}' does not exist.")
            return Path(self.path).open("rb")


class ProjectFile(File):
    """A project file"""

    def __init__(self, path: str, mime: str | None = None, entry_path: str | None = None) -> None:
        super().__init__(path, "Project", mime, entry_path)

    def read_stream(self, project_id: str, client: Client | None = None) -> IO[bytes]:
        """Open the referenced file as a stream.

        Returns a file-like object (stream) in binary mode.
        Caller is responsible for closing the stream.
        """
        client = client or Client.from_env()
        with client.datasets.get_file_resource(project_id, self.path) as response:
            if response.status_code != 200:  # noqa: PLR2004
                raise FileNotFoundError(f"Project file '{self.path}' not found.")
            response_bytes = BytesIO(response.read())
        if self.entry_path:
            archive = zipfile.ZipFile(response_bytes, "r")
            try:
                return archive.open(self.entry_path, "r")
            except KeyError as err:
                archive.close()
                raise FileNotFoundError(
                    f"Entry '{self.entry_path}' not found in project file '{self.path}'."
                ) from err
        else:
            return response_bytes


class FileEntitySchema(TypedEntitySchema[File]):
    """Entity schema that holds a collection of files."""

    def __init__(self):
        # The parent class TypedEntitySchema implements a singleton pattern
        if not hasattr(self, "_initialized"):
            super().__init__(
                type_uri=type_uri("File"),
                paths=[
                    EntityPath(path_uri("filePath"), is_single_value=True),
                    EntityPath(path_uri("fileType"), is_single_value=True),
                    EntityPath(path_uri("mimeType"), is_single_value=True),
                    EntityPath(path_uri("entryPath"), is_single_value=True),
                ],
            )

    def to_entity(self, value: File) -> Entity:
        """Create a generic entity from a file"""
        return Entity(
            uri=instance_uri(value.path),
            values=[
                [value.path],
                [value.file_type],
                [value.mime] if value.mime else [],
                [value.entry_path] if value.entry_path else [],
            ],
        )

    def from_entity(self, entity: Entity) -> File:
        """Create a file entity from a generic entity."""
        path = entity.values[0][0]
        file_type = entity.values[1][0]
        mime = entity.values[2][0] if entity.values[2] and entity.values[2][0] else None
        entry_path = entity.values[3][0] if entity.values[3] and entity.values[3][0] else None

        match file_type:
            case "Local":
                return LocalFile(path, mime, entry_path)
            case "Project":
                return ProjectFile(path, mime, entry_path)
            case _:
                raise ValueError(f"File '{path}' has unexpected type '{file_type}'.")
```

- [ ] **Step 2: Run the file-entity tests**

```bash
poetry run pytest tests/typed_entities tests/test_file_stream.py -v
```

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check cmem_plugin_base/dataintegration/typed_entities/file.py
poetry run ruff format --check cmem_plugin_base/dataintegration/typed_entities/file.py
poetry run mypy -p cmem_plugin_base.dataintegration.typed_entities.file
```

- [ ] **Step 4: Commit**

```bash
git add cmem_plugin_base/dataintegration/typed_entities/file.py
git commit -m "refactor: migrate File/ProjectFile to cmem-client with optional client param"
```

---

### Task 7: Migrate `cmem_plugin_base/testing.py`

**Files:**
- Modify: `cmem_plugin_base/testing.py`

**Interfaces:**
- Consumes: `cmem_client.config.Config.from_env()`, `cmem_client.auth_provider.abc.AuthProvider.from_env(config) -> AuthProvider`, `.get_access_token() -> str` (auto-selects the grant type from `OAUTH_GRANT_TYPE`, defaulting to `client_credentials`, and auto-refreshes internally — replaces cmempy's `get_oauth_default_credentials()` + `get_token()`).
- Produces: `TestUserContext.token()` — unchanged public signature/behavior.

- [ ] **Step 1: Edit the imports and `TestUserContext`**

In `cmem_plugin_base/testing.py`, replace:

```python
from cmem.cmempy.api import get_token
from cmem.cmempy.config import get_oauth_default_credentials
```

with:

```python
from cmem_client.auth_provider.abc import AuthProvider
from cmem_client.config import Config
```

Then replace the `TestUserContext` class body:

```python
class TestUserContext(UserContext):
    """Testing user context"""

    __test__ = False
    default_credential: ClassVar[dict] = {}

    def __init__(self):
        if not TestUserContext.default_credential:
            TestUserContext.default_credential = get_oauth_default_credentials()
        self.access_token = get_token(_oauth_credentials=TestUserContext.default_credential)[
            "access_token"
        ]

    def token(self) -> str:
        """Get an access token"""
        return f"{self.access_token}"
```

with:

```python
class TestUserContext(UserContext):
    """Testing user context"""

    __test__ = False
    _auth_provider: ClassVar[AuthProvider | None] = None

    def __init__(self):
        if TestUserContext._auth_provider is None:
            TestUserContext._auth_provider = AuthProvider.from_env(config=Config.from_env())
        self.access_token = TestUserContext._auth_provider.get_access_token()

    def token(self) -> str:
        """Get an access token"""
        return f"{self.access_token}"
```

(`AuthProvider.from_env` caches nothing itself, but the concrete provider it returns — e.g. `ClientCredentialsFlow` — caches and auto-refreshes its token internally, so caching the provider instance once as a `ClassVar` and calling `.get_access_token()` fresh on every `TestUserContext()` instantiation preserves the original "cache credentials, fetch a fresh token per instantiation" behavior, and is safe across long test sessions.)

- [ ] **Step 2: Run the testing-context tests**

```bash
poetry run pytest tests/test_testing.py -v
```

Expected: all pass — `test_testing.py` only exercises `TestSystemContext`, which is untouched by this task.

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check cmem_plugin_base/testing.py
poetry run ruff format --check cmem_plugin_base/testing.py
poetry run mypy -p cmem_plugin_base.testing
```

- [ ] **Step 4: Commit**

```bash
git add cmem_plugin_base/testing.py
git commit -m "refactor: migrate TestUserContext token retrieval to cmem-client"
```

---

### Task 8: Migrate `tests/conftest.py` fixtures

**Files:**
- Modify: `tests/conftest.py`

**Interfaces:**
- Consumes: `cmem_client.client.Client.from_env()`, `client.projects.create_item(Project(name=...))`, `client.projects.delete_item(name)`, `client.datasets.create_item(Dataset(...))`, `client.datasets.get_item(project_id, dataset_id) -> Dataset`, `client.files.import_item(path: Path, key: "project_id:file_path") -> str`.
- Produces: `json_dataset` fixture yields `{"project": str, "id": str}` (the round-trip test only checks the dict serializes/deserializes identically through JSON — it does not depend on cmempy's original response shape). `json_resource` / `pdf_resource` fixtures yield `ResourceFixture(project_name, resource_name)` — unchanged.

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `tests/conftest.py` with:

```python
"""pytest conftest module"""

import tempfile
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem_client.client import Client
from cmem_client.models.dataset import Dataset, DatasetData
from cmem_client.models.project import Project

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"

FIXTURE_DIR = Path(__file__).parent / "fixture"


@pytest.fixture(name="json_dataset", scope="module")
def _json_dataset() -> Generator[dict]:
    """Provide a dataset"""
    client = Client.from_env()
    client.projects.create_item(Project(name=PROJECT_NAME))
    client.datasets.create_item(
        Dataset(
            id=DATASET_NAME,
            project_id=PROJECT_NAME,
            data=DatasetData(type="json", parameters={"file": RESOURCE_NAME}),
        )
    )
    yield {"project": PROJECT_NAME, "id": DATASET_NAME}
    client.projects.delete_item(PROJECT_NAME)


@dataclass
class ResourceFixture:
    """fixture dataclass"""

    project_name: str
    resource_name: str


@pytest.fixture(name="json_resource", scope="module")
def _json_resource() -> Generator[ResourceFixture]:
    """Set up json resource"""
    _project_name = "json_test_project"
    _resource_name = "sample_test.json"
    client = Client.from_env()
    client.projects.create_item(Project(name=_project_name))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        tmp.write("SAMPLE CONTENT")
        tmp_path = Path(tmp.name)
    try:
        client.files.import_item(path=tmp_path, key=f"{_project_name}:{_resource_name}")
    finally:
        tmp_path.unlink()

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    client.projects.delete_item(_project_name)


@pytest.fixture(name="pdf_resource", scope="module")
def _pdf_resource() -> Generator[ResourceFixture]:
    """Set up pdf resource"""
    _project_name = "pdf_test_project"
    _resource_name = "sample.pdf"
    client = Client.from_env()
    client.projects.create_item(Project(name=_project_name))
    client.files.import_item(
        path=FIXTURE_DIR / "sample.pdf", key=f"{_project_name}:{_resource_name}"
    )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    client.projects.delete_item(_project_name)
```

- [ ] **Step 2: Lint and type-check**

```bash
poetry run ruff check tests/conftest.py
poetry run ruff format --check tests/conftest.py
poetry run mypy -p tests.conftest
```

(Task 9 runs the actual fixture-dependent tests, since `conftest.py` has no tests of its own to execute directly.)

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "refactor: migrate test fixtures in conftest.py to cmem-client"
```

---

### Task 9: Update `tests/test_utils_write_to_dataset.py`

**Files:**
- Modify: `tests/test_utils_write_to_dataset.py`

**Interfaces:**
- Consumes: `RESOURCE_NAME` from `tests.conftest` (Task 8), `cmem_client.client.Client.from_env()`, `client.datasets.get_file_resource(project_id, file_name)`, `httpx.HTTPStatusError` (replaces `requests.exceptions.HTTPError` per the Global Constraints note on `write_to_dataset`'s behavior change).

- [ ] **Step 1: Rewrite the file**

Replace the full contents of `tests/test_utils_write_to_dataset.py` with:

```python
"""graph parameter type tests"""

import io
import json

import httpx
import pytest
from cmem_client.client import Client

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from cmem_plugin_base.dataintegration.utils import write_to_dataset
from cmem_plugin_base.testing import TestPluginContext
from tests.conftest import RESOURCE_NAME
from tests.utils import get_autocomplete_values, needs_cmem


@needs_cmem
def test_write_to_json_dataset(json_dataset: dict) -> None:
    """Test write to json dataset"""
    project_name = json_dataset["project"]
    dataset_name = json_dataset["id"]

    parameter = DatasetParameterType(dataset_type="json")
    dataset_id = f"{project_name}:{dataset_name}"
    context = TestPluginContext(project_name)
    assert dataset_name in get_autocomplete_values(parameter, [], context)

    write_to_dataset(dataset_id, io.StringIO(json.dumps(json_dataset)), TestPluginContext().user)

    client = Client.from_env()
    with client.datasets.get_file_resource(project_name, RESOURCE_NAME) as response:
        get_response = json.loads(response.read())
    assert get_response == json_dataset


@needs_cmem
def test_write_to_not_valid_dataset() -> None:
    """Test write to not valid dataset"""
    with pytest.raises(
        httpx.HTTPStatusError,
        match=r"404 Not Found",
    ):
        write_to_dataset(
            "INVALID_PROJECT:INVALID_DATASET",
            io.StringIO("{}"),
            TestPluginContext().user,
        )


@needs_cmem
def test_write_to_invalid_format_dataset_id() -> None:
    """Test write to invalid format dataset id"""
    with pytest.raises(ValueError, match=r"INVALID_DATASET_ID_FORMAT is not a valid task ID."):
        write_to_dataset("INVALID_DATASET_ID_FORMAT", io.StringIO("{}"), TestPluginContext().user)
```

- [ ] **Step 2: Run the test file**

```bash
poetry run pytest tests/test_utils_write_to_dataset.py -v
```

Expected: pass (with a live CMEM configured) or skip.

- [ ] **Step 3: Lint and type-check**

```bash
poetry run ruff check tests/test_utils_write_to_dataset.py
poetry run ruff format --check tests/test_utils_write_to_dataset.py
poetry run mypy -p tests.test_utils_write_to_dataset
```

- [ ] **Step 4: Commit**

```bash
git add tests/test_utils_write_to_dataset.py
git commit -m "test: adapt write_to_dataset tests to cmem-client (httpx errors, RESOURCE_NAME)"
```

---

### Task 10: Full sweep, CHANGELOG, and final verification

**Files:**
- Modify: `CHANGELOG.md`
- Verify (no code changes expected): everything touched in Tasks 1–9.

**Interfaces:**
- Consumes: nothing new — this task only verifies.

- [ ] **Step 1: Confirm no cmempy imports remain**

```bash
grep -rn "cmem\.cmempy" cmem_plugin_base tests
```

Expected: no output. If anything is found, go back and migrate it (it means Tasks 1–9 missed a call site — re-run the discovery grep from the top of this plan's Global Constraints).

- [ ] **Step 2: Full lint/type/dependency sweep**

```bash
poetry run ruff check tests cmem_plugin_base
poetry run ruff format --check tests cmem_plugin_base
poetry run mypy -p tests -p cmem_plugin_base
poetry run deptry .
```

Expected: no errors. `deptry` should no longer complain about `cmem-cmempy`; if it flags `cmem-client` as unused anywhere, double check the import actually landed in the flagged file.

- [ ] **Step 3: Full test suite**

```bash
poetry run pytest -v
```

Expected: all non-`needs_cmem` tests pass; `needs_cmem` tests pass if `CMEM_BASE_URI` (and matching `OAUTH_*` vars) are configured, otherwise report as `SKIPPED`. Zero `FAILED`/`ERROR`.

- [ ] **Step 4: Update CHANGELOG.md**

In `CHANGELOG.md`, under the existing `## Unreleased` section, add a `### Changed` bullet (create the subsection if it doesn't already have one below `### Fixed`, or reuse the existing `### Changed` block at the top):

```markdown
- Replaced the `cmem-cmempy` dependency with `cmem-client`. `setup_cmempy_user_access`/`setup_cmempy_super_user_access` remain available but are deprecated in favor of `setup_cmem_client`/`setup_cmem_client_super_user_access`, which return a ready-to-use `cmem_client.Client`. `File.read_stream` (and the other `File` convenience methods) gained an optional `client` parameter. **Breaking:** `write_to_dataset` now returns `None` (was `requests.Response`) and raises `httpx.HTTPStatusError` (was `requests.exceptions.HTTPError`) on failed uploads (CMEM-XXXX)
```

Replace `CMEM-XXXX` with the actual ticket ID once one is filed, or drop the parenthetical if this work has no tracked ticket.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog entry for cmem-client migration"
```

---

## Self-Review Notes

- **Spec coverage:** all six original `cmem.cmempy` call sites (`utils/__init__.py`, `parameter/dataset.py`, `parameter/graph.py`, `parameter/resource.py`, `typed_entities/file.py`, `testing.py`) plus the two test-only call sites (`tests/conftest.py`, `tests/test_utils_write_to_dataset.py`) each have a dedicated task. The dependency swap and final verification bookend the plan.
- **Breaking changes are explicit, not hidden:** `write_to_dataset`'s return-type/exception-type change is called out in Global Constraints, in Task 2's docstring, in Task 9's test, and in the CHANGELOG task — not something a future reader has to discover by diffing.
- **Type/signature consistency check:** `setup_cmem_client(context: UserContext | None) -> Client` (Task 2) is the one function every other task imports (Tasks 3, 4, 5, 9 via `write_to_dataset`) — confirmed the parameter type (`UserContext | None`) and return type (`Client`) match at every call site. `File.read_stream(self, project_id: str, client: Client | None = None)` (Task 6) matches the signature used by all six convenience methods in the same file.
