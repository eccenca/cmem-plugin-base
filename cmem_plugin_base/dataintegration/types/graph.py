"""Knowledge Graph Parameter Type."""
import os
from typing import Optional, Set, List

from cmem.cmempy.dp.proxy.graph import get_graphs_list

from cmem_plugin_base.dataintegration.types import StringParameterType, Autocompletion


class GraphParameterType(StringParameterType):
    """Graphs parameter type"""

    allow_only_autocompleted_values: bool = False

    autocomplete_value_with_labels: bool = True

    classes: Optional[Set[str]] = None

    def __init__(
        self,
        show_di_graphs: bool = False,
        show_system_graphs: bool = False,
        classes: List[str] = None,
        allow_only_autocompleted_values: bool = False,
    ):
        """
        The type of Knowledge Graphs from Dataplatform

        :param show_di_graphs: show DI project graphs
        :param show_system_graphs: show system graphs such as shape and query catalogs
        :param classes: allowed classes of the shown graphs
        :param allow_only_autocompleted_values: allow to enter new graph URLs as well
        """
        self.show_di_graphs = show_di_graphs
        self.show_system_graphs = show_system_graphs
        self.allow_only_autocompleted_values = allow_only_autocompleted_values
        if classes:
            self.classes = set(classes)

    def autocomplete(
        self, query_terms: list[str], project_id: Optional[str] = None
    ) -> list[Autocompletion]:
        os.environ["OAUTH_CLIENT_ID"] = os.environ[
            "DATAINTEGRATION_CMEM_SERVICE_CLIENT"
        ]
        os.environ["OAUTH_CLIENT_SECRET"] = os.environ[
            "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET"
        ]
        graphs = get_graphs_list()
        result = []
        for graph in graphs:
            if self.show_di_graphs is False and graph["diProjectGraph"] is True:
                # filter out DI project graphs
                continue
            if self.show_system_graphs is False and graph["systemResource"] is True:
                # filter out system resource graphs
                continue
            graph_classes = set(graph["assignedClasses"])
            if (
                self.classes is not None
                and len(self.classes.intersection(graph_classes)) == 0
            ):
                # filter out graphs which do not match the requested classes
                continue
            iri = graph["iri"]
            title = graph["label"]["title"]
            label = f"{title} ({iri})"
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=iri, label=label))
                    continue
            if len(query_terms) == 0:
                # add any graph to list if no search terms are given
                result.append(Autocompletion(value=iri, label=label))
        result.sort(key=lambda x: x.label)  # type: ignore
        return result
