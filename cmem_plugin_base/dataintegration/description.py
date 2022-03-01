"""Classes for describing plugins"""
import inspect
from inspect import Signature, Parameter
from typing import Optional, List

from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin, TransformPlugin
from cmem_plugin_base.dataintegration.utils import generate_id


class PluginParameter:
    """A plugin parameter.

    :param name: The name of the parameter
    :param label: A human-readable label of the parameter
    :param description: A human-readable description of the parameter
    :param type_name: Optionally overrides the parameter type.
                      Usually does not have to be set manually as it will be inferred from the plugin automatically.
    :param default_value: The parameter default value (optional)
    :param advanced: True, if this is an advanced parameter that should only be
        changed by experienced users
    """

    def __init__(
        self,
        name: str,
        label: str = "",
        description: str = "",
        type_name: Optional[str] = None,
        default_value: Optional[str] = None,
        advanced: bool = False,
    ) -> None:
        self.name = name
        self.label = label
        self.description = description
        self.type_name = type_name
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
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        plugin_class,
        label: str,
        plugin_id: str = None,
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
        if plugin_id is None:
            self.plugin_id = generate_id(
                (self.module_name + "-" + self.class_name).replace(".", "-")
            )
        else:
            self.plugin_id = plugin_id
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
    :param plugin_id: Optionally sets the plugin identifier.
        If not set, an identifier will be generated from the module and class name.
    :param description: A short (few sentence) description of this plugin.
    :param documentation: Documentation for this plugin in Markdown. Note that you
        do not need to add a first level heading to the markdown since the
        documentation rendering component will add a heading anyway.
    :param categories: The categories to which this plugin belongs to.
    :param parameters: Available plugin parameters
    """

    plugins: list[PluginDescription] = []

    def __init__(
        self,
        label: str,
        plugin_id: Optional[str] = None,
        description: str = "",
        documentation: str = "",
        categories: List[str] = None,
        parameters: List[PluginParameter] = None,
    ):
        self.label = label
        self.description = description
        self.documentation = documentation
        self.plugin_id = plugin_id
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
            plugin_id=self.plugin_id,
            description=self.description,
            documentation=self.documentation,
            categories=self.categories,
            parameters=self.retrieve_parameters(func),
        )
        Plugin.plugins.append(plugin_desc)
        return func

    def retrieve_parameters(self, plugin_class) -> List[PluginParameter]:
        """Retrieves parameters from a plugin class and matches them with the user parameter definitions.
        """

        params = []
        sig = inspect.signature(plugin_class.__init__)
        for name in sig.parameters:
            if name != "self":
                param = next((p for p in self.parameters if p.name == name), None)
                if param is None:
                    param = PluginParameter(name)
                param.type_name = self.param_type_name(sig.parameters[name])
                params.append(param)
        return params

    @staticmethod
    def param_type_name(param: Parameter):
        """Determines the DataIntegration type name for a parameter.
        """

        # Mapping between Python type and DataIntegration ParameterType name
        type_map = {
            str: 'string',
            int: 'long',
            float: 'double',
            bool: 'boolean'
        }
        supported_types_str = f"Supported types are: ${', '.join(list(map(lambda c: c.__name__,type_map)))}."
        if param.annotation == Parameter.empty:
            # If there is no type annotation, DI should send the parameter as a string
            return 'string'
        type_name = type_map.get(param.annotation)
        if type_name is None:
            raise ValueError(
                f"Parameter '{param.name}' has an unsupported type {param.annotation.__name__}. {supported_types_str}"
            )
        return type_name