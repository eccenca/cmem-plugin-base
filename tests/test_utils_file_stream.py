"""Tests for file stream utilities.

This module contains tests for the file_stream utility functions,
specifically testing the prepare_stream_for_processing function
with various file types including text (JSON) and binary (PDF) files.
"""

import hashlib
import tempfile

from cmem_plugin_base.dataintegration.entity import Entity
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema
from cmem_plugin_base.dataintegration.utils.file_stream import prepare_stream_for_processing
from tests.conftest import ResourceFixture


def test_prepare_stream_for_processing(
    json_resource: ResourceFixture, pdf_resource: ResourceFixture
) -> None:
    """Test the prepare_stream_for_processing function with different file types.

    This test validates:
    1. Text file (JSON) processing - ensures proper text detection and content reading
    2. Binary file (PDF) processing - ensures binary detection, checksum validation,
       and proper file handling

    Args:
        json_resource: Fixture providing a JSON test resource
        pdf_resource: Fixture providing a PDF test resource

    """
    file_entity = Entity(uri="test.uri", values=[["sample_test.json"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)
    with file.read_stream(json_resource.project_name) as stream:
        prepared_stream, is_text = prepare_stream_for_processing(stream)
        assert is_text
        assert prepared_stream.read() == "SAMPLE CONTENT"

    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)
    with file.read_stream(pdf_resource.project_name) as stream:
        prepared_stream, is_text = prepare_stream_for_processing(stream)
        assert not is_text
        content = prepared_stream.read()
        checksum = hashlib.sha256(content).hexdigest()  # type: ignore[arg-type]
        assert checksum == "ec19194d4aad4f0a452b60f92009c0ba3a2b909ddbb2483f65ff91f72c2ec8b3"
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True, mode="wb") as temp2:
            temp2.write(content)  # type: ignore[arg-type]
