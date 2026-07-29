"""Access to eccenca Corporate Memory via cmem-client."""

import logging

from cmem_client.client import Client

from cmem_plugin_base.dataintegration.context import ExecutionContext, PluginContext


def get_client(
    context: ExecutionContext | PluginContext,
    logger: logging.Logger | None = None,
) -> Client:
    """Create a cmem-client Client for the user of the given context.

    Connection URLs are taken from the context's SystemContext, authentication uses
    the token of the context's UserContext. The token is requested lazily per request,
    so a token refreshed during a long running execution is picked up automatically.

    The returned client holds a lazily created httpx client and offers no explicit
    close method. Create one client per plugin execution rather than one per entity.

    Args:
        context (ExecutionContext | PluginContext): The context to configure from.
        logger (logging.Logger): Logger to use for the client. Defaults to the
            cmem-client logger.

    Returns:
        A configured cmem-client Client.

    Raises:
        ValueError: in case the context provides no user

    """
    if context.user is None:
        raise ValueError("Context has no UserContext.")
    return Client.from_context(context=context, logger=logger)
