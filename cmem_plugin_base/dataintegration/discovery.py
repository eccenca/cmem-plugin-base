"""Package and plugin discovery module."""
import importlib
import importlib.util
import json
import pkgutil
from subprocess import check_output  # nosec
from typing import Sequence

from cmem_plugin_base.dataintegration.description import PluginDescription, Plugin


def get_packages():
    """Get installed python packages.

    Returns a list of dict with the following keys:
     - name - package name
     - version - package version
    """
    return json.loads(check_output(["pip", "list", "--format", "json"], shell=False))


def discover_plugins_in_module(
    package_name: str = "cmem",
) -> Sequence[PluginDescription]:
    """Finds all plugins within a base package.

    :param package_name: The base package. Will recurse into all submodules
        of this package.
    """

    def import_submodules(package):
        for _loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + "." + name
            module = importlib.import_module(full_name)
            if is_pkg:
                import_submodules(module)

    Plugin.plugins = []
    import_submodules(importlib.import_module(package_name))
    return Plugin.plugins


def discover_plugins(package_name: str = "cmem_plugin"):
    """Discover plugin descriptions in packages.

    This is the main discovery method which is executed by DataIntegration.
    It will go through all modules which base names starts with
    package_name.

    :param package_name: The package prefix.
    """
    target_packages = []
    plugin_descriptions = []
    # select prefixed packages
    for module in pkgutil.iter_modules():
        name = module.name
        if name.startswith(package_name) and name != "cmem_plugin_base":
            target_packages.append(name)
    for name in target_packages:
        for plugin in discover_plugins_in_module(package_name=name):
            plugin_descriptions.append(plugin)
    return plugin_descriptions
