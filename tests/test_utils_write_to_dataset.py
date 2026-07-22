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
