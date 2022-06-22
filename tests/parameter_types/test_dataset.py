"""graph parameter type tests"""
import pytest
from cmem.cmempy.workspace.projects.datasets.dataset import (
    make_new_dataset,
    get_dataset,
)
from cmem.cmempy.workspace.projects.project import make_new_project, delete_project

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from ..utils import needs_cmem, TestPluginContext

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "testjson"
RESOURCE_NAME = "test.json"


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
def test_dataset_parameter_type_completion(setup):
    parameter = DatasetParameterType(dataset_type="json")
    dataset_id = f"{PROJECT_NAME}:{DATASET_NAME}"
    context = TestPluginContext(PROJECT_NAME)
    assert dataset_id in [x.value for x in parameter.autocomplete(query_terms=[],
                                                                  context=context)]
    assert len(parameter.autocomplete(query_terms=["lkshfkdsjfhsd"],
                                      context=context)) == 0
