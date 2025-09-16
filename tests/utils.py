"""Testing utilities."""

import os

import pytest

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import ParameterType

needs_cmem = pytest.mark.skipif(
    # check for cmem environment and skip if not present
    "CMEM_BASE_URI" not in os.environ,
    reason="Needs CMEM configuration",
)


def get_autocomplete_values(
    parameter: ParameterType, query_terms: list[str], context: PluginContext
) -> list[str]:
    """Get autocomplete values"""
    return [
        x.value
        for x in parameter.autocomplete(
            query_terms=query_terms, depend_on_parameter_values=[], context=context
        )
    ]
