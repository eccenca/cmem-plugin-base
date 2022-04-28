"""Knowledge Graph Parameter Type."""
from typing import Optional, Set, List

from cmem.cmempy.dp.proxy.graph import get_graphs_list

from cmem_plugin_base.dataintegration.types import StringParameterType, Autocompletion
from cmem_plugin_base.dataintegration.utils import setup_cmempy_super_user_access


class GraphParameterType(StringParameterType):
    """Knowledge Graph parameter type."""

    allow_only_autocompleted_values: bool = False

    autocomplete_value_with_labels: bool = True

    classes: Optional[Set[str]] = None

    def __init__(
        self,
        show_di_graphs: bool = False,
        show_system_graphs: bool = False,
        classes: List[str] = None,
        allow_only_autocompleted_values: bool = True,
    ):
        """
        Knowledge Graph parameter type.

        :param show_di_graphs: show DI project graphs
        :param show_system_graphs: show system graphs such as shape and query catalogs
        :param classes: allowed classes of the shown graphs
            defaults to di:Dataset and void:Dataset
        :param allow_only_autocompleted_values: allow entering new graph URLs
        """
        self.show_di_graphs = show_di_graphs
        self.show_system_graphs = show_system_graphs
        self.allow_only_autocompleted_values = allow_only_autocompleted_values
        if classes:
            self.classes = set(classes)
        else:
            self.classes = {
                "https://vocab.eccenca.com/di/Dataset",
                "http://rdfs.org/ns/void#Dataset"
            }

    def autocomplete(
        self, query_terms: list[str], project_id: Optional[str] = None
    ) -> list[Autocompletion]:
        setup_cmempy_super_user_access()
        graphs = get_graphs_list()
        result = []
        for _ in graphs:
            iri = _["iri"]
            title = _["label"]["title"]
            label = f"{title} ({iri})"
            if self.show_di_graphs is False and _["diProjectGraph"] is True:
                # ignore DI project graphs
                continue
            if self.show_system_graphs is False and _["systemResource"] is True:
                # ignore system resource graphs
                continue
            graph_classes = set(_["assignedClasses"])
            if (
                self.classes is not None
                and len(graph_classes) > 0
                and len(self.classes.intersection(graph_classes)) == 0
            ):
                # ignore graphs which do not match the requested classes
                continue
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=iri, label=label))
                    continue
            if len(query_terms) == 0:
                # add any graph to list if no search terms are given
                result.append(Autocompletion(value=iri, label=label))
        result.sort(key=lambda x: x.label)  # type: ignore
        return list(set(result))
