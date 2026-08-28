"""graph parameter type tests"""

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from cmem_client.repositories.protocols.import_item import ImportConflictPolicy

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
