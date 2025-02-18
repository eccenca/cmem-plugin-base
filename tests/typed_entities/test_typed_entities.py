"""Test for the typed entities feature."""

import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile


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
                    with Path(file.path).open("rb") as f:
                        contents = f.read()
                        o_file.write(contents)

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
        output = ConcatFilesOperator().execute([input_entities], ExecutionContext())

        # Check output
        assert output is not None
        output_entities = list(output.entities)
        assert len(output_entities) == 1
        with Path(FileEntitySchema().from_entity(output_entities[0]).path).open() as output_file:
            output_str = output_file.read()
            assert output_str == "ABC123"


if __name__ == "__main__":
    unittest.main()
