"""pytest conftest module"""
import pytest
from cmem.cmempy.workspace.projects.datasets.dataset import (
    make_new_dataset,
    get_dataset,
)
from cmem.cmempy.workspace.projects.project import make_new_project, delete_project


PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"


@pytest.fixture(name="setup_json_dataset", scope="module")
def _setup_json_dataset(request):
    """setup"""
    make_new_project(PROJECT_NAME)
    make_new_dataset(
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
        dataset_type="json",
        parameters={"file": RESOURCE_NAME},
        autoconfigure=False,
    )

    request.addfinalizer(lambda: delete_project(PROJECT_NAME))

    return get_dataset(PROJECT_NAME, DATASET_NAME)
