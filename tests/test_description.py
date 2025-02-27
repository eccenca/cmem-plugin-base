"""test description"""

import unittest
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.context import ExecutionContext
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
        Plugin.plugins = [] # Remove all previous plugins

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
        Plugin.plugins = [] # Remove all previous plugins

        @Plugin(
            label="My Workflow Plugin",
            actions=[
                PluginAction(
                    name="get_name",
                    label="Get name",
                    description="Returns the supplied name"
                )
            ]
        )
        class MyWorkflowPlugin(WorkflowPlugin):
            """Test workflow plugin"""

            def __init__(self, name: str) -> None:
                self.name = name

            def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
                return inputs[0]

            def get_name(self) -> str:
                return self.name

        # Get plugin description
        plugin = Plugin.plugins[0]

        # Check action
        assert len(plugin.actions) == 1
        action = plugin.actions[0]
        assert action.name == "get_name"
        assert action.label == "Get name"
        assert action.description == "Returns the supplied name"

        # Call action on a plugin instance
        plugin_instance = MyWorkflowPlugin("My Name")
        action.execute(plugin_instance, TestPluginContext())


if __name__ == "__main__":
    unittest.main()
