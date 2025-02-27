"""test description"""

import unittest
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.context import ExecutionContext, PluginContext
from cmem_plugin_base.dataintegration.description import Plugin, PluginAction
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.plugins import TransformPlugin, WorkflowPlugin
from cmem_plugin_base.dataintegration.types import (
    BoolParameterType,
    FloatParameterType,
    StringParameterType,
)
from cmem_plugin_base.testing import TestPluginContext


class PluginTest(unittest.TestCase):
    """Plugin Test Class"""

    def test__basic_parameters(self) -> None:
        """Test basic parameters"""
        Plugin.plugins = []  # Remove all previous plugins

        @Plugin(label="My Transform Plugin")
        class MyTransformPlugin(TransformPlugin):
            """My Transform Plugin Class"""

            def __init__(
                self,
                no_default_param: str,
                string_param: str = "value",
                float_param: float = 1.5,
                bool_param: bool = True,
            ) -> None:
                self.no_default_param = no_default_param
                self.string_param = string_param
                self.float_param = float_param
                self.bool_param = bool_param

            def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
                return []

        plugin = Plugin.plugins[0]

        no_default_par = plugin.parameters[0]
        assert no_default_par.param_type is not None
        assert no_default_par.param_type.name == StringParameterType.name
        assert no_default_par.default_value is None

        string_par = plugin.parameters[1]
        assert string_par.param_type is not None
        assert string_par.param_type.name == StringParameterType.name
        assert string_par.default_value == "value"

        float_par = plugin.parameters[2]
        assert float_par.param_type is not None
        assert float_par.param_type.name == FloatParameterType.name
        assert float_par.default_value == 1.5

        bool_par = plugin.parameters[3]
        assert bool_par.param_type is not None
        assert bool_par.param_type.name == BoolParameterType.name
        assert bool_par.default_value is True

    def test__actions(self) -> None:
        """Test plugin actions"""
        Plugin.plugins = []  # Remove all previous plugins

        @Plugin(
            label="My Workflow Plugin",
            actions=[
                PluginAction(
                    name="get_name",
                    label="Get name",
                    description="Returns the supplied name",
                ),
                PluginAction(
                    name="get_project",
                    label="Get project",
                    description="Returns the current project.",
                ),
            ],
        )
        class MyWorkflowPlugin(WorkflowPlugin):
            """Test workflow plugin"""

            def __init__(self, name: str) -> None:
                self.name = name

            def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
                return inputs[0]

            def get_name(self) -> str:
                return self.name

            def get_project(self, context: PluginContext) -> str:
                return context.project_id

        # Get plugin description
        plugin = Plugin.plugins[0]

        # There should be two actions
        assert len(plugin.actions) == 2
        action1 = plugin.actions[0]
        action2 = plugin.actions[1]

        # Check first action
        assert action1.name == "get_name"
        assert action1.label == "Get name"
        assert action1.description == "Returns the supplied name"

        # Call actions on a plugin instance
        plugin_instance = MyWorkflowPlugin("My Name")
        assert action1.execute(plugin_instance, TestPluginContext()) == "My Name"
        assert action2.execute(plugin_instance, TestPluginContext(project_id="movies")) == "movies"


if __name__ == "__main__":
    unittest.main()
