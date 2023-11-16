"""graph parameter type tests"""
import io
import json

import pytest
import requests.exceptions
from cmem.cmempy.workspace.projects.datasets.dataset import get_resource

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from cmem_plugin_base.dataintegration.utils import write_to_dataset
from tests.utils import needs_cmem, TestPluginContext, get_autocomplete_values


@needs_cmem
def test_write_to_json_dataset(json_dataset):
    """test write to json dataset"""
    project_name = json_dataset['project']
    dataset_name = json_dataset['id']

    parameter = DatasetParameterType(dataset_type="json")
    dataset_id = f"{project_name}:{dataset_name}"
    context = TestPluginContext(project_name)
    assert dataset_name in get_autocomplete_values(parameter, [], context)

    write_to_dataset(
        dataset_id, io.StringIO(json.dumps(json_dataset)), TestPluginContext().user
    )

    get_response = get_resource(project_id=project_name, dataset_id=dataset_name)
    get_response = json.loads(get_response)
    assert get_response == json_dataset


@needs_cmem
def test_write_to_not_valid_dataset():
    """test write to not valid dataset"""
    with pytest.raises(
        requests.exceptions.HTTPError,
        match=r"404 Client Error: Not Found for url.*datasets/INVALID_DATASET/file.*",
    ):
        write_to_dataset(
            "INVALID_PROJECT:INVALID_DATASET",
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
