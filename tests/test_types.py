import unittest
from enum import Enum

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import (
    EnumParameterType,
    Autocompletion,
    get_type,
)


class TestPluginContext(PluginContext):

    def __init__(self):
        self.user = None
        self.project_id = "DummyProject"


# dummy plugin context to be used in tests
pluginContext = TestPluginContext()


class TypesTest(unittest.TestCase):
    class MissingType:
        pass

    def test_missing_type(self):
        self.assertRaisesRegex(
            ValueError, "unsupported type", lambda: get_type(TypesTest.MissingType)
        )


class BasicTypesTest(unittest.TestCase):
    def test_detection(self):
        self.assertEqual(get_type(str).name, "string")
        self.assertEqual(get_type(int).name, "Long")
        self.assertEqual(get_type(float).name, "double")
        self.assertEqual(get_type(bool).name, "boolean")

    def test_conversion(self):
        int_type = get_type(int)
        float_type = get_type(float)
        bool_type = get_type(bool)
        self.assertEqual(int_type.from_string(int_type.to_string(3)), 3)
        self.assertEqual(float_type.from_string(int_type.to_string(1.2)), 1.2)
        self.assertEqual(bool_type.from_string(int_type.to_string(True)), True)
        self.assertEqual(bool_type.from_string(int_type.to_string(False)), False)


class EnumTest(unittest.TestCase):
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    def test_detection(self):
        self.assertEqual(get_type(EnumTest.Color).name, "enumeration")

    def test_conversion(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertEqual(enum.to_string(enum.from_string("RED")), "RED")
        self.assertEqual(enum.to_string(enum.from_string("GREEN")), "GREEN")

    def test_invalid_values(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertRaisesRegex(
            ValueError, "Empty value is not allowed", lambda: enum.from_string("")
        )
        self.assertRaisesRegex(
            ValueError, "not a valid value", lambda: enum.from_string("CYAN")
        )

    def test_autocomplete(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertListEqual(
            list(enum.autocomplete(["red"], pluginContext)),
            [Autocompletion("RED", "RED")]
        )
        self.assertListEqual(
            list(enum.autocomplete(["een"], pluginContext)),
            [Autocompletion("GREEN", "GREEN")]
        )
        self.assertListEqual(
            list(enum.autocomplete(["r"], pluginContext)),
            [Autocompletion("RED", "RED"), Autocompletion("GREEN", "GREEN")],
        )
        self.assertListEqual(
            list(enum.autocomplete(["e", "b"], pluginContext)),
            [Autocompletion("BLUE", "BLUE")]
        )


if __name__ == "__main__":
    unittest.main()
