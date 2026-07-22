"""DI Resource Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmem_client


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
        client = setup_cmem_client(context.user)
        resources = client.files.get_resources(context.project_id)
        result = [
            Autocompletion(
                value=resource.full_path,
                label=resource.name,
            )
            for resource in resources
        ]
        if query_terms:
            result = [_ for _ in result if _.value.find(query_terms[0]) > -1]

        if not result and query_terms:
            result = [
                Autocompletion(value=f"{query_terms[0]}", label=f"{query_terms[0]} (New resource)")
            ]

        return result
