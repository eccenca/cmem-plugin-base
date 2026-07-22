"""graph parameter type tests"""

from pathlib import Path

import pytest
from cmem_client.client import Client

from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType
from cmem_plugin_base.testing import TestPluginContext
from tests.utils import needs_cmem


@needs_cmem
def test_graph_parameter_type_completion() -> None:
    """Test graph parameter type completion"""
    parameter = GraphParameterType(show_system_graphs=True)
    context = TestPluginContext()
    assert "https://ns.eccenca.com/data/queries/" in [
        x.value
        for x in parameter.autocomplete(
            query_terms=["Query", "Catalog"],
            depend_on_parameter_values=[],
            context=context,
        )
    ]
    assert (
        len(
            parameter.autocomplete(
                query_terms=["not there asödlkasöld"],
                depend_on_parameter_values=[],
                context=context,
            )
        )
        == 0
    )


@needs_cmem
def test_graph_parameter_type_hides_system_graphs_by_default() -> None:
    """System resource graphs must be hidden unless show_system_graphs=True"""
    parameter = GraphParameterType(show_system_graphs=False)
    context = TestPluginContext()
    values = [
        x.value
        for x in parameter.autocomplete(
            query_terms=["Query", "Catalog"], depend_on_parameter_values=[], context=context
        )
    ]
    assert "https://ns.eccenca.com/data/queries/" not in values


@needs_cmem
def test_graph_parameter_type_shows_unclassified_graphs_only_when_requested(
    tmp_path: Path,
) -> None:
    """Graphs without any assigned class are hidden unless show_graphs_without_class=True"""
    client = Client.from_env()
    graph_iri = "https://example.org/test/unclassified-graph/"
    ttl_file = tmp_path / "graph.ttl"
    ttl_file.write_text(f'<{graph_iri}s> <{graph_iri}p> "value" .\n')
    client.graphs.delete_item(graph_iri, skip_if_missing=True)
    client.graphs.import_item(path=ttl_file, key=graph_iri)
    try:
        assert client.graphs[graph_iri].assigned_classes == []

        hidden = GraphParameterType(show_graphs_without_class=False)
        shown = GraphParameterType(show_graphs_without_class=True)
        context = TestPluginContext()

        hidden_values = [
            x.value
            for x in hidden.autocomplete(
                query_terms=[], depend_on_parameter_values=[], context=context
            )
        ]
        shown_values = [
            x.value
            for x in shown.autocomplete(
                query_terms=[], depend_on_parameter_values=[], context=context
            )
        ]
        assert graph_iri not in hidden_values
        assert graph_iri in shown_values
    finally:
        client.graphs.delete_item(graph_iri, skip_if_missing=True)


def test_graph_parameter_type_accepts_explicit_classes() -> None:
    """Explicit classes override the default class set"""
    parameter = GraphParameterType(classes=["https://example.org/MyClass"])
    assert parameter.classes == {"https://example.org/MyClass"}


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
