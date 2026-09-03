"""DI Dataset Parameter Type."""

from typing import Any

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType


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
        task_label = (
            get_client(context)
            .datasets.get_task(project_id=context.project_id, task_id=value)
            .label
        )
        return f"{task_label}"

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request - Returns all results that match all provided query terms."""
        datasets = [
            _ for _ in get_client(context).datasets.values() if _.project_id == context.project_id
        ]

        result = []
        for _ in datasets:
            identifier = _.id
            title = _.metadata.get("label", "")
            label = f"{title} ({identifier})"
            if self.dataset_type is not None and self.dataset_type != _.data.type:
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
