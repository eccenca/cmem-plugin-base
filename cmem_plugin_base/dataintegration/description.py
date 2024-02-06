"""Classes for describing plugins"""
import inspect
from base64 import b64encode
from dataclasses import dataclass, field
from inspect import _empty
from mimetypes import guess_type
from pkgutil import get_data
from typing import Optional, List, Type, Any

from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin, TransformPlugin
from cmem_plugin_base.dataintegration.types import (
    ParameterType,
    ParameterTypes,
    PluginContextParameterType,
)
from cmem_plugin_base.dataintegration.utils import generate_id
from cmem_plugin_base.dataintegration.ai.schema_matcher import SchemaMatcherPlugin


class Icon:
    """An Icon.

    :param file_name: The name of the icon file, e.g. 'icon.svg', should be in the
        form of a relative filename, using '/' as the path separator. The parent
        directory name '..' is not allowed, and nor is a rooted name
        (starting with a '/').
    :param package: (Optional) The name of the package, e.g.
        'cmem-plugin-my.workspace', should be in standard module format. For a local
        file from the same module, you can use package=__package__.
    """

    def __init__(
        self,
        file_name: str,
        package: str
    ) -> None:
        self.file_name = file_name

        self.package = package

        try:
            self.data = get_data(self.package, file_name)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"No icon file '{self.file_name}' in package {self.package} found."
            ) from error
        if self.data is None:
            raise FileNotFoundError(
                f"No icon file '{self.file_name}' in package {self.package} found."
            )

        self.mime_type = guess_type(self.file_name)[0]
        if self.mime_type is None:
            raise ValueError(
                f"Could not guess the mime type of the file '{self.file_name}'."
            )
        if not self.mime_type.startswith("image/"):
            raise ValueError(
                f"Guessed mime type '{self.mime_type}' does not start with 'image/'."
            )

    def __str__(self):
        data_base64 = b64encode(self.data).decode()
        return f"""data:{self.mime_type};base64,{data_base64}"""


class PluginParameter:
    """A plugin parameter.

    :param name: The name of the parameter
    :param label: A human-readable label of the parameter
    :param description: A human-readable description of the parameter
    :param param_type: Optionally overrides the parameter type.
        Usually does not have to be set manually as it will be inferred from the
        plugin automatically.
    :param default_value: The parameter default value (optional)
        Will be inferred from the plugin automatically.
    :param advanced: True, if this is an advanced parameter that should only be
        changed by experienced users
    :param visible: If true, the parameter will be displayed to the user in the UI.
    """

    def __init__(
        self,
        name: str,
        label: str = "",
        description: str = "",
        param_type: Optional[ParameterType] = None,
        default_value: Optional[Any] = None,
        advanced: bool = False,
        visible: bool = True,
    ) -> None:
        self.name = name
        self.label = label
        self.description = description
        self.param_type = param_type
        self.default_value = default_value
        self.advanced = advanced
        self.visible = visible


