"""test types"""

import unittest
from enum import Enum

from cmem_plugin_base.dataintegration.types import (
    Autocompletion,
    EnumParameterType,
    ParameterTypes,
)
from tests.utils import TestPluginContext

# dummy plugin context to be used in tests
context = TestPluginContext()


class TypesTest(unittest.TestCase):
    """Test Types"""

    class MissingType:
        """Test Missing Type"""

    def test_missing_type(self) -> None:
        """Test missing type"""
        self.assertRaisesRegex(
            ValueError,
            "unsupported type",
            lambda: ParameterTypes.get_type(TypesTest.MissingType),
        )


class BasicTypesTest(unittest.TestCase):
    """Test Basic Types"""

    def test_detection(self) -> None:
        """Test detection"""
        assert ParameterTypes.get_type(str).name == "string"
        assert ParameterTypes.get_type(int).name == "Long"
        assert ParameterTypes.get_type(float).name == "double"
        assert ParameterTypes.get_type(bool).name == "boolean"

    def test_conversion(self) -> None:
        """Test conversion"""
        int_type = ParameterTypes.get_type(int)
        float_type = ParameterTypes.get_type(float)
        bool_type = ParameterTypes.get_type(bool)
        assert int_type.from_string(int_type.to_string(3), context) == 3
        assert float_type.from_string(int_type.to_string(1.2), context) == 1.2
        assert bool_type.from_string(int_type.to_string(True), context) is True
        assert bool_type.from_string(int_type.to_string(False), context) is False


class EnumTest(unittest.TestCase):
    """Test Enum Parameter"""

    class Color(Enum):
        """Test Enum based class Color"""

        RED = 1
        GREEN = 2
        BLUE = 3

    def test_detection(self) -> None:
        """Test detection"""
        assert ParameterTypes.get_type(EnumTest.Color).name == "enumeration"

    def test_conversion(self) -> None:
        """Test conversion"""
        enum = EnumParameterType(EnumTest.Color)
        assert enum.to_string(enum.from_string("RED", context)) == "RED"
        assert enum.to_string(enum.from_string("GREEN", context)) == "GREEN"

    def test_invalid_values(self) -> None:
        """Test invalid values"""
        enum = EnumParameterType(EnumTest.Color)
        self.assertRaisesRegex(
            ValueError,
            "Empty value is not allowed",
            lambda: enum.from_string("", context),
        )
        self.assertRaisesRegex(
            ValueError, "not a valid value", lambda: enum.from_string("CYAN", context)
        )

    def test_autocomplete(self) -> None:
        """Test autocomplete"""
        enum = EnumParameterType(EnumTest.Color)
        self.assertListEqual(
            list(enum.autocomplete(["red"], [], context)),
            [Autocompletion("RED", "RED")],
        )
        self.assertListEqual(
            list(enum.autocomplete(["een"], [], context)),
            [Autocompletion("GREEN", "GREEN")],
        )
        self.assertListEqual(
            list(enum.autocomplete(["r"], [], context)),
            [Autocompletion("RED", "RED"), Autocompletion("GREEN", "GREEN")],
        )
        self.assertListEqual(
            list(enum.autocomplete(["e", "b"], [], context)),
            [Autocompletion("BLUE", "BLUE")],
        )


if __name__ == "__main__":
    unittest.main()
