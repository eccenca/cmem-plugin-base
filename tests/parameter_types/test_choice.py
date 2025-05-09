"""Choice parameter type tests"""

import collections

from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.testing import TestPluginContext

CHOICE_LIST = collections.OrderedDict({"ONE": "First Option", "TWO": "Second Option"})


def test_dataset_parameter_type_completion() -> None:
    """Test dataset parameter type completion"""
    parameter = ChoiceParameterType(choice_list=CHOICE_LIST)
    context = TestPluginContext()
    assert "ONE" in {
        x.value
        for x in parameter.autocomplete(
            query_terms=["First"], depend_on_parameter_values=[], context=context
        )
    }
    assert "TWO" not in {
        x.value
        for x in parameter.autocomplete(
            query_terms=["First"], depend_on_parameter_values=[], context=context
        )
    }
    assert len(
        parameter.autocomplete(query_terms=[], depend_on_parameter_values=[], context=context)
    ) == len(CHOICE_LIST)
    assert (
        len(
            parameter.autocomplete(
                query_terms=["lkshfkdsjfhsd"],
                depend_on_parameter_values=[],
                context=context,
            )
        )
        == 0
    )
