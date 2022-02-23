import importlib
import importlib.util
import pkgutil
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin, TransformPlugin
from typing import Iterator, Sequence, Optional


class PluginParameter:
    """A plugin parameter.

    :param name: The name of the parameter
    :param label: A human-readable label of the parameter
    :param description: A human-readable description of the parameter
    :param default_value: The parameter default value (optional)
    :param advanced: True, if this is an advanced parameter that should only be changed by experienced users
    """

    def __init__(self, name: str, label: str, description: str,
                 default_value: Optional[str], advanced: bool) -> None:
        self.name = name
        self.label = label
        self.description = description
        self.default_value = default_value
        self.advanced = advanced


class PluginDescription:
    """A plugin description.

    :param plugin_type: The type of the plugin. Same as the class name of the plugin base class, e.g., 'WorkflowPlugin'.
    :param plugin_class: The plugin implementation class
    :param label: A human-readable label of the plugin
    :param description: A short (few sentence) description of this plugin.
    :param documentation: Documentation for this plugin in Markdown.
    :param categories: The categories to which this plugin belongs to.
    :param parameters: Available plugin parameters
    """

    def __init__(self, plugin_type: str, plugin_class, label: str, description: str = "", documentation: str = "",
                 categories: Sequence[str] = [], parameters: Sequence[PluginParameter] = []) -> None:
        self.plugin_type = plugin_type
        self.plugin_class = plugin_class
        self.module_name = plugin_class.__module__
        self.class_name = plugin_class.__name__
        self.categories = categories
        self.label = label
        self.description = description
        self.documentation = documentation
        self.parameters = parameters


def discover_plugins(package_name: str = "cmem") -> Sequence[PluginDescription]:
    """Finds all plugins within a base package.

    :param package_name: The base package. Will recurse into all submodules of this package.
    """

    def import_submodules(package):
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            module = importlib.import_module(full_name)
            if is_pkg:
                import_submodules(module)

    import_submodules(importlib.import_module(package_name))

    plugins = []
    for workflow_plugin in WorkflowPlugin.__subclasses__():
        plugins.append(PluginDescription(WorkflowPlugin.__name__, workflow_plugin, workflow_plugin.__name__))
    for transform_plugin in TransformPlugin.__subclasses__():
        plugins.append(PluginDescription(TransformPlugin.__name__, transform_plugin, transform_plugin.__name__))
    return plugins
