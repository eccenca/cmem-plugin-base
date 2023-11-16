"""Workflow operator input and output ports."""

from typing import Sequence
from cmem_plugin_base.dataintegration.entity import EntitySchema


class Port:
    """Specifies the type of input or output ports."""


class FixedSchemaPort(Port):
    """Input or output port that has a fixed schema."""

    def __init__(self, schema: EntitySchema):
        self.schema = schema


class FlexibleSchemaPort(Port):
    """Port that does not have a fixed schema, but will adapt its schema to the
    connected port.
    Flexible input ports will adapt the schema to the connected output.
    Flexible output ports will adapt the schema to the connected input.
    It is not allowed to connect two flexible ports."""


class UnknownSchemaPort(Port):
    """Port for which the schema is not known in advance.
    This includes output ports with a schema that depends on external factors
    (e.g., REST requests)."""


class InputPorts:
    """Specifies the input ports of a workflow operator."""


class FixedNumberOfInputs(InputPorts):
    """Operator accepts a fixed number of inputs."""

    def __init__(self, ports: Sequence[Port]):
        self.ports = ports


class FlexibleNumberOfInputs(InputPorts):
    """Operator accepts a flexible number of inputs.
    At the moment, each input is a flexible schema port."""
