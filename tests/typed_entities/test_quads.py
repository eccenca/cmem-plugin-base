"""Test for RDF quads."""
import copy
import unittest
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.typed_entities.quads import (
    BlankNode,
    DataTypeLiteral,
    LanguageLiteral,
    PlainLiteral,
    Quad,
    QuadEntitySchema,
    Resource,
)


class ProcessQuadsOperator(WorkflowPlugin):
    """Test operator that modifies the subject of the first quad."""

    def __init__(self) -> None:
        pass

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Modify the subject of the first quad."""
        quads = list(QuadEntitySchema().from_entities(inputs[0]).values)
        quads[0].subject.value = "urn:instance:modified"
        return QuadEntitySchema().to_entities(iter(quads))


class QuadsTest(unittest.TestCase):
    """Test for the typed entities feature."""

    def test_quads(self) -> None:
        """Test RDF quads."""
        # Creat quads with all supported node types
        quads = [
            Quad(
                subject = Resource(value="urn:instance:person1"),
                predicate = Resource(value="urn:instance:hasCity"),
                object = Resource(value="urn:instance:city1")
            ),
            Quad(
                subject = Resource(value="urn:instance:person2"),
                predicate = Resource(value="urn:instance:hasCity"),
                object = PlainLiteral(value="Berlin")
            ),
            Quad(
                subject = Resource(value="urn:instance:person3"),
                predicate = Resource(value="urn:instance:hasCity"),
                object = LanguageLiteral(value="Berlin", language="en")
            ),
            Quad(
                subject = Resource(value="urn:instance:person4"),
                predicate = Resource(value="urn:instance:age"),
                object = DataTypeLiteral(value="29", data_type="http://www.w3.org/2001/XMLSchema#int")
            ),
            Quad(
                subject = BlankNode(value="person5"),
                predicate = Resource(value="urn:instance:hasCity"),
                object = BlankNode(value="city1")
            )
        ]

        # Execute operator
        input_entities = QuadEntitySchema().to_entities(iter(quads))
        output = ProcessQuadsOperator().execute([input_entities], ExecutionContext())

        # Check output
        output_quads = list(QuadEntitySchema().from_entities(output).values)
        expected_output_quads = copy.deepcopy(quads)
        expected_output_quads[0].subject = Resource(value="urn:instance:modified")
        assert output_quads == expected_output_quads


if __name__ == "__main__":
    unittest.main()
