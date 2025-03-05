"""Code parameter types tests"""

import unittest
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.description import Plugin
from cmem_plugin_base.dataintegration.parameter.code import (
    CodeParameterType,
    JinjaCode,
    JsonCode,
    PythonCode,
    SparqlCode,
    SqlCode,
    TurtleCode,
    XmlCode,
    YamlCode,
)
from cmem_plugin_base.dataintegration.plugins import TransformPlugin
from cmem_plugin_base.testing import TestPluginContext


class CodeParameterTest(unittest.TestCase):
    """Code Parameter Test"""

    def test__detection(self) -> None:
        """Test detection"""
        Plugin.plugins = []

        @Plugin(label="My Transform Plugin")
        class MyTransformPlugin(TransformPlugin):
            """Test My Transform Plugin"""

            def __init__(  # pylint: disable=too-many-arguments  # noqa: PLR0913
                self,
                xml: XmlCode = XmlCode("<xml></xml>"),  # noqa: B008
                json: JsonCode = JsonCode("{}"),  # noqa: B008
                jinja: JinjaCode = JinjaCode(""),  # noqa: B008
                sql: SqlCode = SqlCode(""),  # noqa: B008
                yaml: YamlCode = YamlCode(""),  # noqa: B008
                sparql: SparqlCode = SparqlCode(""),  # noqa: B008
                turtle: TurtleCode = TurtleCode(""),  # noqa: B008
                python: PythonCode = PythonCode(""),  # noqa: B008
            ) -> None:
                self.xml = xml
                self.json = json
                self.jinja = jinja
                self.sql = sql
                self.yaml = yaml
                self.sparql = sparql
                self.turtle = turtle
                self.python = python

            def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
                """Test transform"""
                return []

        MyTransformPlugin()

        plugin = Plugin.plugins[0]
        assert plugin.parameters[0].param_type is not None
        assert plugin.parameters[1].param_type is not None
        assert plugin.parameters[2].param_type is not None
        assert plugin.parameters[3].param_type is not None
        assert plugin.parameters[4].param_type is not None
        assert plugin.parameters[5].param_type is not None
        assert plugin.parameters[6].param_type is not None
        assert plugin.parameters[7].param_type is not None

        assert plugin.parameters[0].param_type.name == "code-xml"
        assert plugin.parameters[1].param_type.name == "code-json"
        assert plugin.parameters[2].param_type.name == "code-jinja2"
        assert plugin.parameters[3].param_type.name == "code-sql"
        assert plugin.parameters[4].param_type.name == "code-yaml"
        assert plugin.parameters[5].param_type.name == "code-sparql"
        assert plugin.parameters[6].param_type.name == "code-turtle"
        assert plugin.parameters[7].param_type.name == "code-python"

    def test_serialization(self) -> None:
        """Test serialization from/to strings"""
        jinja_type = CodeParameterType[JinjaCode]("jinja2")

        # Create a jinja code instance from a string
        jinja_code = jinja_type.from_string("my code", TestPluginContext())
        assert jinja_code.code == "my code"

        # Convert jinja code instance to a string
        code_str = jinja_type.to_string(jinja_code)
        assert code_str == "my code"

        # Make sure __str__ will return the code itself
        assert str(jinja_code) == "my code"


if __name__ == "__main__":
    unittest.main()
