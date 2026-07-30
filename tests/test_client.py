"""Tests for the cmem-client access helper."""

import pytest

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.context import PluginContext, UserContext
from cmem_plugin_base.testing import TestSystemContext


class CountingUserContext(UserContext):
    """User context which counts how often its token was requested"""

    def __init__(self, token: str = "not-a-real-token"):  # noqa: S107
        self._token = token
        self.token_calls = 0

    def token(self) -> str:
        """Get the access token"""
        self.token_calls += 1
        return self._token


def build_context(user: UserContext | None) -> PluginContext:
    """Build a plugin context which does not need a CMEM connection"""
    context = PluginContext()
    context.system = TestSystemContext(cmem_base_uri="https://example.org")
    context.user = user
    context.project_id = "TestProject"
    return context


def test_configures_urls_from_system_context() -> None:
    """Client URLs are taken from the SystemContext of the given context."""
    client = get_client(build_context(user=CountingUserContext()))

    assert str(client.config.url_base) == "https://example.org"
    assert str(client.config.url_build_api) == "https://example.org/dataintegration/"
    assert str(client.config.url_explore_api) == "https://example.org/dataplatform/"


def test_authenticates_with_user_context_token() -> None:
    """The client authenticates via the token of the context user."""
    user = CountingUserContext()

    client = get_client(build_context(user=user))

    assert client.auth.provider_object is user
    assert client.auth.method_name == "token"


def test_does_not_request_token_before_first_request() -> None:
    """The token is requested lazily, so a refreshed token is picked up later."""
    user = CountingUserContext()

    get_client(build_context(user=user))

    assert user.token_calls == 0


def test_raises_without_user() -> None:
    """A context without a user cannot be authenticated."""
    context = build_context(user=None)

    with pytest.raises(ValueError, match="no UserContext"):
        get_client(context)
