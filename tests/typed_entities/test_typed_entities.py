"""Test for the typed entities feature."""

import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path

import pytest

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.entity import Entities, Entity
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile
from cmem_plugin_base.testing import TestTaskContext


class ConcatFilesOperator(WorkflowPlugin):
    """Test operator that concatenates input files."""

    def __init__(self):
        self.input_ports = FixedNumberOfInputs([FixedSchemaPort(FileEntitySchema())])
        self.output_port = FixedSchemaPort(FileEntitySchema())

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
        """Concatenate input files"""
        input_files = FileEntitySchema().from_entities(inputs[0])

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as o_file:
            output_name = o_file.name
            for file in input_files.values:
                if isinstance(file, LocalFile):
                    with file.read_stream(context.task.project_id()) as in_stream:
                        o_file.write(in_stream.read())

        return FileEntitySchema().to_entities(iter([LocalFile(output_name)]))


class TypedEntitiesTest(unittest.TestCase):
    """Test for the typed entities feature."""

    def test_files(self) -> None:
        """Test file entity schema."""
        # Create two files
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp1:
            temp1.write("ABC")
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp2:
            temp2.write("123")

        # Execute operator
        input_entities = FileEntitySchema().to_entities(
            iter([LocalFile(temp1.name), LocalFile(temp2.name)])
        )
        context = ExecutionContext()
        context.task = TestTaskContext(project_id="TestProject", task_id="TestTask")
        output = ConcatFilesOperator().execute([input_entities], context)

        # Check output
        assert output is not None
        output_entities = list(output.entities)
        assert len(output_entities) == 1
        with Path(FileEntitySchema().from_entity(output_entities[0]).path).open() as output_file:
            output_str = output_file.read()
            assert output_str == "ABC123"

    def test_file_entity_conversion(self) -> None:
        """Test conversion from entity to file"""
        file_entity = Entity(uri="test.uri", values=[["test.txt"], ["Local"], [], []])
        assert FileEntitySchema().from_entity(file_entity)

        file_entity = Entity(uri="test.uri", values=[["test.txt"], ["Local"], [""], [""]])
        assert FileEntitySchema().from_entity(file_entity)

        with pytest.raises(ValueError, match="File 'test.txt' has unexpected type 'Wrong Type'"):
            FileEntitySchema().from_entity(
                Entity(uri="test.uri", values=[["test.txt"], ["Wrong Type"], [], []])
            )


if __name__ == "__main__":
    unittest.main()
