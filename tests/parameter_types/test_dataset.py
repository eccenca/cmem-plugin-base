"""graph parameter type tests"""

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from tests.utils import needs_cmem, TestPluginContext, get_autocomplete_values

PROJECT_NAME = "dateset_test_project"
DATASET_NAME = "sample_test"


@needs_cmem
def test_dataset_parameter_type_completion(setup_json_dataset):
    """test dataset parameter type completion"""
    _ = setup_json_dataset
    parameter = DatasetParameterType(dataset_type="json")
    context = TestPluginContext(PROJECT_NAME)
    assert DATASET_NAME in get_autocomplete_values(parameter, [], context)
    assert len(get_autocomplete_values(parameter, ["lkshfkdsjfhsd"], context)) == 0
