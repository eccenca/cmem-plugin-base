"""graph parameter type tests"""
import io
import json

import pytest
import requests.exceptions
from cmem.cmempy.workspace.projects.resources.resource import get_resource_response

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from cmem_plugin_base.dataintegration.utils import write_to_dataset
from tests.utils import needs_cmem, TestPluginContext, get_autocomplete_values

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"
RESOURCE_NAME = "sample_test.json"


@needs_cmem
def test_write_to_json_dataset(setup_json_dataset):
    """test write to json dataset"""
    sample_dataset = setup_json_dataset
    parameter = DatasetParameterType(dataset_type="json")
    dataset_id = f"{PROJECT_NAME}:{DATASET_NAME}"
    context = TestPluginContext(PROJECT_NAME)
    assert DATASET_NAME in get_autocomplete_values(parameter, [], context)

    write_to_dataset(
        dataset_id, io.StringIO(json.dumps(sample_dataset)), TestPluginContext().user
    )

    with get_resource_response(PROJECT_NAME, RESOURCE_NAME) as response:
        assert sample_dataset == response.json()


@needs_cmem
def test_write_to_not_valid_dataset():
    """test write to not valid dataset"""
    with pytest.raises(
        requests.exceptions.HTTPError,
        match=r"404 Client Error: Not Found for url.*tasks/INVALID_DATASET.*",
    ):
        write_to_dataset(
            f"f{PROJECT_NAME}:INVALID_DATASET",
            io.StringIO("{}"),
            TestPluginContext().user,
        )


@needs_cmem
def test_write_to_invalid_format_dataset_id():
    """test write to invalid format dataset id"""
    with pytest.raises(
        ValueError, match=r"INVALID_DATASET_ID_FORMAT is not a valid task ID."
    ):
        write_to_dataset(
            "INVALID_DATASET_ID_FORMAT", io.StringIO("{}"), TestPluginContext().user
        )
