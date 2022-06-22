"""Testing utilities."""
import os
from typing import Optional

import pytest

# check for cmem environment and skip if not present
from cmem_plugin_base.dataintegration.context import PluginContext, UserContext

needs_cmem = pytest.mark.skipif(
    "CMEM_BASE_URI" not in os.environ, reason="Needs CMEM configuration"
)


class TestPluginContext(PluginContext):
    """dummy plugin context that can be used in tests"""

    def __init__(self, project_id: str = "dummyProject",
                 user: Optional[UserContext] = None):
        self.project_id = project_id
        self.user = user

