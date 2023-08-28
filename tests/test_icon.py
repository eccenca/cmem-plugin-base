"""tests for icon class."""
import pytest

from cmem_plugin_base.dataintegration.description import Icon


def test_for_errors():
    """Test Icon inits with errors."""
    with pytest.raises(FileNotFoundError):
        Icon(file_name="no.file", package=__package__)
    with pytest.raises(ValueError):
        Icon(file_name="icons/test.txt", package=__package__)
    with pytest.raises(ValueError):
        Icon(file_name="icons/test.nomime", package=__package__)


def test_svg():
    """Test SVG icon"""
    icon = Icon(file_name="icons/test.svg", package=__package__)
    assert icon.mime_type == "image/svg+xml"
    assert len(str(icon)) == 906


def test_png():
    """Test PNG icon"""
    icon = Icon(file_name="icons/test.png", package=__package__)
    assert icon.mime_type == "image/png"
    assert len(str(icon)) == 63818
