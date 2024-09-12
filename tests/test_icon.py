"""tests for icon class."""

from collections.abc import Sequence

import pytest

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin


@Plugin(
    label="My Workflow Plugin with custom icon",
    icon=Icon(file_name="icons/test.svg", package=__package__),
)
class MyWorkflowPlugin(WorkflowPlugin):
    """My Workflow Plugin Class"""

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> None:
        return None


def test_for_errors() -> None:
    """Test Icon inits with errors."""
    with pytest.raises(FileNotFoundError):
        Icon(file_name="no.file", package=__package__)
    with pytest.raises(ValueError):
        Icon(file_name="icons/test.txt", package=__package__)
    with pytest.raises(ValueError):
        Icon(file_name="icons/test.nomime", package=__package__)


def test_svg() -> None:
    """Test SVG icon"""
    icon = Icon(file_name="icons/test.svg", package=__package__)
    assert icon.mime_type == "image/svg+xml"
    assert len(str(icon)) == 906


def test_png() -> None:
    """Test PNG icon"""
    icon = Icon(file_name="icons/test.png", package=__package__)
    assert icon.mime_type == "image/png"
    assert len(str(icon)) == 63818


def test_plugin_init() -> None:
    """Test initialization of a workflow plugin with custom icon."""
    _ = MyWorkflowPlugin()
