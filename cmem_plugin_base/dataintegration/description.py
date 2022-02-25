"""Classes for describing plugins"""
from typing import Optional, List

from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin, TransformPlugin


class PluginParameter:
    """A plugin parameter.

    :param name: The name of the parameter
    :param label: A human-readable label of the parameter
    :param description: A human-readable description of the parameter
    :param default_value: The parameter default value (optional)
    :param advanced: True, if this is an advanced parameter that should only be
        changed by experienced users
    """

    def __init__(
        self,
        name: str,
        label: str = "",
        description: str = "",
        default_value: Optional[str] = None,
        advanced: bool = False,
    ) -> None:
        self.name = name
        self.label = label
        self.description = description
        self.default_value = default_value
        self.advanced = advanced


class PluginDescription:
    """A plugin description.

    :param plugin_class: The plugin implementation class
    :param label: A human-readable label of the plugin
    :param description: A short (few sentence) description of this plugin.
    :param documentation: Documentation for this plugin in Markdown.
    :param categories: The categories to which this plugin belongs to.
    :param parameters: Available plugin parameters
    """

    def __init__(
        self,
        plugin_class,
        label: str,
        description: str = "",
        documentation: str = "",
        categories: List[str] = None,
        parameters: List[PluginParameter] = None,
    ) -> None:
        #  Set the type of the plugin. Same as the class name of the plugin
        #  base class, e.g., 'WorkflowPlugin'.
        if issubclass(plugin_class, WorkflowPlugin):
            self.plugin_type = "WorkflowPlugin"
        elif issubclass(plugin_class, TransformPlugin):
            self.plugin_type = "TransformPlugin"
        else:
            raise ValueError(
                f"Class {plugin_class.__name__} does not implement a supported"
                f"plugin base class (e.g., WorkflowPlugin)."
            )

        self.plugin_class = plugin_class
        self.module_name = plugin_class.__module__
        self.class_name = plugin_class.__name__
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        self.label = label
        self.description = description
        self.documentation = documentation
        if parameters is None:
            self.parameters = []
        else:
            self.parameters = parameters


class Plugin:
    """Annotate classes with plugin descriptions.

    :param label: A human-readable label of the plugin
    :param description: A short (few sentence) description of this plugin.
    :param documentation: Documentation for this plugin in Markdown.
    :param categories: The categories to which this plugin belongs to.
    :param parameters: Available plugin parameters
    """
    plugins: list[PluginDescription] = []

    def __init__(
        self,
        label: str,
        description: str = "",
        documentation: str = "",
        categories: List[str] = None,
        parameters: List[PluginParameter] = None,
    ):
        self.label = label
        self.description = description
        self.documentation = documentation
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        if parameters is None:
            self.parameters = []
        else:
            self.parameters = parameters

    def __call__(self, func):
        plugin_desc = PluginDescription(
            plugin_class=func,
            label=self.label,
            description=self.description,
            documentation=self.documentation,
            categories=self.categories,
            parameters=self.parameters,
        )
        Plugin.plugins.append(plugin_desc)
        return func
