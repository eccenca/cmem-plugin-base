"""Testing utilities."""

import os

import pytest

# check for cmem environment and skip if not present
from cmem.cmempy.api import get_token

from cmem_plugin_base.dataintegration.context import PluginContext, UserContext
from cmem_plugin_base.dataintegration.types import ParameterType

needs_cmem = pytest.mark.skipif(
    "CMEM_BASE_URI" not in os.environ, reason="Needs CMEM configuration"
)


class TestUserContext(UserContext):
    """dummy user context that can be used in tests"""

    __test__ = False

    def __init__(self):
        # get access token from default service account
        access_token: str = get_token()["access_token"]
        self.token = lambda: access_token


class TestPluginContext(PluginContext):
    """dummy plugin context that can be used in tests"""

    __test__ = False

    def __init__(
        self,
        project_id: str = "dummyProject",
        user: UserContext | None = None,
    ):
        self.project_id = project_id
        if user is None:
            self.user = TestUserContext()
        else:
            self.user = user


def get_autocomplete_values(parameter: ParameterType, query_terms: list[str],
                            context: PluginContext) -> list[str]:
    """Get autocomplete values"""
    return [
        x.value
        for x in parameter.autocomplete(
            query_terms=query_terms, depend_on_parameter_values=[], context=context
        )
    ]
