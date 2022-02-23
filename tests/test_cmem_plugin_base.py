"""test file."""
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntitySchema,
    EntityPath,
)


class OutputOnlyPlugin(WorkflowPlugin):
    """Example Plugin - only Output."""

    def __init__(self):
        pass

    def execute(self, inputs=()) -> Entities:
        entity1 = Entity(uri="urn:my:1", values=(["value1"], ["value2"]))
        entity2 = Entity(uri="urn:my:2", values=(["value3"], ["value4"]))
        schema = EntitySchema(
            type_uri="urn:my-entity",
            paths=(EntityPath(path="urn:name"), EntityPath(path="urn:desc")),
        )
        return Entities(entities=[entity1, entity2], schema=schema)


def test_readonly_plugin():
    """Test example Workflow Plugin."""
    output_only = OutputOnlyPlugin()
    result = output_only.execute()
    for item in result.entities:
        assert len(item.values) == len(result.schema.paths)
