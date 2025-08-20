"""Tests for file stream utilities.

This module contains tests for the File class methods,
specifically testing the is_text, is_bytes, read_text, and read_bytes methods
with various file types including text (JSON) and binary (PDF) files.
"""

import hashlib
import tempfile

from cmem_plugin_base.dataintegration.entity import Entity
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema
from tests.conftest import ResourceFixture


def test_file_class_methods(
    json_resource: ResourceFixture, pdf_resource: ResourceFixture
) -> None:
    """Test the File class methods with different file types.

    This test validates:
    1. Text file (JSON) processing - ensures proper text detection and content reading
    2. Binary file (PDF) processing - ensures binary detection, checksum validation,
       and proper file handling

    Args:
        json_resource: Fixture providing a JSON test resource
        pdf_resource: Fixture providing a PDF test resource

    """
    # Test text file methods
    file_entity = Entity(uri="test.uri", values=[["sample_test.json"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)
    
    assert file.is_text(json_resource.project_name)
    assert not file.is_bytes(json_resource.project_name)
    assert file.read_text(json_resource.project_name) == "SAMPLE CONTENT"

    # Test binary file methods
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)
    
    assert not file.is_text(pdf_resource.project_name)
    assert file.is_bytes(pdf_resource.project_name)
    content = file.read_bytes(pdf_resource.project_name)
    checksum = hashlib.sha256(content).hexdigest()
    assert checksum == "ec19194d4aad4f0a452b60f92009c0ba3a2b909ddbb2483f65ff91f72c2ec8b3"
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True, mode="wb") as temp2:
        temp2.write(content)
