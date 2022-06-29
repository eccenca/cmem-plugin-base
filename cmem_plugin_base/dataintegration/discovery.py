"""Package and plugin discovery module."""
import importlib
import importlib.util
import json
import pkgutil
import sys
import traceback
from subprocess import check_output  # nosec
from types import ModuleType

from cmem_plugin_base.dataintegration.description import PluginDescription, Plugin, \
    PluginDiscoveryResult, PluginDiscoveryError


def get_packages():
    """Get installed python packages.

    Returns a list of dict with the following keys:
     - name - package name
     - version - package version
    """
    return json.loads(check_output(["pip", "list", "--format", "json"], shell=False))


def discover_plugins_in_module(
    package_name: str = "cmem",
) -> list[PluginDescription]:
    """Finds all plugins within a base package.

    :param package_name: The base package. Will recurse into all submodules
        of this package.
    """

    def load_module(module_name: str) -> ModuleType:
        module_is_imported = module_name in sys.modules
        module = importlib.import_module(module_name)
        if module_is_imported:
            importlib.reload(module)  # need to reload in order to discover plugins
        return module

    def import_submodules(module: ModuleType):
        for _loader, name, is_pkg in pkgutil.walk_packages(module.__path__):
            sub_module = load_module(module.__name__ + "." + name)
            if is_pkg:
                import_submodules(sub_module)

    Plugin.plugins = []
    import_submodules(load_module(package_name))
    return Plugin.plugins


def discover_plugins(package_name: str = "cmem_plugin") -> PluginDiscoveryResult:
    """Discover plugin descriptions in packages.

    This is the main discovery method which is executed by DataIntegration.
    It will go through all modules which base names starts with
    package_name.

    :param package_name: The package prefix.
    """
    # pylint: disable=broad-except

    target_packages = []
    plugin_descriptions = PluginDiscoveryResult()
    # select prefixed packages
    for module in pkgutil.iter_modules():
        name = module.name
        if name.startswith(package_name) and name != "cmem_plugin_base":
            target_packages.append(name)
    for name in target_packages:
        try:
            for plugin in discover_plugins_in_module(package_name=name):
                plugin_descriptions.plugins.append(plugin)
        except BaseException as ex:
            error = PluginDiscoveryError(package_name=name,
                                         error_message=str(ex),
                                         error_type=type(ex).__name__,
                                         stack_trace=traceback.format_exc())
            plugin_descriptions.errors.append(error)

    return plugin_descriptions
