"""graph parameter type tests"""
from cmem_plugin_base.dataintegration.parameter.dataset import DatasetParameterType
from ..utils import needs_cmem


@needs_cmem
def test_dataset_parameter_type_completion():
    parameter = DatasetParameterType(dataset_type="json")
    assert "testjson" in [x.value for x in parameter.autocomplete(query_terms=[])]
    assert len(parameter.autocomplete(query_terms=["lkshfkdsjfhsd"])) == 0
