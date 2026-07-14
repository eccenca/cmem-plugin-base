"""Tests for TestSystemContext env-var-aware defaults."""

import pytest

from cmem_plugin_base.testing import TestSystemContext


def test_defaults_to_docker_localhost_when_no_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no env vars and no ctor args, falls back to docker.localhost URLs."""
    monkeypatch.delenv("CMEM_BASE_URI", raising=False)
    monkeypatch.delenv("DP_API_ENDPOINT", raising=False)
    monkeypatch.delenv("DI_API_ENDPOINT", raising=False)

    context = TestSystemContext()

    assert context.cmem_base_uri() == "http://docker.localhost"
    assert context.dp_api_endpoint() == "http://docker.localhost/dataplatform"
    assert context.di_api_endpoint() == "http://docker.localhost/dataintegration"


def test_uses_cmem_base_uri_env_var_and_derives_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CMEM_BASE_URI env var is picked up and endpoints are derived from it."""
    monkeypatch.setenv("CMEM_BASE_URI", "https://example.org")
    monkeypatch.delenv("DP_API_ENDPOINT", raising=False)
    monkeypatch.delenv("DI_API_ENDPOINT", raising=False)

    context = TestSystemContext()

    assert context.cmem_base_uri() == "https://example.org"
    assert context.dp_api_endpoint() == "https://example.org/dataplatform"
    assert context.di_api_endpoint() == "https://example.org/dataintegration"


def test_independent_endpoint_env_vars_take_precedence_over_derived(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DP_API_ENDPOINT/DI_API_ENDPOINT env vars override derivation from CMEM_BASE_URI."""
    monkeypatch.setenv("CMEM_BASE_URI", "https://example.org")
    monkeypatch.setenv("DP_API_ENDPOINT", "https://dp.example.org")
    monkeypatch.setenv("DI_API_ENDPOINT", "https://di.example.org")

    context = TestSystemContext()

    assert context.cmem_base_uri() == "https://example.org"
    assert context.dp_api_endpoint() == "https://dp.example.org"
    assert context.di_api_endpoint() == "https://di.example.org"


def test_explicit_constructor_args_take_precedence_over_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit constructor arguments win over any env var."""
    monkeypatch.setenv("CMEM_BASE_URI", "https://example.org")
    monkeypatch.setenv("DP_API_ENDPOINT", "https://dp.example.org")
    monkeypatch.setenv("DI_API_ENDPOINT", "https://di.example.org")

    context = TestSystemContext(
        cmem_base_uri="https://explicit.test",
        dp_api_endpoint="https://explicit.test/dp",
        di_api_endpoint="https://explicit.test/di",
    )

    assert context.cmem_base_uri() == "https://explicit.test"
    assert context.dp_api_endpoint() == "https://explicit.test/dp"
    assert context.di_api_endpoint() == "https://explicit.test/di"
