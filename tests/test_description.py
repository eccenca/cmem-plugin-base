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

    def test__basic_parameters(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
