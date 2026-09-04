"""graph parameter type tests"""

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem_client.models.graph import Graph
from cmem_client.repositories.protocols.import_item import ImportConflictPolicy

import cmem_plugin_base.dataintegration.parameter.graph as graph_module
from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType
from cmem_plugin_base.testing import TestPluginContext
from tests.utils import get_autocomplete_values, needs_cmem

FIXTURE_DIR = Path(__file__).parent / "fixture"

ALPHA_GRAPH_IRI = (
    "https://ns.eccenca.com/cmem-plugin-base/tests/graph-parameter-type/alpha-sort-test-graph"
)
ZULU_GRAPH_IRI = (
    "https://ns.eccenca.com/cmem-plugin-base/tests/graph-parameter-type/zulu-sort-test-graph"
)


@dataclass
class SortTestGraphs:
    """Two known test graphs used to verify result sorting and ALL-terms matching."""

    alpha_iri: str
    zulu_iri: str


@pytest.fixture(name="sort_test_graphs", scope="module")
def _sort_test_graphs() -> Generator[SortTestGraphs]:
    """Provide two known graphs for sort/match assertions, cleaned up afterwards"""
    client = get_client(TestPluginContext())
    client.graphs.import_item(
        path=FIXTURE_DIR / "alpha_sort_test_graph.ttl",
        key=ALPHA_GRAPH_IRI,
        on_conflict=ImportConflictPolicy.REPLACE,
    )
    client.graphs.import_item(
        path=FIXTURE_DIR / "zulu_sort_test_graph.ttl",
        key=ZULU_GRAPH_IRI,
        on_conflict=ImportConflictPolicy.REPLACE,
    )
    try:
        yield SortTestGraphs(alpha_iri=ALPHA_GRAPH_IRI, zulu_iri=ZULU_GRAPH_IRI)
    finally:
        client.graphs.delete_item(ALPHA_GRAPH_IRI, skip_if_missing=True)
        client.graphs.delete_item(ZULU_GRAPH_IRI, skip_if_missing=True)


@needs_cmem
def test_graph_parameter_type_completion(sort_test_graphs: SortTestGraphs) -> None:
    """Test graph parameter type completion: sorting and ALL-terms matching"""
    parameter = GraphParameterType()
    context = TestPluginContext()

    # both fixture graphs match all three terms, and must come back sorted by label
    values = get_autocomplete_values(
        parameter, ["CmemPluginBase", "SortRegressionTest", "Graph"], context
    )
    assert sort_test_graphs.alpha_iri in values
    assert sort_test_graphs.zulu_iri in values
    assert values.index(sort_test_graphs.alpha_iri) < values.index(sort_test_graphs.zulu_iri)

    # an additional term only present in the "Alpha" label must narrow results to just that graph
    narrowed_values = get_autocomplete_values(
        parameter, ["CmemPluginBase", "SortRegressionTest", "Alpha"], context
    )
    assert sort_test_graphs.alpha_iri in narrowed_values
    assert sort_test_graphs.zulu_iri not in narrowed_values

    assert len(get_autocomplete_values(parameter, ["not there asödlkasöld"], context)) == 0


def _build_graph(
    iri: str, *, di_project_graph: bool = False, system_resource: bool = False
) -> Graph:
    """Build a Graph as cmem-client would parse it from a raw /graphs/list response."""
    return Graph.model_validate(
        {
            "iri": iri,
            "writeable": True,
            "assignedClasses": [],
            "diProjectGraph": di_project_graph,
            "systemResource": system_resource,
            "label": {"title": iri},
        }
    )


class _FakeGraphsRepo:
    """Stand-in for GraphsRepository exposing just what autocomplete() uses."""

    def __init__(self, graphs: list[Graph]) -> None:
        self._graphs = graphs

    def values(self) -> list[Graph]:
        """Return the configured graphs, matching Repository.values()."""
        return self._graphs


class _FakeClient:
    """Stand-in for cmem_client.Client exposing just the .graphs repository."""

    def __init__(self, graphs: list[Graph]) -> None:
        self.graphs = _FakeGraphsRepo(graphs)


def test_graph_parameter_type_filters_di_and_system_graphs(monkeypatch: pytest.MonkeyPatch) -> None:
    """show_di_graphs/show_system_graphs must exclude/include the matching graphs.

    Regression test for the getattr-then-model_extra fallback in
    cmem_plugin_base.dataintegration.parameter.graph._get_untyped_flag: diProjectGraph
    and systemResource aren't typed on cmem-client's Graph model yet, so this exercises
    the fallback path directly without needing a live CMEM instance.
    """
    ordinary = _build_graph("urn:ordinary")
    di_graph = _build_graph("urn:di", di_project_graph=True)
    system_graph = _build_graph("urn:system", system_resource=True)
    fake_client = _FakeClient([ordinary, di_graph, system_graph])
    monkeypatch.setattr(graph_module, "get_client", lambda context: fake_client)  # noqa: ARG005
    context = TestPluginContext()

    default_values = get_autocomplete_values(
        GraphParameterType(show_graphs_without_class=True), [], context
    )
    assert ordinary.iri in default_values
    assert di_graph.iri not in default_values
    assert system_graph.iri not in default_values

    with_di = get_autocomplete_values(
        GraphParameterType(show_di_graphs=True, show_graphs_without_class=True), [], context
    )
    assert di_graph.iri in with_di
    assert system_graph.iri not in with_di

    with_system = get_autocomplete_values(
        GraphParameterType(show_system_graphs=True, show_graphs_without_class=True), [], context
    )
    assert system_graph.iri in with_system
    assert di_graph.iri not in with_system


def test_graph_validation() -> None:
    """Test graph parameter string validation"""
    parameter = GraphParameterType(show_system_graphs=True)

    parameter.name = "urn:ISBN:3-8273-7019-1"
    parameter._validate_graph()  # noqa: SLF001

    parameter.name = "http://test/data"
    parameter._validate_graph()  # noqa: SLF001

    parameter.name = "https://test/data"
    parameter._validate_graph()  # noqa: SLF001

    parameter.name = "test :test"
    with pytest.raises(ValueError, match=f"Could not validate graph IRI '{parameter.name}'"):
        parameter._validate_graph()  # noqa: SLF001

    parameter.name = ":ttt"
    with pytest.raises(ValueError, match=f"Could not validate graph IRI '{parameter.name}'"):
        parameter._validate_graph()  # noqa: SLF001

    parameter.name = ""
    with pytest.raises(ValueError, match=f"Could not validate graph IRI '{parameter.name}'"):
        parameter._validate_graph()  # noqa: SLF001
