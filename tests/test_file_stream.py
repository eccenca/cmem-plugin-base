"""Tests for file stream utilities.

This module contains tests for the File class methods,
specifically testing the is_text, is_bytes, read_text, and read_bytes methods
with various file types including text (JSON) and binary (PDF) files.
"""

import hashlib
import tempfile

import pytest

from cmem_plugin_base.dataintegration.entity import Entity
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from cmem_plugin_base.testing import TestPluginContext
from tests.conftest import ResourceFixture

PDF_CHECKSUM = "ec19194d4aad4f0a452b60f92009c0ba3a2b909ddbb2483f65ff91f72c2ec8b3"


def test_file_class_methods(json_resource: ResourceFixture, pdf_resource: ResourceFixture) -> None:
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
    context = TestPluginContext(project_id=json_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["sample_test.json"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    assert file.is_text(context=context)
    assert not file.is_bytes(context=context)
    assert file.read_text(context=context) == "SAMPLE CONTENT"

    # Test binary file methods
    context = TestPluginContext(project_id=pdf_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    assert not file.is_text(context=context)
    assert file.is_bytes(context=context)
    content = file.read_bytes(context=context)
    checksum = hashlib.sha256(content).hexdigest()
    assert checksum == PDF_CHECKSUM
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True, mode="wb") as temp2:
        temp2.write(content)


def test_reads_project_file_with_cmempy(pdf_resource: ResourceFixture) -> None:
    """Passing only a project ID reads the file with cmempy.

    Args:
        pdf_resource: Fixture providing a PDF test resource

    """
    setup_cmempy_user_access(TestPluginContext().user)
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    content = file.read_bytes(pdf_resource.project_name)

    assert hashlib.sha256(content).hexdigest() == PDF_CHECKSUM


def test_reads_project_file_without_cmempy_environment(
    pdf_resource: ResourceFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reading with a context needs no cmempy environment at all.

    This simulates a plugin running inside DataIntegration: the context carries the token
    and the endpoint URLs, and nothing in the process configures cmempy. The context is
    built before the environment is stripped, because TestUserContext still mints its
    token via cmempy and TestSystemContext resolves its URLs in __init__.

    Args:
        pdf_resource: Fixture providing a PDF test resource
        monkeypatch: Fixture used to remove the cmempy environment

    """
    context = TestPluginContext(project_id=pdf_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)
    for variable in (
        "CMEM_BASE_URI",
        "DEPLOY_BASE_URL",
        "OAUTH_GRANT_TYPE",
        "OAUTH_ACCESS_TOKEN",
        "OAUTH_CLIENT_ID",
        "OAUTH_CLIENT_SECRET",
    ):
        monkeypatch.delenv(variable, raising=False)

    content = file.read_bytes(context=context)

    assert hashlib.sha256(content).hexdigest() == PDF_CHECKSUM


def test_reports_missing_project_file_as_file_not_found_error(
    pdf_resource: ResourceFixture,
) -> None:
    """Reading a missing project file with cmem-client raises FileNotFoundError.

    Note that the cmempy path behaves differently: get_resource_response() calls
    raise_for_status(), so it raises a requests HTTPError instead.

    Args:
        pdf_resource: Fixture providing an existing project to read from

    """
    context = TestPluginContext(project_id=pdf_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["does-not-exist.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    with pytest.raises(FileNotFoundError):
        file.read_bytes(context=context)


def test_requires_project_id_or_context() -> None:
    """Reading without a project ID and without a context is an error."""
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    with pytest.raises(ValueError, match="Either project_id or context"):
        file.read_bytes()


def test_file_streaming_methods(
    json_resource: ResourceFixture, pdf_resource: ResourceFixture
) -> None:
    """Test the File class streaming methods for memory-efficient processing.

    This test validates:
    1. Text streaming - ensures line-by-line processing of text files
    2. Binary streaming - ensures chunk-based processing of binary files

    Args:
        json_resource: Fixture providing a JSON test resource
        pdf_resource: Fixture providing a PDF test resource

    """
    # Test text streaming
    context = TestPluginContext(project_id=json_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["sample_test.json"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    with file.text_stream(context=context) as stream:
        content_lines = [line.strip() for line in stream]
        assert "".join(content_lines) == "SAMPLE CONTENT"

    # Test binary streaming
    context = TestPluginContext(project_id=pdf_resource.project_name)
    file_entity = Entity(uri="test.uri", values=[["sample.pdf"], ["Project"], [], []])
    file = FileEntitySchema().from_entity(file_entity)

    with file.bytes_stream(context=context) as stream:
        chunks = []
        while chunk := stream.read(1024):
            chunks.append(chunk)

        full_content = b"".join(chunks)
        checksum = hashlib.sha256(full_content).hexdigest()
        assert checksum == PDF_CHECKSUM
