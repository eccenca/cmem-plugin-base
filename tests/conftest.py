"""pytest conftest module"""

import tempfile
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem_client.models.dataset import Dataset, DatasetData
from cmem_client.models.project import Project
from cmem_client.repositories.protocols.import_item import ImportConflictPolicy

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.testing import TestPluginContext

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"

FIXTURE_DIR = Path(__file__).parent / "fixture"


@pytest.fixture(name="json_dataset", scope="module")
def _json_dataset() -> Generator[dict]:
    """Provide a dataset"""
    client = get_client(TestPluginContext())
    client.projects.create_item(Project(name=PROJECT_NAME))
    dataset = client.datasets.create_item(
        Dataset(
            project_id=PROJECT_NAME,
            id=DATASET_NAME,
            data=DatasetData(type="json", parameters={"file": RESOURCE_NAME}),
        )
    )
    yield {"project": dataset.project_id, "id": dataset.id}
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
    client = get_client(TestPluginContext())
    client.projects.create_item(Project(name=_project_name))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=True) as temp:
        temp.write("SAMPLE CONTENT")
        temp.flush()
        client.files.import_item(
            path=Path(temp.name),
            key=f"{_project_name}:{_resource_name}",
            on_conflict=ImportConflictPolicy.REPLACE,
        )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    client.projects.delete_item(_project_name)


@pytest.fixture(name="pdf_resource", scope="module")
def _pdf_resource() -> Generator[ResourceFixture]:
    """Set up pdf resource"""
    _project_name = "pdf_test_project"
    _resource_name = "sample.pdf"
    client = get_client(TestPluginContext())
    client.projects.create_item(Project(name=_project_name))
    client.files.import_item(
        path=FIXTURE_DIR / "sample.pdf",
        key=f"{_project_name}:{_resource_name}",
        on_conflict=ImportConflictPolicy.REPLACE,
    )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    client.projects.delete_item(_project_name)
