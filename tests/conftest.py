"""pytest conftest module"""

import io
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem.cmempy.workspace.projects.datasets.dataset import (
    get_dataset,
    make_new_dataset,
)
from cmem.cmempy.workspace.projects.project import delete_project, make_new_project
from cmem.cmempy.workspace.projects.resources.resource import create_resource

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"

FIXTURE_DIR = Path(__file__).parent / "fixture"


@pytest.fixture(name="json_dataset", scope="module")
def _json_dataset() -> Generator[dict, None, None]:
    """Provide a dataset"""
    make_new_project(PROJECT_NAME)
    make_new_dataset(
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
        dataset_type="json",
        parameters={"file": RESOURCE_NAME},
        autoconfigure=False,
    )
    dataset = get_dataset(PROJECT_NAME, DATASET_NAME)
    yield dataset
    delete_project(PROJECT_NAME)


@dataclass
class ResourceFixture:
    """fixture dataclass"""

    project_name: str
    resource_name: str


@pytest.fixture(name="json_resource", scope="module")
def _json_resource() -> Generator[ResourceFixture, None, None]:
    """Set up json resource"""
    _project_name = "json_test_project"
    _resource_name = "sample_test.json"
    make_new_project(_project_name)
    create_resource(
        project_name=_project_name,
        resource_name=_resource_name,
        file_resource=io.StringIO("SAMPLE CONTENT"),
        replace=True,
    )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    delete_project(_project_name)


@pytest.fixture(name="pdf_resource", scope="module")
def _pdf_resource() -> Generator[ResourceFixture, None, None]:
    """Set up pdf resource"""
    _project_name = "pdf_test_project"
    _resource_name = "sample.pdf"
    make_new_project(_project_name)
    with Path(FIXTURE_DIR / "sample.pdf").open("rb") as pdf:
        create_resource(
            project_name=_project_name,
            resource_name=_resource_name,
            file_resource=pdf,
            replace=True,
        )

    _ = ResourceFixture(project_name=_project_name, resource_name=_resource_name)
    yield _
    delete_project(_project_name)
