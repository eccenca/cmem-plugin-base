"""Code parameter types tests"""
import unittest
from typing import Sequence
from tests.utils import TestPluginContext
from cmem_plugin_base.dataintegration.description import Plugin
from cmem_plugin_base.dataintegration.parameter.code import (XmlCode,
                                                             CodeParameterType,
                                                             JsonCode,
                                                             JinjaCode, YamlCode,
                                                             SqlCode, SparqlCode)
from cmem_plugin_base.dataintegration.plugins import TransformPlugin


class CodeParameterTest(unittest.TestCase):
    """Code Parameter Test"""

    def test__detection(self):
        """test detection"""
        Plugin.plugins = []

        @Plugin(label="My Transform Plugin")
        class MyTransformPlugin(TransformPlugin):
            """Test My Transform Plugin"""

            def __init__(self,
                         xml: XmlCode = XmlCode("<xml></xml>"),
                         json: JsonCode = JsonCode("{}"),
                         jinja: JinjaCode = JinjaCode(""),
                         sql: SqlCode = SqlCode(""),
                         yaml: YamlCode = YamlCode(""),
                         sparql: SparqlCode = SparqlCode("")) -> None:
                self.xml = xml
                self.json = json
                self.jinja = jinja
                self.sql = sql
                self.yaml = yaml
                self.sparql = sparql

            def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
                """test transform"""
                return []

        MyTransformPlugin()

        plugin = Plugin.plugins[0]
        self.assertEqual(plugin.parameters[0].param_type.name, "code-xml")
        self.assertEqual(plugin.parameters[1].param_type.name, "code-json")
        self.assertEqual(plugin.parameters[2].param_type.name, "code-jinja2")
        self.assertEqual(plugin.parameters[3].param_type.name, "code-sql")
        self.assertEqual(plugin.parameters[4].param_type.name, "code-yaml")
        self.assertEqual(plugin.parameters[5].param_type.name, "code-sparql")

    def test_serialization(self):
        """test serialization from/to strings"""
        jinja_type = CodeParameterType[JinjaCode]("jinja2")

        # Create a jinja code instance from a string
        jinja_code = jinja_type.from_string("my code", TestPluginContext(user=None))
        self.assertEqual(jinja_code.code, "my code")

        # Convert jinja code instance to a string
        code_str = jinja_type.to_string(jinja_code)
        self.assertEqual(code_str, "my code")

        # Make sure __str__ will return the code itself
        self.assertEqual(str(jinja_code), "my code")


if __name__ == "__main__":
    unittest.main()
