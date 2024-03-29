"""Password parameter type tests"""
import unittest
from typing import Sequence

from cmem_plugin_base.dataintegration.description import Plugin
from cmem_plugin_base.dataintegration.parameter.password import (
    Password,
    PasswordParameterType,
)
from cmem_plugin_base.dataintegration.plugins import TransformPlugin


class PasswordParameterTest(unittest.TestCase):
    """Password Parameter Test"""

    def test__detection(self):
        """test detection"""
        Plugin.plugins = []

        @Plugin(label="My Transform Plugin")
        class MyTransformPlugin(TransformPlugin):
            """Test My Transform Plugin"""

            def __init__(self, password: Password) -> None:
                self.password = password

            def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
                """test transform"""
                return []

        Plugin.plugins.append(MyTransformPlugin)

        plugin = Plugin.plugins[0]
        password_param = plugin.parameters[0]
        self.assertEqual(password_param.param_type.name, PasswordParameterType.name)


if __name__ == "__main__":
    unittest.main()
