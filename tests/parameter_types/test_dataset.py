"""graph parameter type tests"""

from cmem_client.client import Client
from cmem_client.models.dataset import Dataset, DatasetData

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from cmem_plugin_base.testing import TestPluginContext
from tests.utils import get_autocomplete_values, needs_cmem


@needs_cmem
def test_dataset_parameter_type_completion(json_dataset: dict) -> None:
    """Test dataset parameter type completion"""
    project_name = json_dataset["project"]
    dataset_name = json_dataset["id"]
    parameter = DatasetParameterType(dataset_type="json")
    context = TestPluginContext(project_name)
    assert dataset_name in get_autocomplete_values(parameter, [], context)
    assert len(get_autocomplete_values(parameter, ["lkshfkdsjfhsd"], context)) == 0
    # positive term match: a term that actually occurs in the dataset's label/id
    assert dataset_name in get_autocomplete_values(parameter, [dataset_name[:6]], context)


@needs_cmem
def test_dataset_parameter_type_completion_filters_by_dataset_type(json_dataset: dict) -> None:
    """Datasets of a different plugin type must not show up when dataset_type is set"""
    project_name = json_dataset["project"]
    other_dataset_id = "other_type_dataset"
    client = Client.from_env()
    client.datasets.create_item(
        Dataset(
            id=other_dataset_id,
            project_id=project_name,
            data=DatasetData(type="csv", parameters={"file": "other_type_dataset.csv"}),
        )
    )
    try:
        # confirm the dataset actually exists (avoids a false-positive from search-index lag)
        assert client.datasets.get_item(project_name, other_dataset_id).data.type == "csv"

        parameter = DatasetParameterType(dataset_type="json")
        context = TestPluginContext(project_name)
        assert other_dataset_id not in get_autocomplete_values(parameter, [], context)

        # sanity check: an unfiltered parameter DOES see it, proving the exclusion above is
        # actually due to the dataset_type filter, not search-index lag
        unfiltered = DatasetParameterType()
        assert other_dataset_id in get_autocomplete_values(unfiltered, [], context)
    finally:
        client.datasets.delete_item(f"{project_name}:{other_dataset_id}", skip_if_missing=True)


@needs_cmem
def test_dataset_parameter_type_label(json_dataset: dict) -> None:
    """Test dataset parameter type label lookup"""
    project_name = json_dataset["project"]
    dataset_name = json_dataset["id"]
    parameter = DatasetParameterType(dataset_type="json")
    context = TestPluginContext(project_name)
    label = parameter.label(dataset_name, [], context)
    assert isinstance(label, str)
    assert label != ""
