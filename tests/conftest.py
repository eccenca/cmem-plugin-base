"""pytest conftest module"""

import tempfile
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem_client.client import Client
from cmem_client.models.dataset import Dataset, DatasetData
from cmem_client.models.project import Project

PROJECT_NAME = "cmem_plugin_base_dataset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"

FIXTURE_DIR = Path(__file__).parent / "fixture"


@pytest.fixture(name="json_dataset", scope="module")
def _json_dataset() -> Generator[dict]:
    """Provide a dataset"""
    client = Client.from_env()
    client.projects.delete_item(PROJECT_NAME, skip_if_missing=True)
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
    _project_name = "cmem_plugin_base_json_test_project"
    _resource_name = "sample_test.json"
    client = Client.from_env()
    client.projects.delete_item(_project_name, skip_if_missing=True)
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
    _project_name = "cmem_plugin_base_pdf_test_project"
    _resource_name = "sample.pdf"
    client = Client.from_env()
    client.projects.delete_item(_project_name, skip_if_missing=True)
    client.projects.create_item(Project(name=_project_name))
    client.files.import_item(
        path=FIXTURE_DIR / "sample.pdf", key=f"{_project_name}:{_resource_name}"
    )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    client.projects.delete_item(_project_name)
