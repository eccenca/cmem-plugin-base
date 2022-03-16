"""Parameter types."""
from dataclasses import dataclass
from enum import Enum
from inspect import Parameter
from typing import Optional, TypeVar, Generic, Type, Iterable


@dataclass
class Autocompletion:
    """A single auto-completion result."""

    value: str
    """The value to which the parameter value should be set."""

    label: Optional[str]
    """An optional label that a human user would see instead."""


ValueType = TypeVar('ValueType')


class ParameterType(Generic[ValueType]):
    """Represents a plugin parameter type.
    Provides string-based serialization and autocompletion. """

    name: str
    """The name by which this type can be identified. If available,
    this should be the same as the corresponding DataIntegration type name."""

    allow_only_autocompleted_values: bool = False
    """Hint to the UI that it should only allow to set values for the parameter coming
     from the auto-completion.
    """

    autocomplete_value_with_labels: bool = False
    """Signals that the auto-completed values have labels that must be
    displayed to the user."""

    # flake8: noqa
    # pylint: disable=no-member
    def get_type(self):
        """Retrieves the type that is supported by a given instance."""
        return self.__orig_bases__[0].__args__[0]

    def from_string(self, value: str) -> ValueType:
        """Parses strings into parameter values."""

    # pylint: disable=no-self-use
    def to_string(self, value: ValueType) -> str:
        """Converts parameter values into their string representation.
        """
        return str(value)

    # pylint: disable=unused-argument
    def autocomplete(self, query_terms: list[str],
                     project_id: Optional[str] = None) -> list[Autocompletion]:
        """Autocompletion request.
        Returns all results that match ALL provided query terms.

        :param query_terms: A list of lower case conjunctive search terms.
        :param project_id: The identifier of the project.
        """
        return []

    def label(self, value: str, project_id: Optional[str] = None) -> Optional[str]:
        """Returns the label if exists for the given value.
        """
        return None


class StringParameterType(ParameterType[str]):
    """String type"""

    name = "string"

    def from_string(self, value: str) -> str:
        return value


class IntParameterType(ParameterType[int]):
    """Int type"""

    name = "Long"

    def from_string(self, value: str) -> int:
        return int(value)


class FloatParameterType(ParameterType[float]):
    """Float type"""

    name = "double"

    def from_string(self, value: str) -> float:
        return float(value)


class BoolParameterType(ParameterType[bool]):
    """Boolean type"""

    name = "boolean"

    def from_string(self, value: str) -> bool:
        lower = value.lower()
        if lower in ("true", "1"):
            return True
        if lower in ("false", "0"):
            return False
        raise ValueError("Value must be either 'true' or 'false'")


class EnumParameterType(ParameterType[Enum]):
    """Enumeration type"""

    name = "enumeration"

    allow_only_autocompleted_values = True

    def __init__(self, enum_type: Type[Enum]):
        super().__init__()
        self.enum_type = enum_type

    def from_string(self, value: str) -> Enum:
        values = self.enum_type.__members__
        if not value:
            raise ValueError("Empty value is not allowed.")
        if value not in values:
            vals = ', '.join(list(values.keys()))
            raise ValueError(f"'{value}' is not a valid value. Valid values: {vals}.")
        return values[value]

    def to_string(self, value: Enum) -> str:
        return value.name

    def autocomplete(self, query_terms: list[str],
                     project_id: Optional[str] = None) -> list[Autocompletion]:
        values = self.enum_type.__members__.keys()
        return list(self.find_matches(query_terms, values))

    @staticmethod
    def find_matches(lower_case_terms: list[str],
                     values: Iterable[str]) -> Iterable[Autocompletion]:
        """Finds autocompletions in a list of values"""
        for value in values:
            if EnumParameterType.matches_search_term(lower_case_terms, value.lower()):
                yield Autocompletion(value, value)

    @staticmethod
    def matches_search_term(lower_case_terms: list[str], search_in: str) -> bool:
        """Tests if a string contains a list of (lower case) search terms."""
        lower_case_text = search_in.lower()
        return all(search_term in lower_case_text for search_term in lower_case_terms)


basic_types: list[ParameterType] = [StringParameterType(), BoolParameterType(),
                                    IntParameterType(), FloatParameterType()]


def get_type(param_type: Type) -> ParameterType:
    """Retrieves the ParameterType instance for a given type."""

    if issubclass(param_type, Enum):
        return EnumParameterType(param_type)
    found_type = next((t for t in basic_types
                       if issubclass(param_type, t.get_type())), None)
    if found_type is None:
        mapped = map(lambda t: str(t.get_type().__name__), basic_types)
        raise ValueError(
            f"Parameter has an unsupported type {param_type.__name__}. "
            "Supported types are: Enum, "
            f"{', '.join(list(mapped))}."
        )
    return found_type


def get_param_type(param: Parameter) -> ParameterType:
    """Retrieves the ParameterType instance for a given parameter."""

    if param.annotation == Parameter.empty:
        # If there is no type annotation, DI should send the parameter as a string
        return StringParameterType()
    return get_type(param.annotation)
