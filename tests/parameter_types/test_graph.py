"""graph parameter type tests"""

from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType

from ..utils import TestPluginContext, needs_cmem


@needs_cmem
def test_graph_parameter_type_completion():
    """Test graph parameter type completion"""
    parameter = GraphParameterType(show_system_graphs=True)
    context = TestPluginContext()
    assert "https://ns.eccenca.com/data/queries/" in [
        x.value
        for x in parameter.autocomplete(
            query_terms=["Query", "Catalog"],
            depend_on_parameter_values=[],
            context=context,
        )
    ]
    assert (
        len(
            parameter.autocomplete(
                query_terms=["not there asödlkasöld"],
                depend_on_parameter_values=[],
                context=context,
            )
        )
        == 0
    )
