"""resource parameter type tests"""

from cmem_plugin_base.dataintegration.parameter.resource import ResourceParameterType
from cmem_plugin_base.testing import TestPluginContext
from tests.conftest import JSONResourceFixtureDate
from tests.utils import get_autocomplete_values, needs_cmem


@needs_cmem
def test_resource_parameter_type_completion(json_resource: JSONResourceFixtureDate) -> None:
    """Test resource parameter type completion"""
    project_name = json_resource.project_name
    resource_name = json_resource.resource_name
    parameter = ResourceParameterType()
    context = TestPluginContext(project_name)
    assert resource_name in get_autocomplete_values(parameter, [], context)
    new_resource_name = "lkshfkdsjfhsd"
    assert len(get_autocomplete_values(parameter, [new_resource_name], context)) == 1
    assert new_resource_name in get_autocomplete_values(parameter, [new_resource_name], context)
