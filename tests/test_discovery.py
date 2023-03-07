"""discovery test module"""
import pytest

from cmem_plugin_base.dataintegration.discovery import discover_plugins


@pytest.mark.skip(reason='cmem-plugin-examples is not added')
def test_discover_plugins():
    """test plugin discovery."""
    plugins = discover_plugins("cmem_plugin").plugins

    # cmem_plugin_examples should have at least one plugin
    assert len(plugins) > 0
