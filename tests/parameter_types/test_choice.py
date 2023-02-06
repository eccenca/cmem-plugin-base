"""Choice parameter type tests"""
import collections

from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from tests.utils import TestPluginContext

CHOICE_LIST = collections.OrderedDict({
    "ONE": "First Option",
    "TWO": "Second Option"
})


def test_dataset_parameter_type_completion():
    parameter = ChoiceParameterType(choice_list=CHOICE_LIST)
    context = TestPluginContext()
    assert 'ONE' in {x.value for x in parameter.autocomplete(query_terms=['First'],
                                                             depend_on_parameter_values=[],
                                                             context=context)}
    assert 'TWO' not in {x.value for x in parameter.autocomplete(query_terms=['First'],
                                                                 depend_on_parameter_values=[],
                                                                 context=context)}
    assert len(parameter.autocomplete(query_terms=[],
                                      context=context)) == len(CHOICE_LIST)
    assert len(parameter.autocomplete(query_terms=["lkshfkdsjfhsd"],
                                      context=context)) == 0
