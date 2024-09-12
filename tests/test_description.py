"""test description"""

import unittest
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.description import Plugin
from cmem_plugin_base.dataintegration.plugins import TransformPlugin
from cmem_plugin_base.dataintegration.types import (
    BoolParameterType,
    FloatParameterType,
    StringParameterType,
)


class PluginTest(unittest.TestCase):
    """Plugin Test Class"""

    def test__basic_parameters(self):
        """Test basic parameters"""
        Plugin.plugins = []

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

        _ = MyTransformPlugin
        plugin = Plugin.plugins[0]

        no_default_par = plugin.parameters[0]
        self.assertEqual(no_default_par.param_type.name, StringParameterType.name)
        self.assertIsNone(no_default_par.default_value)

        string_par = plugin.parameters[1]
        self.assertEqual(string_par.param_type.name, StringParameterType.name)
        self.assertEqual(string_par.default_value, "value")

        float_par = plugin.parameters[2]
        self.assertEqual(float_par.param_type.name, FloatParameterType.name)
        self.assertEqual(float_par.default_value, 1.5)

        bool_par = plugin.parameters[3]
        self.assertEqual(bool_par.param_type.name, BoolParameterType.name)
        self.assertEqual(bool_par.default_value, True)


if __name__ == "__main__":
    unittest.main()
