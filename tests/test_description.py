import unittest

from typing import Sequence

from cmem_plugin_base.dataintegration.plugins import TransformPlugin

from cmem_plugin_base.dataintegration.description import Plugin
from cmem_plugin_base.dataintegration.types import (
    StringParameterType,
    FloatParameterType,
)


class PluginTest(unittest.TestCase):
    def test__basic_parameters(self):
        Plugin.plugins = []

        @Plugin(label="My Transform Plugin")
        class MyTransformPlugin(TransformPlugin):
            def __init__(
                self,
                no_default_param: str,
                string_param: str = "value",
                float_param: float = 1.5,
            ) -> None:
                self.no_default_param = no_default_param
                self.string_param = string_param
                self.float_param = float_param

            def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
                return []

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


if __name__ == "__main__":
    unittest.main()
