"""DI Code Parameter Type."""
import typing
from typing import TypeVar, Generic

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import ParameterTypes, ParameterType


class Code:
    """Base class of all code types.
    Don't use directly, instead use one of the subclasses."""

    code: str
    """The code string"""

    def __str__(self):
        return self.code


class JinjaCode(Code):
    """Jinja 2 code"""

    def __init__(self, code: str):
        self.code = code


class JsonCode(Code):
    """JSON code"""

    def __init__(self, code: str):
        self.code = code


class SparqlCode(Code):
    """SPARQL code"""

    def __init__(self, code: str):
        self.code = code


class SqlCode(Code):
    """SQL code"""

    def __init__(self, code: str):
        self.code = code


class XmlCode(Code):
    """XML code"""

    def __init__(self, code: str):
        self.code = code


class YamlCode(Code):
    """YAML code"""

    def __init__(self, code: str):
        self.code = code


class TurtleCode(Code):
    """RDF Turtle code"""

    def __init__(self, code: str):
        self.code = code


class PythonCode(Code):
    """Python code"""

    def __init__(self, code: str):
        self.code = code


LANG = TypeVar("LANG", bound=Code)


class CodeParameterType(Generic[LANG], ParameterType[LANG]):
    """Code parameter type."""

    def __init__(self, code_mode: str):
        """Code parameter type."""
        self.name = "code-" + code_mode

    # flake8: noqa
    # pylint: disable=no-member
    def get_type(self):
        """Retrieves the concrete code type."""
        return typing.get_args(self.__orig_class__)[0]

    def from_string(self, value: str, context: PluginContext) -> LANG:
        """Parses strings into code instances."""
        code: LANG = self.get_type()(value)
        return code

    def to_string(self, value: LANG) -> str:
        """Converts code values into their string representation."""
        return value.code


ParameterTypes.register_type(CodeParameterType[JinjaCode]("jinja2"))
ParameterTypes.register_type(CodeParameterType[JsonCode]("json"))
ParameterTypes.register_type(CodeParameterType[SparqlCode]("sparql"))
ParameterTypes.register_type(CodeParameterType[SqlCode]("sql"))
ParameterTypes.register_type(CodeParameterType[XmlCode]("xml"))
ParameterTypes.register_type(CodeParameterType[YamlCode]("yaml"))
ParameterTypes.register_type(CodeParameterType[TurtleCode]("turtle"))
ParameterTypes.register_type(CodeParameterType[PythonCode]("python"))
