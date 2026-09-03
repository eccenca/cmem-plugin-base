"""DI Resource Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType


class ResourceParameterType(StringParameterType):
    """Resource parameter type."""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match ALL provided query terms."""
        resources = get_client(context).files.get_resources(context.project_id)
        result = [
            Autocompletion(
                value=f"{_.full_path}",
                label=f"{_.name}",
            )
            for _ in resources
        ]
        if query_terms:
            result = [_ for _ in result if _.value.find(query_terms[0]) > -1]

        if not result and query_terms:
            result = [
                Autocompletion(value=f"{query_terms[0]}", label=f"{query_terms[0]} (New resource)")
            ]

        return result
