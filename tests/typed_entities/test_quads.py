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

    def __init__(self) -> None:
        pass

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
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
                subject = Resource("urn:instance:person1"),
                predicate = Resource("urn:instance:hasCity"),
                object = Resource("urn:instance:city1")
            ),
            Quad(
                subject = Resource("urn:instance:person2"),
                predicate = Resource("urn:instance:hasCity"),
                object = PlainLiteral("Berlin")
            ),
            Quad(
                subject = Resource("urn:instance:person3"),
                predicate = Resource("urn:instance:hasCity"),
                object = LanguageLiteral("Berlin", "en")
            ),
            Quad(
                subject = Resource("urn:instance:person4"),
                predicate = Resource("urn:instance:age"),
                object = DataTypeLiteral("29", "http://www.w3.org/2001/XMLSchema#int")
            ),
            Quad(
                subject = BlankNode("person5"),
                predicate = Resource("urn:instance:hasCity"),
                object = BlankNode("city1")
            )
        ]

        # Execute operator
        input_entities = QuadEntitySchema().to_entities(iter(quads))
        output = ProcessQuadsOperator().execute([input_entities], ExecutionContext())

        # Check output
        output_quads = list(QuadEntitySchema().from_entities(output).values)
        expected_output_quads = copy.deepcopy(quads)
        expected_output_quads[0].subject = Resource("urn:instance:modified")
        assert output_quads == expected_output_quads


if __name__ == "__main__":
    unittest.main()
