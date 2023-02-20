import unittest
from enum import Enum

from cmem_plugin_base.dataintegration.types import (
    EnumParameterType,
    Autocompletion, ParameterTypes
)
from tests.utils import TestPluginContext


# dummy plugin context to be used in tests
context = TestPluginContext()


class TypesTest(unittest.TestCase):
    class MissingType:
        pass

    def test_missing_type(self):
        self.assertRaisesRegex(
            ValueError, "unsupported type",
            lambda: ParameterTypes.get_type(TypesTest.MissingType)
        )


class BasicTypesTest(unittest.TestCase):
    def test_detection(self):
        self.assertEqual(ParameterTypes.get_type(str).name, "string")
        self.assertEqual(ParameterTypes.get_type(int).name, "Long")
        self.assertEqual(ParameterTypes.get_type(float).name, "double")
        self.assertEqual(ParameterTypes.get_type(bool).name, "boolean")

    def test_conversion(self):
        int_type = ParameterTypes.get_type(int)
        float_type = ParameterTypes.get_type(float)
        bool_type = ParameterTypes.get_type(bool)
        self.assertEqual(int_type.from_string(int_type.to_string(3), context), 3)
        self.assertEqual(float_type.from_string(int_type.to_string(1.2), context), 1.2)
        self.assertEqual(bool_type.from_string(int_type.to_string(True), context), True)
        self.assertEqual(bool_type.from_string(int_type.to_string(False), context),
                         False)


class EnumTest(unittest.TestCase):
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    def test_detection(self):
        self.assertEqual(ParameterTypes.get_type(EnumTest.Color).name, "enumeration")

    def test_conversion(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertEqual(enum.to_string(enum.from_string("RED", context)), "RED")
        self.assertEqual(enum.to_string(enum.from_string("GREEN", context)), "GREEN")

    def test_invalid_values(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertRaisesRegex(
            ValueError, "Empty value is not allowed",
            lambda: enum.from_string("", context)
        )
        self.assertRaisesRegex(
            ValueError, "not a valid value", lambda: enum.from_string("CYAN", context)
        )

    def test_autocomplete(self):
        enum = EnumParameterType(EnumTest.Color)
        self.assertListEqual(
            list(enum.autocomplete(["red"], [], context)),
            [Autocompletion("RED", "RED")]
        )
        self.assertListEqual(
            list(enum.autocomplete(["een"], [], context)),
            [Autocompletion("GREEN", "GREEN")]
        )
        self.assertListEqual(
            list(enum.autocomplete(["r"], [], context)),
            [Autocompletion("RED", "RED"), Autocompletion("GREEN", "GREEN")],
        )
        self.assertListEqual(
            list(enum.autocomplete(["e", "b"], [], context)),
            [Autocompletion("BLUE", "BLUE")]
        )


if __name__ == "__main__":
    unittest.main()
