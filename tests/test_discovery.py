"""discovery test module"""
from unittest import skip

from cmem_plugin_base.dataintegration.discovery import discover_plugins


@skip
def test_discover_plugins():
    """test plugin discovery."""
    plugins = discover_plugins("cmem_plugin").plugins

    # cmem_plugin_examples should have at least one plugin
    assert len(plugins) > 0
