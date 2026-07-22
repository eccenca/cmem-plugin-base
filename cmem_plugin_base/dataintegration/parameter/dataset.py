"""DI Dataset Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmem_client


class DatasetParameterType(StringParameterType):
    """Dataset parameter type."""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    dataset_type: str | None = None

    def __init__(self, dataset_type: str | None = None):
        """Dataset parameter type."""
        self.dataset_type = dataset_type

    def label(
        self, value: str, depend_on_parameter_values: list[Any], context: PluginContext
    ) -> str | None:
        """Return the label for the given dataset."""
        client = setup_cmem_client(context.user)
        task = client.datasets.get_task(project_id=context.project_id, task_id=value)
        return f"{task.label}"

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match all provided query terms."""
        client = setup_cmem_client(context.user)
        datasets = [
            dataset
            for dataset in client.datasets.values()
            if dataset.project_id == context.project_id
        ]

        result = []
        for dataset in datasets:
            identifier = dataset.id
            title = dataset.metadata.get("label", identifier)
            label = f"{title} ({identifier})"
            if self.dataset_type is not None and self.dataset_type != dataset.data.type:
                # Ignore datasets of other types
                continue
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=identifier, label=label))  # noqa: PERF401
            if len(query_terms) == 0:
                # add any dataset to list if no search terms are given
                result.append(Autocompletion(value=identifier, label=label))
        result.sort(key=lambda x: x.label)  # type: ignore[return-value, arg-type]
        return list(set(result))