class PluginDescription:
    """A plugin description.

    :param plugin_class: The plugin implementation class
    :param label: A human-readable label of the plugin
    :param description: A short (few sentence) description of this plugin.
    :param documentation: Documentation for this plugin in Markdown.
    :param categories: The categories to which this plugin belongs to.
    :param parameters: Available plugin parameters
    :param icon: An optional custom plugin icon.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(  # pylint: disable=too-many-arguments
        self,
        plugin_class,
        label: str,
        plugin_id: Optional[str] = None,
        description: str = "",
        documentation: str = "",
        categories: Optional[List[str]] = None,
        parameters: Optional[List[PluginParameter]] = None,
        icon: Optional[Icon] = None
    ) -> None:
        #  Set the type of the plugin. Same as the class name of the plugin
        #  base class, e.g., 'WorkflowPlugin'.
        if issubclass(plugin_class, WorkflowPlugin):
            self.plugin_type = "WorkflowPlugin"
        elif issubclass(plugin_class, TransformPlugin):
            self.plugin_type = "TransformPlugin"
        elif issubclass(plugin_class, SchemaMatcherPlugin):
            self.plugin_type = "SchemaMatcherPlugin"
        else:
            raise ValueError(
                f"Class {plugin_class.__name__} does not implement a supported "
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
        self.icon = icon


@dataclass
class PluginDiscoveryError:
    """Generated if a plugin package could not be loaded."""

    package_name: str
    """The name of the package that failed to be loaded."""

    error_message: str
    """The error message"""

    error_type: str
    """The name of the raised exception"""

    stack_trace: str
    """The stack trace of the raised exception"""


@dataclass
class PluginDiscoveryResult:
    """Result of running a plugin discovery"""

    plugins: list[PluginDescription] = field(default_factory=list)
    """The list of discovered plugins"""

    errors: list[PluginDiscoveryError] = field(default_factory=list)
    """Errors that occurred during discovering plugins."""


class Categories:
    """A list of common plugin categories. At the moment, in the UI,
    categories are only utilized for rule operators, such as transform plugins."""

    # Plugins in the 'Recommended' category will be shown preferably
    RECOMMENDED: str = "Recommended"

    # Common transform categories
    COMBINE: str = "Combine"
    CONDITIONAL: str = "Conditional"
    CONVERSION: str = "Conversion"
    DATE: str = "Date"
    EXCEL: str = "Excel"
    EXTRACT: str = "Extract"
    FILTER: str = "Filter"
    GEO: str = "Geo"
    LINGUISTIC: str = "Linguistic"
    NORMALIZE: str = "Normalize"
    NUMERIC: str = "Numeric"
    PARSER: str = "Parser"
    REPLACE: str = "Replace"
    SCRIPTING: str = "Scripting"
    SELECTION: str = "Selection"
    SEQUENCE: str = "Sequence"
    SUBSTRING: str = "Substring"
    TOKENIZATION: str = "Tokenization"
    VALIDATION: str = "Validation"
    VALUE: str = "Value"


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
    :param parameters: Available plugin parameters.
    :param icon: Optional custom plugin icon.
    """

    plugins: list[PluginDescription] = []

    def __init__(
        self,
        label: str,
        plugin_id: Optional[str] = None,
        description: str = "",
        documentation: str = "",
        categories: Optional[List[str]] = None,
        parameters: Optional[List[PluginParameter]] = None,
        icon: Optional[Icon] = None
    ):
        self.label = label
        self.description = description
        self.documentation = documentation
        self.plugin_id = plugin_id
        self.icon = icon
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
            icon=self.icon
        )
        Plugin.plugins.append(plugin_desc)
        return func

    def retrieve_parameters(self, plugin_class: Type) -> List[PluginParameter]:
        """Retrieves parameters from a plugin class and matches them with the user
        parameter definitions."""

        # Only return parameters for user-defined init methods.
        if not hasattr(plugin_class.__init__, "__code__"):
            return []
        # Collect parameters from init method
        params = []
        sig = inspect.signature(plugin_class.__init__)
        for name in sig.parameters:
            if name != "self":
                param = next((p for p in self.parameters if p.name == name), None)
                if param is None:
                    param = PluginParameter(name)
                sig_param = sig.parameters[name]
                if param.param_type is None:
                    param.param_type = ParameterTypes.get_param_type(sig_param)

                # Make sure that the parameter type is valid
                if not isinstance(param.param_type, ParameterType):
                    raise ValueError(
                        f"Parameter '{sig_param.name}' has an invalid "
                        f"type: '{param.param_type}' is not an instance "
                        "of 'ParameterType'."
                    )

                # Special handling of PluginContext parameter
                if isinstance(param.param_type, PluginContextParameterType):
                    param.visible = False  # Should never be visible in the UI
                    param.default_value = ""  # dummy value

                if param.default_value is None and sig_param.default != _empty:
                    param.default_value = sig_param.default
                params.append(param)
        return params
