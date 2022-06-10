"""DI Multiline String Parameter Type."""
from typing import Optional

from cmem.cmempy.workspace.search import list_items
from cmem.cmempy.workspace.tasks import get_task
from cmem_plugin_base.dataintegration.types import StringParameterType, Autocompletion
from cmem_plugin_base.dataintegration.utils import (
    setup_cmempy_super_user_access,
    split_task_id
)


class MultilineStringParameterType(StringParameterType):
    """Multiline string parameter type."""

    name = "multiline string"
    """Same type name as MultilineStringParameterType in DataIntegration code base."""
