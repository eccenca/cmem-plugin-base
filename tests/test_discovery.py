"""discovery test module"""
from cmem_plugin_base.dataintegration.discovery import discover_plugins


def test_discover_plugins():
    """test plugin discovery."""
    plugins = discover_plugins("cmem_plugin")

    # cmem_plugin_examples has currently one plugin
    assert len(plugins) == 1
