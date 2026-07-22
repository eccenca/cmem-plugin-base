"""Tests for the cmem-client auth/setup helpers in cmem_plugin_base.dataintegration.utils."""

import os

import pytest
from cmem_client.auth_provider.client_credentials import (
    DEFAULT_OAUTH_CLIENT_ID,
    DEFAULT_OAUTH_CLIENT_SECRET,
)
from cmem_client.client import Client

from cmem_plugin_base.dataintegration.context import UserContext
from cmem_plugin_base.dataintegration.utils import (
    setup_cmem_client,
    setup_cmem_client_super_user_access,
    setup_cmempy_super_user_access,
    setup_cmempy_user_access,
)
from cmem_plugin_base.testing import TestUserContext
from tests.utils import needs_cmem


def test_setup_cmem_client_requires_context() -> None:
    """setup_cmem_client(None) must raise ValueError without making any network call"""
    with pytest.raises(ValueError, match=r"No UserContext given\."):
        setup_cmem_client(None)


def test_setup_cmem_client_requires_token() -> None:
    """A UserContext whose token() returns None must raise ValueError"""
    with pytest.raises(ValueError, match=r"UserContext has no token\."):
        setup_cmem_client(UserContext())


@needs_cmem
def test_setup_cmem_client_builds_working_client() -> None:
    """setup_cmem_client must return a Client authenticated as the given user"""
    user = TestUserContext()
    client = setup_cmem_client(user)
    assert isinstance(client, Client)
    assert os.environ["OAUTH_GRANT_TYPE"] == "prefetched_token"
    assert os.environ["OAUTH_ACCESS_TOKEN"] == user.access_token
    # exercise the client to confirm the auth/config actually work end-to-end
    assert client.projects is not None


@needs_cmem
def test_setup_cmempy_user_access_deprecated_wrapper_still_works() -> None:
    """The deprecated wrapper must keep setting up a working ambient environment"""
    user = TestUserContext()
    result = setup_cmempy_user_access(user)  # type: ignore[func-returns-value]
    assert result is None
    # the ambient env vars it sets must be enough to build a working Client.from_env()
    assert Client.from_env().projects is not None


def test_setup_cmem_client_super_user_access_requires_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing super-user configuration must raise ValueError, not KeyError"""
    for var in (
        "OAUTH_CLIENT_ID",
        "OAUTH_CLIENT_SECRET",
        "DATAINTEGRATION_CMEM_SERVICE_CLIENT",
        "DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET",
    ):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(ValueError, match=r"Super user configuration not available\."):
        setup_cmem_client_super_user_access()


@needs_cmem
def test_setup_cmem_client_super_user_access_builds_working_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """setup_cmem_client_super_user_access must fall back to the DI service account"""
    # Use the real, already-verified-working secret from the ambient test environment.
    # DEFAULT_OAUTH_CLIENT_SECRET is a library placeholder that only matches a fresh,
    # unconfigured local docker CMEM stack, which CI/the shared test instance is not.
    real_client_secret = os.environ.get("OAUTH_CLIENT_SECRET", DEFAULT_OAUTH_CLIENT_SECRET)
    monkeypatch.delenv("OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("OAUTH_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT", DEFAULT_OAUTH_CLIENT_ID)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET", real_client_secret)
    client = setup_cmem_client_super_user_access()
    assert isinstance(client, Client)
    assert client.projects is not None


@needs_cmem
def test_setup_cmempy_super_user_access_deprecated_wrapper_still_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The deprecated super-user wrapper must keep setting up a working ambient environment"""
    real_client_secret = os.environ.get("OAUTH_CLIENT_SECRET", DEFAULT_OAUTH_CLIENT_SECRET)
    monkeypatch.delenv("OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("OAUTH_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT", DEFAULT_OAUTH_CLIENT_ID)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET", real_client_secret)
    result = setup_cmempy_super_user_access()  # type: ignore[func-returns-value]
    assert result is None
    assert Client.from_env().projects is not None


@needs_cmem
def test_setup_cmem_client_falls_back_to_deploy_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """When CMEM_BASE_URI is not set, it must be derived from DEPLOY_BASE_URL"""
    user = TestUserContext()
    # Reuse the real, reachable CMEM_BASE_URI as the DEPLOY_BASE_URL fallback value -
    # "http://docker.localhost" is only reachable inside a docker-compose test rig.
    deploy_base_url = os.environ["CMEM_BASE_URI"]
    monkeypatch.delenv("CMEM_BASE_URI", raising=False)
    monkeypatch.setenv("DEPLOY_BASE_URL", deploy_base_url)
    client = setup_cmem_client(user)
    assert os.environ["CMEM_BASE_URI"] == deploy_base_url
    assert client.projects is not None


@needs_cmem
def test_setup_cmem_client_super_user_access_falls_back_to_deploy_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The super-user path must also derive CMEM_BASE_URI from DEPLOY_BASE_URL when unset"""
    deploy_base_url = os.environ["CMEM_BASE_URI"]
    real_client_secret = os.environ.get("OAUTH_CLIENT_SECRET", DEFAULT_OAUTH_CLIENT_SECRET)
    monkeypatch.delenv("CMEM_BASE_URI", raising=False)
    monkeypatch.setenv("DEPLOY_BASE_URL", deploy_base_url)
    monkeypatch.delenv("OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("OAUTH_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT", DEFAULT_OAUTH_CLIENT_ID)
    monkeypatch.setenv("DATAINTEGRATION_CMEM_SERVICE_CLIENT_SECRET", real_client_secret)
    client = setup_cmem_client_super_user_access()
    assert os.environ["CMEM_BASE_URI"] == deploy_base_url
    assert client.projects is not None
