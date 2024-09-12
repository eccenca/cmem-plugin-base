"""graph parameter type tests"""

from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from tests.utils import TestPluginContext, get_autocomplete_values, needs_cmem


@needs_cmem
def test_dataset_parameter_type_completion(json_dataset):
    """Test dataset parameter type completion"""
    project_name = json_dataset["project"]
    dataset_name = json_dataset["id"]
    parameter = DatasetParameterType(dataset_type="json")
    context = TestPluginContext(project_name)
    assert dataset_name in get_autocomplete_values(parameter, [], context)
    assert len(get_autocomplete_values(parameter, ["lkshfkdsjfhsd"], context)) == 0
