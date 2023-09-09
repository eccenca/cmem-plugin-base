"""pytest conftest module"""
import io
from dataclasses import dataclass

import pytest
from cmem.cmempy.workspace.projects.datasets.dataset import (
    make_new_dataset,
    get_dataset,
)
from cmem.cmempy.workspace.projects.project import make_new_project, delete_project
from cmem.cmempy.workspace.projects.resources.resource import create_resource

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"


@pytest.fixture(name="json_dataset", scope="module")
def _json_dataset():
    """setup"""
    make_new_project(PROJECT_NAME)
    make_new_dataset(
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
        dataset_type="json",
        parameters={"file": RESOURCE_NAME},
        autoconfigure=False,
    )
    yield get_dataset(PROJECT_NAME, DATASET_NAME)
    delete_project(PROJECT_NAME)


@pytest.fixture(name="json_resource", scope="module")
def _json_resource():
    """setup json resource"""
    _project_name = "resource_test_project"
    _resource_name = "sample_test.json"
    make_new_project(_project_name)
    create_resource(
        project_name=_project_name,
        resource_name=_resource_name,
        file_resource=io.StringIO("SAMPLE CONTENT"),
        replace=True
    )

    @dataclass
    class FixtureDate:
        """fixture dataclass"""
        project_name = _project_name
        resource_name = _resource_name

    _ = FixtureDate()
    yield _
    delete_project(_project_name)
