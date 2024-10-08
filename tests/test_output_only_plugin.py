"""test file."""

from collections.abc import Sequence

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin


@Plugin(
    label="My Plugin",
    description="Plugin Description",
    documentation="""# Plugin Documentation
    is in markdown
    ## nice
    """,
    parameters=[
        PluginParameter(
            name="param1",
            label="My First Parameter",
            description="My first description",
            default_value="default value",
        )
    ],
)
class OutputOnlyPlugin(WorkflowPlugin):
    """Example Plugin - only Output."""

    def __init__(self, param1: str) -> None:
        self.param1 = param1

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Execute the workflow plugin on a given collection of entities."""
        entity1 = Entity(uri="urn:my:1", values=(["value1"], ["value2"]))
        entity2 = Entity(uri="urn:my:2", values=(["value3"], ["value4"]))
        schema = EntitySchema(
            type_uri="urn:my-entity",
            paths=(EntityPath(path="urn:name"), EntityPath(path="urn:desc")),
        )
        return Entities(entities=iter([entity1, entity2]), schema=schema)


def test_output_only_plugin() -> None:
    """Test example Workflow Plugin."""
    output_only = OutputOnlyPlugin(param1="test")
    result = output_only.execute((), ExecutionContext())
    for item in result.entities:
        assert len(item.values) == len(result.schema.paths)
