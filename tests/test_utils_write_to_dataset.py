"""graph parameter type tests"""
import io
import json

import pytest
import requests.exceptions
from cmem.cmempy.workspace.projects.datasets.dataset import (
    make_new_dataset,
    get_dataset,
)
from cmem.cmempy.workspace.projects.project import make_new_project, delete_project
from cmem.cmempy.workspace.projects.resources.resource import get_resource_response

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from cmem_plugin_base.dataintegration.utils import write_to_dataset
from .utils import needs_cmem

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"


@pytest.fixture(scope="module")
def setup(request):
    make_new_project(PROJECT_NAME)
    make_new_dataset(
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
        dataset_type="json",
        parameters={"file": RESOURCE_NAME},
        autoconfigure=False,
    )

    def teardown():
        delete_project(PROJECT_NAME)

    request.addfinalizer(teardown)

    return get_dataset(PROJECT_NAME, DATASET_NAME)


@needs_cmem
def test_write_to_json_dataset(setup):
    sample_dataset = setup
    parameter = DatasetParameterType(dataset_type="json")
    dataset_id = f"{PROJECT_NAME}:{DATASET_NAME}"
    assert dataset_id in [x.value for x in parameter.autocomplete(query_terms=[])]

    write_to_dataset(dataset_id, io.StringIO(json.dumps(sample_dataset)))

    with get_resource_response(PROJECT_NAME, RESOURCE_NAME) as response:
        assert sample_dataset == response.json()


@needs_cmem
def test_write_to_not_valid_dataset():
    with pytest.raises(
        requests.exceptions.HTTPError,
        match=r"404 Client Error: Not Found for url.*tasks/INVALID_DATASET.*",
    ):
        write_to_dataset(f"f{PROJECT_NAME}:INVALID_DATASET", io.StringIO("{}"))


def test_write_to_invalid_format_dataset_id():
    with pytest.raises(
        ValueError, match=r"INVALID_DATASET_ID_FORMAT is not a valid task ID."
    ):
        write_to_dataset("INVALID_DATASET_ID_FORMAT", io.StringIO("{}"))
